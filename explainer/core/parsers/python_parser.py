"""
Python AST & Semantic Framework Parser for Explainer.
Uses Python's standard `ast` module to analyze classes, functions, decorators, imports, async routines, and frameworks.
"""
import ast
import re
from typing import List, Dict, Any
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class PythonASTVisitor(ast.NodeVisitor):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.symbols: List[FileSymbol] = []
        self.imports: List[FileImport] = []
        self.exports: List[FileExport] = []
        self.connections: List[FileConnection] = []
        self.tech_stack: List[str] = ["Python 3"]
        self.concepts: List[str] = []
        self.classes: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.routes: List[Dict[str, str]] = []
        self.is_async: bool = False
        self.has_pydantic: bool = False
        self.has_dataclass: bool = False

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(FileImport(
                source=alias.asname or alias.name,
                target=alias.name,
                line=node.lineno,
                import_type="standard_import"
            ))
            self._check_package(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        level = node.level  # > 0 means relative import
        prefix = "." * level
        full_target = f"{prefix}{mod}"

        for alias in node.names:
            self.imports.append(FileImport(
                source=alias.asname or alias.name,
                target=full_target,
                line=node.lineno,
                import_type="relative" if level > 0 else "from_import"
            ))
            if level > 0:
                self.connections.append(FileConnection(
                    source_file=self.filepath,
                    target_file=full_target,
                    relation_type="imports_python_module",
                    mechanism=f"Relative Import: from {full_target} import {alias.name}",
                    rationale="Composes internal package functionality, models, utilities, or services."
                ))
            else:
                self._check_package(mod)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        bases = [ast.unparse(b) for b in node.bases]
        decorators = [ast.unparse(d) for d in node.decorator_list]
        doc = ast.get_docstring(node) or ""

        is_pydantic = any("BaseModel" in b for b in bases)
        is_dataclass = any("dataclass" in d for d in decorators)

        if is_pydantic:
            self.has_pydantic = True
        if is_dataclass:
            self.has_dataclass = True

        class_methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                class_methods.append(item.name)

        sig = f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
        desc = doc.strip() if doc else f"Class defining {node.name} data structure and behavior with {len(class_methods)} methods."

        self.symbols.append(FileSymbol(
            name=node.name,
            kind="class",
            line=node.lineno,
            signature=sig,
            description=desc,
            attributes={"bases": bases, "decorators": decorators, "methods": class_methods}
        ))
        self.classes.append({"name": node.name, "line": node.lineno, "bases": bases, "methods": class_methods})
        self.exports.append(FileExport(name=node.name, kind="class", line=node.lineno))

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._record_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.is_async = True
        self._record_function(node, is_async=True)
        self.generic_visit(node)

    def _record_function(self, node, is_async: bool):
        decorators = [ast.unparse(d) for d in node.decorator_list]
        doc = ast.get_docstring(node) or ""
        args = [a.arg for a in node.args.args]
        ret = ast.unparse(node.returns) if node.returns else "None"
        sig = f"{'async ' if is_async else ''}def {node.name}({', '.join(args)}) -> {ret}"

        # Detect HTTP API Endpoints in FastAPI/Flask
        for dec in decorators:
            if any(dec.startswith(p) for p in ("app.get", "app.post", "app.put", "app.delete", "router.get", "router.post")):
                route_match = re.search(r"\(['\"]([^'\"]+)['\"]", dec)
                route_path = route_match.group(1) if route_match else "unknown"
                self.routes.append({"method": dec.split("(")[0], "path": route_path, "func": node.name})

        desc = doc.strip() if doc else f"{'Asynchronous coroutine' if is_async else 'Function'} implementing {node.name} logic."

        # If it's top-level or not a dunder method
        if not node.name.startswith("__"):
            self.symbols.append(FileSymbol(
                name=node.name,
                kind="async_function" if is_async else "function",
                line=node.lineno,
                signature=sig,
                description=desc,
                attributes={"decorators": decorators, "args": args, "returns": ret}
            ))
            self.functions.append({"name": node.name, "line": node.lineno, "is_async": is_async})
            self.exports.append(FileExport(name=node.name, kind="function", line=node.lineno))

    def _check_package(self, pkg: str):
        top_pkg = pkg.split(".")[0].lower()
        mapping = {
            "fastapi": "FastAPI Framework",
            "flask": "Flask Framework",
            "django": "Django Framework",
            "sqlalchemy": "SQLAlchemy ORM",
            "pydantic": "Pydantic Data Validation",
            "pytest": "Pytest Test Suite",
            "numpy": "NumPy Numerical Engine",
            "pandas": "Pandas DataFrames",
            "requests": "Requests HTTP Client",
            "httpx": "HTTPX Async Client",
            "torch": "PyTorch Machine Learning",
            "rich": "Rich Terminal UI",
            "click": "Click CLI Interface",
            "celery": "Celery Distributed Task Queue",
            "redis": "Redis In-Memory Store",
            "asyncio": "AsyncIO Asynchronous Concurrency"
        }
        if top_pkg in mapping:
            self.tech_stack.append(mapping[top_pkg])


class PythonFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".py", ".pyw"]

    @property
    def language_name(self) -> str:
        return "Python"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        visitor = PythonASTVisitor(filepath)
        security_and_practices: List[str] = []

        try:
            tree = ast.parse(content, filename=filepath)
            visitor.visit(tree)
        except SyntaxError as e:
            # Fallback regex extraction if file has python syntax errors
            security_and_practices.append(f"Syntax error during AST parsing at line {e.lineno}: {e.msg}")

        concepts = visitor.concepts
        if visitor.is_async:
            concepts.append("Asynchronous Event Loop & Non-Blocking Coroutines (async/await)")
        if visitor.has_pydantic:
            concepts.append("Pydantic Schema Validation & Serialization")
        if visitor.has_dataclass:
            concepts.append("Python Standard Dataclass Models")
        if visitor.classes:
            concepts.append(f"Object-Oriented Design ({len(visitor.classes)} class(es) declared)")
        if visitor.routes:
            concepts.append(f"RESTful API Service Controller ({len(visitor.routes)} endpoint(s) mapped)")

        components_breakdown = [
            {
                "section": "Modules & External Dependencies",
                "details": f"Imports {len(visitor.imports)} libraries and modules. Detected ecosystems: {', '.join(set(visitor.tech_stack))}."
            },
            {
                "section": "Class Hierarchy & Data Structures",
                "details": f"Defines {len(visitor.classes)} class(es): {', '.join(c['name'] for c in visitor.classes) if visitor.classes else 'None (functional module)'}."
            },
            {
                "section": "Functions & Executable Routines",
                "details": f"Implements {len(visitor.functions)} callable routines ({len([f for f in visitor.functions if f['is_async']])} async coroutines)."
            }
        ]
        if visitor.routes:
            components_breakdown.append({
                "section": "HTTP API Routes",
                "details": "; ".join(f"[{r['method']}] {r['path']} -> {r['func']}()" for r in visitor.routes)
            })

        # Security check
        if "subprocess" in content and "shell=True" in content:
            security_and_practices.append("Warning: `shell=True` detected in subprocess execution. Avoid shell injection by passing argument lists.")
        if "os.environ" in content and "PASSWORD" in content.upper():
            security_and_practices.append("Loads credentials or secrets from environment. Ensure secret values are not logged.")

        # Summary & Architectural Role
        summary = f"Python module ({filename}) with {loc} lines of code. "
        if visitor.routes:
            summary += f"Acts as an API web service controller defining {len(visitor.routes)} routes."
            arch_role = "Backend Controller / Web API Endpoint"
        elif visitor.has_pydantic or any("Model" in c["name"] for c in visitor.classes):
            summary += f"Defines domain data models, schemas, and serialization contracts."
            arch_role = "Domain Data Model / Entity Schema"
        elif "test_" in filename or "_test.py" in filename:
            summary += f"Defines automated test suite and verification assertions."
            arch_role = "Test Suite / Quality Assurance"
        elif visitor.classes:
            summary += f"Implements object-oriented business domain services."
            arch_role = "Business Service / Core Domain Logic"
        else:
            summary += f"Provides functional utilities, algorithms, or script automation."
            arch_role = "Utility / Automation Module"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".py",
            language="Python",
            lines_of_code=loc,
            size_bytes=size_bytes,
            summary=summary,
            architecture_role=arch_role,
            tech_stack=list(set(visitor.tech_stack)),
            symbols=visitor.symbols,
            imports=visitor.imports,
            exports=visitor.exports,
            concepts=concepts,
            components_breakdown=components_breakdown,
            outgoing_connections=visitor.connections,
            security_and_best_practices=security_and_practices,
            tags=["python", "backend", "script" if not visitor.classes else "oop"]
        )
