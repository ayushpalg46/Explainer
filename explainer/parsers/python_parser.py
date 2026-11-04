import ast
import re
import textwrap
from typing import List, Dict, Optional
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import PYTHON_KNOWLEDGE


class PythonParser(BaseParser):
    def __init__(self):
        super().__init__(language="Python")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        dedented = textwrap.dedent(content)
        
        try:
            tree = ast.parse(dedented, filename=file_path)
        except Exception:
            return self._fallback_regex_parse(analysis, content)

        classes = []
        functions = []
        decorators = []
        has_async = False
        detected_frameworks = []
        detected_concepts = []

        for node in ast.walk(tree):
            # Imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis.raw_imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                analysis.raw_imports.append(mod)

            # Classes
            elif isinstance(node, ast.ClassDef):
                bases = [self._get_node_name(b) for b in node.bases]
                classes.append((node.name, node.lineno, bases, ast.get_docstring(node)))

            # Functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_async = isinstance(node, ast.AsyncFunctionDef)
                if is_async:
                    has_async = True
                fn_decorators = [self._get_node_name(d) for d in node.decorator_list]
                decorators.extend(fn_decorators)
                functions.append((node.name, node.lineno, is_async, fn_decorators, ast.get_docstring(node)))

        # Framework detection based on imports and patterns
        all_imports = " ".join(analysis.raw_imports) + " " + content
        if "fastapi" in all_imports:
            detected_frameworks.append("FastAPI")
        if "flask" in all_imports:
            detected_frameworks.append("Flask")
        if "django" in all_imports:
            detected_frameworks.append("Django")
        if "pydantic" in all_imports or "BaseModel" in content:
            detected_frameworks.append("Pydantic Data Validation")
        if "torch" in all_imports or "transformers" in all_imports:
            detected_frameworks.append("PyTorch / Machine Learning")
        if "pytest" in all_imports or "unittest" in all_imports:
            detected_frameworks.append("Pytest Testing Suite")

        if classes:
            detected_concepts.append(f"Object-Oriented Architecture ({len(classes)} classes)")
        if functions:
            detected_concepts.append(f"Functional / Modular Routines ({len(functions)} functions)")
        if decorators:
            detected_concepts.append(f"Metaprogramming Decorators ({len(set(decorators))} distinct)")
        if has_async:
            detected_concepts.append("Asyncio Asynchronous Coroutines")

        # Create ElementExplanations for Classes
        kb_class = PYTHON_KNOWLEDGE.get("class", {})
        for cname, lineno, bases, doc in classes:
            base_str = f" inherits from `{', '.join(bases)}`" if bases else " base class"
            analysis.elements.append(ElementExplanation(
                name=f"class {cname}",
                kind="class",
                line_number=lineno,
                snippet=f"class {cname}({', '.join(bases)}):",
                what_it_is=kb_class.get("what_it_is", "Class definition structuring state and methods."),
                how_it_is_used=f"Defined at line {lineno}{base_str}. {f'Docstring: {doc[:100]}...' if doc else ''}",
                where_it_is_used=f"Class blueprint declared at line {lineno}.",
                why_it_works=kb_class.get("why_it_works", "Instantiates instances with bound methods and instance state."),
                best_practices_and_pitfalls=kb_class.get("best_practices", "Keep class responsibilities cohesive.")
            ))

        # Create ElementExplanations for Functions
        kb_fn = PYTHON_KNOWLEDGE.get("function", {})
        for fname, lineno, is_async, decs, doc in functions:
            prefix = "async def" if is_async else "def"
            dec_str = f" decorated by `@{', '.join(decs)}`" if decs else ""
            analysis.elements.append(ElementExplanation(
                name=f"{prefix} {fname}()",
                kind="function",
                line_number=lineno,
                snippet=f"{prefix} {fname}(...):",
                what_it_is=kb_fn.get("what_it_is", "Callable function encapsulating specific logic."),
                how_it_is_used=f"Defined at line {lineno}{dec_str}. {f'Doc: {doc[:80]}...' if doc else ''}",
                where_it_is_used=f"Function declared at line {lineno}.",
                why_it_works=kb_fn.get("why_it_works", "Executes with a local stack frame and returns evaluated values."),
                best_practices_and_pitfalls=kb_fn.get("best_practices", "Write deterministic, well-typed functions.")
            ))

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks

        # Determine Role
        if any(f in detected_frameworks for f in ["FastAPI", "Flask", "Django"]):
            analysis.role_in_codebase = "Backend API & Web Server Service"
        elif "Pytest Testing Suite" in detected_frameworks or "test_" in file_path.lower():
            analysis.role_in_codebase = "Automated Test Suite"
        elif classes:
            analysis.role_in_codebase = "Domain Model / Object-Oriented Core Service"
        else:
            analysis.role_in_codebase = "Modular Python Logic & Utility Pipeline"

        analysis.summary = (
            f"Python module containing {len(analysis.raw_imports)} imports, {len(classes)} class definition(s), "
            f"and {len(functions)} function(s). "
            f"{'Built with ' + ', '.join(detected_frameworks) + '. ' if detected_frameworks else ''}"
            f"{'Features asynchronous coroutines. ' if has_async else ''}"
        )

        return analysis

    def _get_node_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_node_name(node.func)
        return "unknown"

    def _fallback_regex_parse(self, analysis: FileAnalysis, content: str) -> FileAnalysis:
        analysis.summary = "Python file analyzed via regex fallback."
        analysis.role_in_codebase = "Python Source File"
        for m in re.finditer(r'^(?:from\s+([a-zA-Z0-9_.]+)\s+import|import\s+([a-zA-Z0-9_.,\s]+))', content, re.MULTILINE):
            imp = m.group(1) or m.group(2)
            if imp:
                for item in imp.split(','):
                    analysis.raw_imports.append(item.strip().split()[0])
        return analysis
