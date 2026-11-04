import re
from typing import List, Dict, Set
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import CSS_CONCEPT_KNOWLEDGE


class CssParser(BaseParser):
    def __init__(self):
        super().__init__(language="CSS")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        # Regex extractors
        import_urls = re.findall(r'@import\s+(?:url\()?["\']?([^"\'\)\s]+)["\']?\)?', content)
        for imp in import_urls:
            analysis.raw_imports.append(imp)

        asset_urls = re.findall(r'url\(["\']?([^"\'\)\s]+)["\']?\)', content)
        for asset in asset_urls:
            if not asset.startswith(("data:", "http://", "https://")) and asset not in analysis.raw_imports:
                analysis.raw_imports.append(asset)

        # Detect Layout Features
        has_flex = bool(re.search(r'display\s*:\s*flex', content, re.IGNORECASE))
        has_grid = bool(re.search(r'display\s*:\s*grid', content, re.IGNORECASE))
        has_variables = bool(re.search(r'--[a-zA-Z0-9\-_]+\s*:', content))
        keyframes = re.findall(r'@keyframes\s+([a-zA-Z0-9\-_]+)', content)
        media_queries = re.findall(r'@media\s*([^{]+)', content)
        transitions = re.findall(r'(?:transition|transform)\s*:\s*([^;]+)', content)

        # Class and ID selectors count
        class_selectors = set(re.findall(r'\.([a-zA-Z0-9\-_]+)', content))
        id_selectors = set(re.findall(r'#([a-zA-Z0-9\-_]+)', content))

        detected_concepts = []
        detected_frameworks = []

        if has_flex:
            detected_concepts.append("Flexbox One-Dimensional Layout Engine")
            kb = CSS_CONCEPT_KNOWLEDGE["flexbox"]
            analysis.elements.append(ElementExplanation(
                name="Flexbox (`display: flex`)",
                kind="layout",
                line_number=None,
                snippet="display: flex; justify-content: ...; align-items: ...",
                what_it_is=kb["what_it_is"],
                how_it_is_used="Applied to parent containers to automatically align, distribute, and space child elements.",
                where_it_is_used="Found in container and layout rules across the stylesheet.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        if has_grid:
            detected_concepts.append("CSS Grid Two-Dimensional Layout Engine")
            kb = CSS_CONCEPT_KNOWLEDGE["css_grid"]
            analysis.elements.append(ElementExplanation(
                name="CSS Grid (`display: grid`)",
                kind="layout",
                line_number=None,
                snippet="display: grid; grid-template-columns: ...",
                what_it_is=kb["what_it_is"],
                how_it_is_used="Establishes explicit rows and columns for structured card matrices and multi-panel dashboards.",
                where_it_is_used="Defines the overarching scaffolding and responsive layout grids.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        if has_variables:
            detected_concepts.append("CSS Custom Properties / Design Tokens")
            kb = CSS_CONCEPT_KNOWLEDGE["css_variables"]
            analysis.elements.append(ElementExplanation(
                name="CSS Variables (`--custom-properties`)",
                kind="concept",
                line_number=None,
                snippet="--primary-color: #...; --bg-surface: ...;",
                what_it_is=kb["what_it_is"],
                how_it_is_used="Centralizes color palettes, font stacks, and spacing tokens for dynamic theming (e.g. dark/light mode).",
                where_it_is_used="Declared in `:root` and consumed with `var(--...)` throughout declarations.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        if keyframes:
            detected_concepts.append(f"Keyframe Animations ({', '.join(keyframes[:4])})")
            kb = CSS_CONCEPT_KNOWLEDGE["keyframes_animation"]
            analysis.elements.append(ElementExplanation(
                name=f"@keyframes ({len(keyframes)} defined)",
                kind="animation",
                line_number=None,
                snippet=f"@keyframes {keyframes[0]} {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}",
                what_it_is=kb["what_it_is"],
                how_it_is_used=f"Declares discrete animation sequences: {', '.join(keyframes)}.",
                where_it_is_used="Referenced by `animation:` properties on interactive or hero elements.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        if media_queries:
            detected_concepts.append(f"Responsive Breakpoints ({len(media_queries)} queries)")
            kb = CSS_CONCEPT_KNOWLEDGE["media_queries"]
            analysis.elements.append(ElementExplanation(
                name=f"@media Queries ({len(media_queries)} rules)",
                kind="concept",
                line_number=None,
                snippet=f"@media {media_queries[0].strip()[:40]}...",
                what_it_is=kb["what_it_is"],
                how_it_is_used="Adapts layout rules dynamically when screen width changes between mobile, tablet, and desktop viewports.",
                where_it_is_used=f"Configured breakpoints: {', '.join([q.strip()[:25] for q in media_queries[:3]])}...",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        if "@tailwind" in content or "@apply" in content:
            detected_frameworks.append("Tailwind CSS / PostCSS")
        if re.search(r'\$[a-zA-Z0-9\-_]+:', content):
            detected_frameworks.append("SASS / SCSS Preprocessor")

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks
        analysis.role_in_codebase = "Application Styling, Design System Tokens & Responsive Theme Layer"
        analysis.summary = (
            f"CSS stylesheet containing {len(class_selectors)} class selectors, {len(id_selectors)} ID selectors, "
            f"and {len(media_queries)} responsive media query breakpoints. "
            f"{'Employs modern Flexbox alignment. ' if has_flex else ''}"
            f"{'Features CSS Grid layout templates. ' if has_grid else ''}"
            f"{'Configures centralized CSS custom variables. ' if has_variables else ''}"
            f"{f'Defines {len(keyframes)} GPU-accelerated keyframe animations. ' if keyframes else ''}"
        )

        analysis.design_and_style_notes = (
            f"Selector count: {len(class_selectors)} classes, {len(id_selectors)} IDs. "
            f"Layout architectures: {'Flexbox ' if has_flex else ''}{'CSS Grid ' if has_grid else ''}. "
            f"Design tokens: {'Yes (CSS Custom Properties)' if has_variables else 'Hardcoded values'}. "
            f"Responsive adaptation: {len(media_queries)} breakpoints."
        )

        if keyframes or transitions:
            analysis.animations_and_interactions = (
                f"Active motion design layer: {len(keyframes)} @keyframes sequences defined. "
                f"{len(transitions)} transition/transform rules for hover, focus, and state animations."
            )

        return analysis
