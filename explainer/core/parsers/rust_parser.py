"""
Rust Module, Struct, and Trait Parser for Explainer.
Analyzes Rust modules, use statements, structs, enums, traits, impl blocks, async functions, and memory patterns.
"""
import re
from typing import List, Dict, Any
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class RustFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".rs"]

    @property
    def language_name(self) -> str:
        return "Rust"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["Rust"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        # 1. Parse use statements
        use_pattern = re.finditer(r"(?:pub\s+)?use\s+([^;]+);", content)
        for m in use_pattern:
            import_path = m.group(1).strip()
            line_num = content[:m.start()].count("\n") + 1
            imports.append(FileImport(
                source=import_path.split("::")[-1],
                target=import_path,
                line=line_num,
                import_type="rust_use"
            ))

            # Interconnection if referencing crate or local module
            if import_path.startswith(("crate::", "super::", "self::")):
                connections.append(FileConnection(
                    source_file=filepath,
                    target_file=import_path,
                    relation_type="imports_rust_module",
                    mechanism=f"use {import_path};",
                    rationale="Imports structs, traits, or functions from project crate module tree."
                ))
            else:
                self._classify_crate(import_path, tech_stack)

        # 2. Parse mod declarations
        mod_pattern = re.finditer(r"(?:pub\s+)?mod\s+([a-zA-Z0-9_]+);", content)
        for m in mod_pattern:
            mod_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            connections.append(FileConnection(
                source_file=filepath,
                target_file=f"{mod_name}.rs",
                relation_type="declares_submodule",
                mechanism=f"mod {mod_name};",
                rationale="Mounts sibling module or subdirectory module file into crate compilation graph."
            ))

        # 3. Parse Structs
        struct_matches = re.finditer(r"(?:pub(?:\([^)]+\))?\s+)?struct\s+([A-Z][a-zA-Z0-9_]*)", content)
        struct_names = []
        for m in struct_matches:
            s_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            struct_names.append(s_name)
            symbols.append(FileSymbol(
                name=s_name,
                kind="rust_struct",
                line=line_num,
                signature=f"struct {s_name}",
                description=f"Rust data structure defining typed fields and memory layout for {s_name}."
            ))
            exports.append(FileExport(name=s_name, kind="struct", line=line_num))

        if struct_names:
            concepts.append(f"Struct Data Modeling ({len(struct_names)} struct(s): {', '.join(struct_names)})")

        # 4. Parse Enums
        enum_matches = re.finditer(r"(?:pub(?:\([^)]+\))?\s+)?enum\s+([A-Z][a-zA-Z0-9_]*)", content)
        enum_names = []
        for m in enum_matches:
            e_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            enum_names.append(e_name)
            symbols.append(FileSymbol(
                name=e_name,
                kind="rust_enum",
                line=line_num,
                signature=f"enum {e_name}",
                description=f"Algebraic Data Type (ADT) defining polymorphic variants for {e_name}."
            ))
        if enum_names:
            concepts.append(f"Algebraic Sum Types / Enums ({', '.join(enum_names)})")

        # 5. Parse Traits
        trait_matches = re.finditer(r"(?:pub(?:\([^)]+\))?\s+)?trait\s+([A-Z][a-zA-Z0-9_]*)", content)
        trait_names = []
        for m in trait_matches:
            t_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            trait_names.append(t_name)
            symbols.append(FileSymbol(
                name=t_name,
                kind="rust_trait",
                line=line_num,
                signature=f"trait {t_name}",
                description=f"Shared behavior contract / trait specification for {t_name}."
            ))
        if trait_names:
            concepts.append(f"Trait Behavior Abstractions ({', '.join(trait_names)})")

        # 6. Parse Functions & Async
        fn_matches = re.finditer(r"(?:pub(?:\([^)]+\))?\s+)?(async\s+)?fn\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)(?:\s*->\s*([^{]+))?", content)
        fn_count = 0
        async_count = 0
        for m in fn_matches:
            is_async = bool(m.group(1))
            f_name = m.group(2)
            f_args = m.group(3)
            f_ret = (m.group(4) or "()").strip()
            line_num = content[:m.start()].count("\n") + 1
            fn_count += 1
            if is_async:
                async_count += 1

            symbols.append(FileSymbol(
                name=f_name,
                kind="async_function" if is_async else "function",
                line=line_num,
                signature=f"{'async ' if is_async else ''}fn {f_name}({f_args}) -> {f_ret}",
                description=f"{'Asynchronous non-blocking routine' if is_async else 'Routine'} executing {f_name}."
            ))
            exports.append(FileExport(name=f_name, kind="function", line=line_num))

        if async_count > 0:
            concepts.append(f"Asynchronous Rust Concurrency ({async_count} async function(s))")

        # 7. Memory & Safety Patterns
        if "unsafe" in content:
            concepts.append("Unsafe Memory Blocks (Direct Pointer/FFI Operations)")
            security_and_practices.append("Caution: Contains `unsafe` block. Verify invariants and bounds checking manually.")
        if "Arc<" in content or "Mutex<" in content:
            concepts.append("Thread-Safe Shared Memory Concurrency (Arc / Mutex)")
        if "tokio" in content:
            tech_stack.append("Tokio Async Runtime")

        # Components breakdown
        components_breakdown.append({
            "section": "Modules & Crates Imported",
            "details": f"Imports {len(imports)} items. Ecosystem crates detected: {', '.join(set(tech_stack))}."
        })
        components_breakdown.append({
            "section": "Data Types & Type System",
            "details": f"Implements {len(struct_names)} structs, {len(enum_names)} enums, and {len(trait_names)} traits."
        })
        components_breakdown.append({
            "section": "Function Implementations",
            "details": f"Declares {fn_count} functions ({async_count} async tasks)."
        })

        summary = f"Rust source file ({filename}) with {loc} lines, defining {len(struct_names)} structs and {fn_count} functions."
        arch_role = "Systems Core / High-Performance Service Logic" if filename != "main.rs" else "Binary Application Entrypoint"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".rs",
            language="Rust",
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
            tags=["rust", "systems", "memory-safe", "concurrency"]
        )

    def _classify_crate(self, path: str, stack: List[str]):
        top = path.split("::")[0].lower()
        mapping = {
            "tokio": "Tokio Async Runtime",
            "serde": "Serde Serialization Engine",
            "axum": "Axum Web Framework",
            "actix_web": "Actix Web Framework",
            "tracing": "Tracing Diagnostics",
            "anyhow": "Anyhow Error Handling",
            "clap": "Clap CLI Parser",
            "sqlx": "SQLx Async Database Driver"
        }
        if top in mapping:
            stack.append(mapping[top])
