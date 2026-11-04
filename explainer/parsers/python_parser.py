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
        
        # Clean content and attempt AST parse
        cleaned_content = textwrap.dedent(content.replace("\r\n", "\n"))
        try:
            tree = ast.parse(cleaned_content, filename=file_path)
            return self._parse_ast(analysis, tree, cleaned_content, relative_path)
        except Exception:
            return self._fallback_regex_parse(analysis, cleaned_content, relative_path)

    def _parse_ast(self, analysis: FileAnalysis, tree: ast.AST, content: str, relative_path: str) -> FileAnalysis:
        classes = []
        functions = []
        decorators = []
        imports_found = []
        has_async = False
        has_main_guard = False
        detected_frameworks = []
        detected_concepts = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    analysis.raw_imports.append(alias.name)
                    imports_found.append((alias.name, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                names = [a.name for a in node.names]
                analysis.raw_imports.append(mod)
                imports_found.append((f"{mod} ({', '.join(names)})", node.lineno))

            elif isinstance(node, ast.ClassDef):
                bases = [self._get_node_name(b) for b in node.bases]
                classes.append((node.name, node.lineno, bases, ast.get_docstring(node)))

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                is_async = isinstance(node, ast.AsyncFunctionDef)
                if is_async:
                    has_async = True
                fn_decorators = [self._get_node_name(d) for d in node.decorator_list]
                decorators.extend(fn_decorators)
                # Extract args
                arg_names = [a.arg for a in node.args.args]
                functions.append((node.name, node.lineno, is_async, fn_decorators, ast.get_docstring(node), arg_names))

            elif isinstance(node, ast.If):
                # Check for if __name__ == '__main__':
                if (isinstance(node.test, ast.Compare) and 
                    isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"):
                    has_main_guard = True

        # Framework detection
        all_imports = " ".join(analysis.raw_imports) + " " + content
        if "fastapi" in all_imports:
            detected_frameworks.append("FastAPI Web Server")
        if "flask" in all_imports:
            detected_frameworks.append("Flask Web Server")
        if "django" in all_imports:
            detected_frameworks.append("Django Web Framework")
        if "pydantic" in all_imports or "BaseModel" in content:
            detected_frameworks.append("Pydantic Data Validation")
        if "torch" in all_imports or "transformers" in all_imports:
            detected_frameworks.append("PyTorch Machine Learning")
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
        if has_main_guard:
            detected_concepts.append("Direct Executable Script Entrypoint (`__main__`)")

        # Explain Imports
        for imp_name, lineno in imports_found:
            analysis.elements.append(ElementExplanation(
                name=f"import {imp_name}",
                kind="import",
                line_number=lineno,
                snippet=f"import {imp_name}",
                what_it_is=f"Brings tools and helpers from the module `{imp_name}` into this script.",
                how_it_is_used=f"Written at line {lineno} to provide external functions or data.",
                where_it_is_used=f"Line {lineno} of `{relative_path}`.",
                why_it_works="Python's import system loads the specified module into `sys.modules` and binds its name locally.",
                best_practices_and_pitfalls="Import standard libraries first, then third-party libraries, then local files.",
                simple_analogy=f"Think of this like borrowing a special tool `{imp_name}` from a friend's toolbox so you can use it here!",
                what_happens_on_screen="Allows the rest of the file to use functions and classes from that module.",
                what_if_removed=f"The program crashes with an error: 'NameError: name is not defined' when trying to call `{imp_name}`."
            ))

        # Explain Classes
        for cname, lineno, bases, doc in classes:
            base_str = f" inherits from `{', '.join(bases)}`" if bases else " base class"
            analysis.elements.append(ElementExplanation(
                name=f"class {cname}",
                kind="class",
                line_number=lineno,
                snippet=f"class {cname}({', '.join(bases)}):",
                what_it_is=f"A blueprint creating `{cname}` objects that bundle data and actions together.",
                how_it_is_used=f"Declared at line {lineno}{base_str}. {f'Docstring: {doc[:100]}...' if doc else ''}",
                where_it_is_used=f"Class declared at line {lineno} of `{relative_path}`.",
                why_it_works="Instantiating invokes `__new__` to allocate memory and `__init__` to configure attributes.",
                best_practices_and_pitfalls="Keep each class focused on one single responsibility.",
                simple_analogy=f"Think of `class {cname}` like a cookie cutter! The class is the cookie cutter blueprint, and every object you make with it is a real cookie with its own sprinkles!",
                what_happens_on_screen="Organizes complicated information into neat, reusable objects.",
                what_if_removed=f"The program won't know how to create `{cname}` objects and will crash."
            ))

        # Explain Functions
        for fname, lineno, is_async, decs, doc, args in functions:
            prefix = "async def" if is_async else "def"
            dec_str = f" decorated by `@{', '.join(decs)}`" if decs else ""
            arg_str = ", ".join(args)
            analysis.elements.append(ElementExplanation(
                name=f"{prefix} {fname}({arg_str})",
                kind="function",
                line_number=lineno,
                snippet=f"{prefix} {fname}({arg_str}):",
                what_it_is=f"A named recipe of instructions that takes inputs `({arg_str})` and calculates an output.",
                how_it_is_used=f"Defined at line {lineno}{dec_str}. {f'Doc: {doc[:80]}...' if doc else ''}",
                where_it_is_used=f"Function declared at line {lineno} of `{relative_path}`.",
                why_it_works="Python creates a function object in memory that executes within its own local stack frame when called.",
                best_practices_and_pitfalls="Give functions descriptive action names and keep them short and easy to test.",
                simple_analogy=f"Think of `{fname}` like teaching a robot helper a brand new recipe! Whenever you call `{fname}`, the robot follows these exact steps and gives you back the result!",
                what_happens_on_screen="Executes calculations, transforms data, or triggers actions behind the scenes.",
                what_if_removed=f"Any code that calls `{fname}` will crash with an error saying the function does not exist."
            ))

        # Explain Main Guard
        if has_main_guard:
            analysis.elements.append(ElementExplanation(
                name="if __name__ == '__main__':",
                kind="concept",
                line_number=None,
                snippet="if __name__ == '__main__': ...",
                what_it_is="The standard Python execution guard ensuring code only runs when executed directly.",
                how_it_is_used="Wraps the entrypoint script execution at the bottom of the file.",
                where_it_is_used=f"Bottom of `{relative_path}`.",
                why_it_works="Python assigns `__name__ = '__main__'` only when the script is directly run from terminal.",
                best_practices_and_pitfalls="Always wrap script execution in a `main()` function under this guard.",
                simple_analogy="Think of this like a sign on a toy racecar: 'Only start the engine if someone presses the main START button, not when it is sitting inside the toy box!'",
                what_happens_on_screen="Starts the script when run from the command line, but stays quiet if another file imports it.",
                what_if_removed="If another file imports this file, the whole program would accidentally run prematurely!"
            ))

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks

        if any(f in detected_frameworks for f in ["FastAPI", "Flask", "Django"]):
            analysis.role_in_codebase = "Backend API & Web Server Service"
        elif "Pytest Testing Suite" in detected_frameworks or "test_" in file_path.lower():
            analysis.role_in_codebase = "Automated Test Suite"
        elif classes:
            analysis.role_in_codebase = "Domain Model / Object-Oriented Core Service"
        else:
            analysis.role_in_codebase = "Modular Python Logic & Utility Pipeline"

        analysis.beginner_story = (
            f"Imagine this file `{relative_path}` is a recipe book for a smart kitchen robot! "
            f"It defines {len(functions)} recipe(s) (`def`) and {len(classes)} cookie-cutter blueprint(s) (`class`). "
            f"When other files or users need to do calculations or process data, they ask this file to run its recipes "
            f"and deliver the fresh results!"
        )

        analysis.summary = (
            f"Python module containing {len(analysis.raw_imports)} imports, {len(classes)} class definition(s), "
            f"and {len(functions)} function(s). "
            f"{'Built with ' + ', '.join(detected_frameworks) + '. ' if detected_frameworks else ''}"
            f"{'Features asynchronous coroutines. ' if has_async else ''}"
        )

        return analysis

    def _fallback_regex_parse(self, analysis: FileAnalysis, content: str, relative_path: str) -> FileAnalysis:
        analysis.summary = "Python module analyzed via pattern recognition."
        analysis.role_in_codebase = "Python Source File"

        # Regex for functions
        for m in re.finditer(r'^\s*(async\s+def|def)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\):', content, re.MULTILINE):
            prefix = m.group(1)
            fname = m.group(2)
            args = m.group(3)
            line_no = content[:m.start()].count('\n') + 1
            analysis.elements.append(ElementExplanation(
                name=f"{prefix} {fname}({args})",
                kind="function",
                line_number=line_no,
                snippet=m.group(0),
                what_it_is=f"A Python function `{fname}` that performs calculations or actions.",
                how_it_is_used=f"Defined at line {line_no} with parameters `({args})`.",
                where_it_is_used=f"Line {line_no} of `{relative_path}`.",
                why_it_works="Executes instructions and returns evaluated values.",
                simple_analogy=f"Think of `{fname}` like a helpful robot recipe that runs whenever you call its name!",
                what_happens_on_screen="Executes logic behind the scenes and returns answers.",
                what_if_removed="The program cannot run this calculation and will crash with an error."
            ))

        # Regex for classes
        for m in re.finditer(r'^\s*class\s+([a-zA-Z0-9_]+)(?:\(([^)]*)\))?:', content, re.MULTILINE):
            cname = m.group(1)
            bases = m.group(2) or ""
            line_no = content[:m.start()].count('\n') + 1
            analysis.elements.append(ElementExplanation(
                name=f"class {cname}",
                kind="class",
                line_number=line_no,
                snippet=m.group(0),
                what_it_is=f"A Python class `{cname}` structuring data and behaviors.",
                how_it_is_used=f"Blueprint defined at line {line_no}.",
                where_it_is_used=f"Line {line_no} of `{relative_path}`.",
                why_it_works="Instantiates object instances with state and methods.",
                simple_analogy=f"Think of `class {cname}` like a cookie cutter blueprint making custom objects!",
                what_happens_on_screen="Organizes application data cleanly.",
                what_if_removed=f"The program won't know how to create `{cname}` objects."
            ))

        # Regex for imports
        for m in re.finditer(r'^(?:from\s+([a-zA-Z0-9_.]+)\s+import\s+([a-zA-Z0-9_.,\s*]+)|import\s+([a-zA-Z0-9_.,\s]+))', content, re.MULTILINE):
            imp = m.group(1) or m.group(3)
            line_no = content[:m.start()].count('\n') + 1
            analysis.elements.append(ElementExplanation(
                name=f"import {imp.strip()}",
                kind="import",
                line_number=line_no,
                snippet=m.group(0),
                what_it_is=f"Imports external module `{imp.strip()}`.",
                how_it_is_used=f"Line {line_no}.",
                where_it_is_used=f"Line {line_no} of `{relative_path}`.",
                why_it_works="Loads external module into Python scope.",
                simple_analogy="Think of this like borrowing a tool from another room!",
                what_happens_on_screen="Enables external functions to be used here.",
                what_if_removed="Code calling these functions will crash with an error."
            ))

        analysis.beginner_story = (
            f"Imagine this file `{relative_path}` is a recipe book for a smart kitchen robot! "
            f"It provides instructions telling the computer how to calculate numbers and prepare data."
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
