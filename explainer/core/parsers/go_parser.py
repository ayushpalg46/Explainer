"""
Go Struct, Interface, Goroutine, and HTTP Handler Parser for Explainer.
Analyzes package, imports, structs, interfaces, methods, goroutines, channels, and Go web frameworks.
"""
import re
from typing import List, Dict, Any
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class GoFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".go"]

    @property
    def language_name(self) -> str:
        return "Go"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["Go (Golang)"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        # 1. Package declaration
        pkg_match = re.search(r"package\s+([a-zA-Z0-9_]+)", content)
        package_name = pkg_match.group(1) if pkg_match else "main"
        concepts.append(f"Go Package Boundary: `{package_name}`")

        # 2. Imports (single and grouped)
        grouped_import_match = re.search(r"import\s*\(([^)]+)\)", content)
        if grouped_import_match:
            for imp_line in grouped_import_match.group(1).splitlines():
                imp_line = imp_line.strip()
                if not imp_line or imp_line.startswith("//"):
                    continue
                path_match = re.search(r"['\"]([^'\"]+)['\"]", imp_line)
                if path_match:
                    target = path_match.group(1)
                    imports.append(FileImport(
                        source=target.split("/")[-1],
                        target=target,
                        line=1,
                        import_type="go_import"
                    ))
                    self._classify_import(target, tech_stack)

        single_imports = re.finditer(r"import\s+['\"]([^'\"]+)['\"]", content)
        for m in single_imports:
            target = m.group(1)
            imports.append(FileImport(
                source=target.split("/")[-1],
                target=target,
                line=content[:m.start()].count("\n") + 1,
                import_type="go_import"
            ))
            self._classify_import(target, tech_stack)

        # 3. Structs
        struct_matches = re.finditer(r"type\s+([a-zA-Z0-9_]+)\s+struct\b", content)
        struct_names = []
        for m in struct_matches:
            s_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            struct_names.append(s_name)
            is_exported = s_name[0].isupper()
            symbols.append(FileSymbol(
                name=s_name,
                kind="go_struct",
                line=line_num,
                signature=f"type {s_name} struct",
                description=f"{'Exported' if is_exported else 'Internal'} Go data struct definition."
            ))
            if is_exported:
                exports.append(FileExport(name=s_name, kind="struct", line=line_num))

        if struct_names:
            concepts.append(f"Data Struct Modeling ({len(struct_names)} struct(s): {', '.join(struct_names)})")

        # 4. Interfaces
        interface_matches = re.finditer(r"type\s+([a-zA-Z0-9_]+)\s+interface\b", content)
        interface_names = []
        for m in interface_matches:
            i_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            interface_names.append(i_name)
            symbols.append(FileSymbol(
                name=i_name,
                kind="go_interface",
                line=line_num,
                signature=f"type {i_name} interface",
                description=f"Implicit interface contract defining polymorphic behavior."
            ))
            if i_name[0].isupper():
                exports.append(FileExport(name=i_name, kind="interface", line=line_num))

        if interface_names:
            concepts.append(f"Implicit Go Interface Contracts ({', '.join(interface_names)})")

        # 5. Functions and Receiver Methods
        func_matches = re.finditer(r"func\s+(?:\(([^)]+)\)\s+)?([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*(?:[^{]+)?\{", content)
        func_count = 0
        method_count = 0
        for m in func_matches:
            receiver = m.group(1)
            f_name = m.group(2)
            f_args = m.group(3)
            line_num = content[:m.start()].count("\n") + 1

            if receiver:
                method_count += 1
                kind = "go_method"
                sig = f"func ({receiver}) {f_name}({f_args})"
                desc = f"Receiver method bound to `{receiver}`."
            else:
                func_count += 1
                kind = "go_function"
                sig = f"func {f_name}({f_args})"
                desc = f"Package function executing {f_name}."

            symbols.append(FileSymbol(
                name=f_name,
                kind=kind,
                line=line_num,
                signature=sig,
                description=desc
            ))
            if f_name[0].isupper():
                exports.append(FileExport(name=f_name, kind="function" if not receiver else "method", line=line_num))

        # 6. Concurrency: Goroutines & Channels
        goroutines = len(re.findall(r"\bgo\s+(?:func|[a-zA-Z0-9_]+)\b", content))
        has_channels = "chan " in content or "make(chan" in content or "<-" in content
        if goroutines > 0:
            concepts.append(f"CSP Concurrency: {goroutines} Goroutine Spawn(s)")
        if has_channels:
            concepts.append("Channel Communication Pipelines (CSP)")

        # 7. Web frameworks & routes
        if "gin." in content or "*gin.Context" in content:
            tech_stack.append("Gin Web Framework")
        if "fiber." in content:
            tech_stack.append("Fiber Web Framework")
        if "http.HandleFunc" in content or "http.ListenAndServe" in content:
            tech_stack.append("Go Standard net/http Engine")

        # Components breakdown
        components_breakdown.append({
            "section": "Package & Imported Crates/Packages",
            "details": f"Belongs to package `{package_name}`. Imports {len(imports)} packages: {', '.join(set(tech_stack))}."
        })
        components_breakdown.append({
            "section": "Types & Interfaces",
            "details": f"Defines {len(struct_names)} structs and {len(interface_names)} interfaces."
        })
        components_breakdown.append({
            "section": "Functions & Receiver Methods",
            "details": f"Implements {func_count} package functions and {method_count} struct receiver methods."
        })

        summary = f"Go source file ({filename}) in package '{package_name}' containing {loc} lines, {len(struct_names)} structs, and {func_count + method_count} functions/methods."
        if package_name == "main":
            arch_role = "Executable Application Entrypoint / Command"
        elif "service" in package_name.lower():
            arch_role = "Business Service Layer"
        elif "handler" in package_name.lower() or "controller" in package_name.lower():
            arch_role = "HTTP Request Handler / Controller"
        elif "model" in package_name.lower():
            arch_role = "Data Model / Schema Definition"
        else:
            arch_role = "Package Library Module"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".go",
            language="Go",
            lines_of_code=loc,
            size_bytes=size_bytes,
            summary=summary,
            architecture_role=arch_role,
            tech_stack=list(set(tech_stack)),
            symbols=symbols,
            imports=imports,
            exports=exports,
            concepts=concepts,
            components_breakdown=components_breakdown,
            outgoing_connections=connections,
            security_and_best_practices=security_and_practices,
            tags=["go", "golang", "backend", "concurrency"]
        )

    def _classify_import(self, target: str, stack: List[str]):
        if "github.com/gin-gonic/gin" in target:
            stack.append("Gin Web Framework")
        elif "github.com/gofiber/fiber" in target:
            stack.append("Fiber Web Framework")
        elif "gorm.io/gorm" in target:
            stack.append("GORM ORM Engine")
        elif "net/http" in target:
            stack.append("net/http Standard Library")
        elif "database/sql" in target:
            stack.append("database/sql Engine")
