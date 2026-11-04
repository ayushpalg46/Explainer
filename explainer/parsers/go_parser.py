import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class GoParser(BaseParser):
    def __init__(self):
        super().__init__(language="Go")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)

        # Package
        pkg_match = re.search(r'package\s+([a-zA-Z0-9_]+)', content)
        package_name = pkg_match.group(1) if pkg_match else "main"

        # Imports
        # Multi-line imports or single
        import_block = re.search(r'import\s*\((.*?)\)', content, re.DOTALL)
        if import_block:
            for imp in re.findall(r'["\']([^"\']+)["\']', import_block.group(1)):
                analysis.raw_imports.append(imp)
        for single in re.findall(r'import\s+["\']([^"\']+)["\']', content):
            if single not in analysis.raw_imports:
                analysis.raw_imports.append(single)

        # Structs, Interfaces, Functions
        structs = re.findall(r'type\s+([a-zA-Z0-9_]+)\s+struct', content)
        interfaces = re.findall(r'type\s+([a-zA-Z0-9_]+)\s+interface', content)
        functions = re.findall(r'func\s+(?:\([^)]+\)\s+)?([a-zA-Z0-9_]+)\s*\(', content)

        has_goroutine = bool(re.search(r'\bgo\s+[a-zA-Z0-9_]+|\bgo\s+func\(', content))
        has_channel = bool(re.search(r'\bchan\s+|<-', content))

        detected_frameworks = []
        detected_concepts = []

        all_imports = " ".join(analysis.raw_imports)
        if "gin-gonic" in all_imports:
            detected_frameworks.append("Gin Web Framework")
        if "gorm.io" in all_imports:
            detected_frameworks.append("GORM ORM")
        if "net/http" in all_imports:
            detected_frameworks.append("Go Standard net/http")

        if structs:
            detected_concepts.append(f"Go Composite Structs ({', '.join(structs[:3])})")
        if interfaces:
            detected_concepts.append(f"Implicit Go Interfaces ({', '.join(interfaces[:3])})")
        if has_goroutine or has_channel:
            detected_concepts.append("CSP Concurrency (Goroutines & Channels)")

        for s in structs[:5]:
            analysis.elements.append(ElementExplanation(
                name=f"type {s} struct",
                kind="struct",
                snippet=f"type {s} struct {{ ... }}",
                what_it_is=f"Go struct `{s}` defining a typed data container.",
                how_it_is_used="Stores state and serves as receiver for associated Go methods.",
                where_it_is_used=f"Part of package `{package_name}`.",
                why_it_works="Allocated contiguously in memory for minimal cache misses and fast GC scanning.",
                best_practices_and_pitfalls="Use struct tags (`json:\"name\"`) to govern serialization."
            ))

        for f in functions[:5]:
            analysis.elements.append(ElementExplanation(
                name=f"func {f}()",
                kind="function",
                snippet=f"func {f}(...) {{ ... }}",
                what_it_is=f"Go function or method `{f}`.",
                how_it_is_used="Executes explicit, procedural logic with explicit error checking.",
                where_it_is_used=f"Defined in package `{package_name}`.",
                why_it_works="Compiled to statically-linked native binary with an embedded Go runtime.",
                best_practices_and_pitfalls="Always check returned `err` values immediately (`if err != nil`)."
            ))

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks
        analysis.role_in_codebase = "Go Cloud Microservice / High-Performance Backend Routine"
        analysis.summary = (
            f"Go file in package `{package_name}` with {len(structs)} struct(s), {len(interfaces)} interface(s), "
            f"and {len(functions)} function(s). Uses {len(analysis.raw_imports)} package imports. "
            f"{'Features lightweight goroutine concurrency. ' if has_goroutine else ''}"
        )
        return analysis
