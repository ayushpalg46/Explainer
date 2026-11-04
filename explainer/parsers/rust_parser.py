import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class RustParser(BaseParser):
    def __init__(self):
        super().__init__(language="Rust")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)

        # Uses: use crate::... or use std::...
        uses = re.findall(r'use\s+([^;]+);', content)
        for u in uses:
            analysis.raw_imports.append(u.strip())

        # Modules: mod foo;
        mods = re.findall(r'mod\s+([a-zA-Z0-9_]+)\s*;', content)
        for m in mods:
            analysis.raw_imports.append(f"mod::{m}")

        # Structs, Enums, Traits
        structs = re.findall(r'(?:pub\s+)?struct\s+([a-zA-Z0-9_]+)', content)
        enums = re.findall(r'(?:pub\s+)?enum\s+([a-zA-Z0-9_]+)', content)
        traits = re.findall(r'(?:pub\s+)?trait\s+([a-zA-Z0-9_]+)', content)
        impls = re.findall(r'impl(?:<[^>]+>)?\s+(?:([a-zA-Z0-9_]+)\s+for\s+)?([a-zA-Z0-9_]+)', content)
        functions = re.findall(r'(?:pub\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)', content)

        detected_concepts = []
        if structs:
            detected_concepts.append(f"Data Structures ({', '.join(structs[:3])})")
        if enums:
            detected_concepts.append(f"Algebraic Data Types / Enums ({', '.join(enums[:3])})")
        if traits:
            detected_concepts.append(f"Trait Abstractions ({', '.join(traits[:3])})")
        if "Result<" in content or "Option<" in content or "?" in content:
            detected_concepts.append("Rust Zero-Cost Error Handling (Result / Option / ?)")
        if "tokio" in content or "async fn" in content:
            detected_concepts.append("Async Tokio Runtime & Concurrency")

        # Element explanations
        for s in structs[:5]:
            analysis.elements.append(ElementExplanation(
                name=f"struct {s}",
                kind="struct",
                snippet=f"struct {s} {{ ... }}",
                what_it_is=f"Rust custom data struct `{s}` defining memory layout and fields.",
                how_it_is_used="Provides strict, type-safe data modeling with zero runtime overhead.",
                where_it_is_used="Declared in this module to represent core state or domain entities.",
                why_it_works="Rust guarantees memory safety without garbage collection via ownership rules and compile-time borrowing checks.",
                best_practices_and_pitfalls="Derive standard traits like `#[derive(Debug, Clone, PartialEq)]` where appropriate."
            ))

        for f in functions[:5]:
            analysis.elements.append(ElementExplanation(
                name=f"fn {f}()",
                kind="function",
                snippet=f"fn {f}(...) {{ ... }}",
                what_it_is=f"Rust function `{f}` implementing typed computation.",
                how_it_is_used="Performs modular operations according to Rust's strict ownership contracts.",
                where_it_is_used="Declared at the module or impl block level.",
                why_it_works="Compiled down to native machine code with LLVM optimizations and zero-cost abstractions.",
                best_practices_and_pitfalls="Return `Result<T, E>` for recoverable errors rather than panicking."
            ))

        analysis.concepts_detected = detected_concepts
        analysis.role_in_codebase = "Rust Systems Service / High-Performance Core Engine"
        analysis.summary = (
            f"Rust module declaring {len(structs)} struct(s), {len(enums)} enum(s), {len(traits)} trait(s), "
            f"and {len(functions)} function(s). Uses {len(analysis.raw_imports)} crate/module imports."
        )
        return analysis

