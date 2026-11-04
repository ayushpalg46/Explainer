"""
CSS Semantic & Design System Parser for Explainer.
Analyzes selectors, layout systems (Flex/Grid), design tokens, animations, media queries, and typography.
"""
import re
from typing import List, Dict, Any, Set
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class CSSFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".css", ".scss", ".sass", ".less"]

    @property
    def language_name(self) -> str:
        return "CSS"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["CSS3"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        # 1. Parse @import statements
        import_matches = re.finditer(r"@import\s+(?:url\(['\"]?([^'\")]+)['\"]?\)|['\"]([^'\"]+)['\"]);?", content)
        for m in import_matches:
            url = m.group(1) or m.group(2)
            line = content[:m.start()].count("\n") + 1
            imports.append(FileImport(
                source="@import",
                target=url,
                line=line,
                import_type="stylesheet"
            ))
            connections.append(FileConnection(
                source_file=filepath,
                target_file=url,
                relation_type="imports_stylesheet",
                mechanism=f"@import url('{url}')",
                rationale="Cascades external stylesheet rules, theme definitions, or modular component styles into this file."
            ))

        # 2. Parse CSS Custom Properties / Design Tokens (:root or variables)
        custom_props = re.findall(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", content)
        unique_vars = {}
        for var_name, var_val in custom_props:
            if var_name not in unique_vars:
                unique_vars[var_name] = var_val.strip()

        if unique_vars:
            concepts.append(f"Design System Tokens / Custom Properties ({len(unique_vars)} CSS Variables defined)")
            for var_name, var_val in list(unique_vars.items())[:20]:
                symbols.append(FileSymbol(
                    name=var_name,
                    kind="css_variable",
                    line=1,
                    signature=f"{var_name}: {var_val}",
                    description=f"Design token declaring reusable design value: '{var_val}'"
                ))

        # 3. Detect Layout Systems (Flexbox vs Grid)
        has_flex = bool(re.search(r"display\s*:\s*flex\b", content, re.IGNORECASE))
        has_grid = bool(re.search(r"display\s*:\s*grid\b", content, re.IGNORECASE))
        has_sticky = bool(re.search(r"position\s*:\s*sticky\b", content, re.IGNORECASE))
        has_fixed = bool(re.search(r"position\s*:\s*fixed\b", content, re.IGNORECASE))

        if has_flex:
            concepts.append("Flexbox Dynamic Flow Layout System")
        if has_grid:
            concepts.append("CSS Grid Two-Dimensional Layout Architecture")
        if has_sticky or has_fixed:
            concepts.append("Viewport Anchored / Sticky Positioning")

        # 4. Detect Animations & Keyframes
        keyframe_matches = re.findall(r"@keyframes\s+([a-zA-Z0-9_-]+)", content)
        if keyframe_matches:
            concepts.append(f"Custom Keyframe Animations ({len(keyframe_matches)} declared: {', '.join(keyframe_matches)})")
            for kf in keyframe_matches:
                symbols.append(FileSymbol(
                    name=f"@keyframes {kf}",
                    kind="keyframe_animation",
                    line=1,
                    description=f"CSS keyframe animation sequence named '{kf}'."
                ))

        # 5. Media Queries & Responsive Breakpoints
        media_queries = re.findall(r"@media\s*([^{]+)\{", content)
        if media_queries:
            clean_queries = [mq.strip() for mq in media_queries]
            concepts.append(f"Responsive Media Query System ({len(clean_queries)} breakpoint rule(s))")
            if any("prefers-color-scheme" in mq for mq in clean_queries):
                concepts.append("Dark Mode / Color Scheme Adaptation (prefers-color-scheme)")

        # 6. Extract Key Selectors & Rules
        # Find selectors before opening brackets '{'
        clean_code = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)  # strip comments
        rule_blocks = re.findall(r"([^{}]+)\{([^}]+)\}", clean_code)
        
        selectors_list: List[str] = []
        classes_found: Set[str] = set()
        ids_found: Set[str] = set()

        for raw_sel, raw_body in rule_blocks:
            sel = raw_sel.strip()
            if sel.startswith("@"):
                continue  # skip @media / @keyframes header lines
            for sub_sel in sel.split(","):
                sub_sel_clean = sub_sel.strip()
                if sub_sel_clean:
                    selectors_list.append(sub_sel_clean)
                    for cls in re.findall(r"\.([a-zA-Z0-9_-]+)", sub_sel_clean):
                        classes_found.add(cls)
                    for elem_id in re.findall(r"#([a-zA-Z0-9_-]+)", sub_sel_clean):
                        ids_found.add(elem_id)

        # Framework Identification
        if any(v.startswith("--tw-") for v in unique_vars) or any(cls.startswith("tw-") for cls in classes_found):
            tech_stack.append("Tailwind CSS Engine")
        if any(cls.startswith("btn-") or cls in ("container", "row", "col") for cls in classes_found):
            tech_stack.append("Bootstrap Classes")

        # Color and Typography Analysis
        font_families = re.findall(r"font-family\s*:\s*([^;]+);", content, re.IGNORECASE)
        if font_families:
            unique_fonts = list(set([f.strip() for f in font_families]))
            concepts.append(f"Typography Scale: {', '.join(unique_fonts[:3])}")

        # Components Breakdown
        components_breakdown.append({
            "section": "Design Tokens & Variable Registry",
            "details": f"Defines {len(unique_vars)} custom variables for brand colors, layout dimensions, and typography scales."
        })
        components_breakdown.append({
            "section": "Selector Rules & Specificity",
            "details": f"Contains {len(selectors_list)} selector declarations targeting {len(classes_found)} unique classes and {len(ids_found)} ID elements."
        })
        if media_queries:
            components_breakdown.append({
                "section": "Responsive Breakpoints",
                "details": f"Implements responsive rules: {'; '.join(clean_queries[:4])}"
            })

        # Best practices & optimizations
        if len(import_matches := list(import_matches)) > 2:
            security_and_practices.append("Multiple `@import` statements detected. Consider bundling or `<link>` tags in HTML to avoid render-blocking waterfalls.")
        if "!important" in content:
            important_count = content.count("!important")
            if important_count > 5:
                security_and_practices.append(f"Found {important_count} instances of `!important`. Consider refactoring CSS specificity for maintainability.")

        summary = (
            f"Cascading Style Sheet ({filename}) declaring {len(selectors_list)} rule blocks, "
            f"{len(unique_vars)} design tokens, and {len(media_queries)} responsive breakpoints."
        )
        arch_role = "Visual Presentation & Design Token System"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".css",
            language="CSS",
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
            tags=["styling", "css", "design-tokens", "layout", "responsive"]
        )
