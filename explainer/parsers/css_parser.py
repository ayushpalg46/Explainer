import re
from typing import List, Dict, Set, Optional
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import CSS_CONCEPT_KNOWLEDGE


class CssParser(BaseParser):
    def __init__(self):
        super().__init__(language="CSS")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        # Regex extractors for imports
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

        detected_concepts = []
        if has_flex:
            detected_concepts.append("Flexbox One-Dimensional Layout Engine")
        if has_grid:
            detected_concepts.append("CSS Grid Two-Dimensional Layout Engine")
        if has_variables:
            detected_concepts.append("CSS Custom Properties / Design Tokens")
        if keyframes:
            detected_concepts.append(f"Keyframe Animations ({', '.join(keyframes[:4])})")
        if media_queries:
            detected_concepts.append(f"Responsive Breakpoints ({len(media_queries)} queries)")

        # Parse concrete CSS rules block by block
        rule_pattern = re.finditer(r'([^{]+)\{([^}]+)\}', content)
        rules_found = 0
        for m in rule_pattern:
            selector = m.group(1).strip()
            body = m.group(2).strip()
            # Skip media query wrappers or empty selectors
            if selector.startswith("@media") or not selector:
                continue
            rules_found += 1
            line_no = content[:m.start()].count('\n') + 1

            # Format words breakdown for this rule
            words_dict: Dict[str, str] = {}
            if selector.startswith("."):
                words_dict[selector] = f"Class selector. Targets any HTML tag with class='{selector[1:]}'."
            elif selector.startswith("#"):
                words_dict[selector] = f"ID selector. Targets the unique element with id='{selector[1:]}'."
            elif selector.startswith(":root"):
                words_dict[":root"] = "Root selector. Targets the highest level of the document to store global CSS variables."
            else:
                words_dict[selector] = f"Tag selector. Targets all `<{selector}>` elements across the page."

            words_dict["{ ... }"] = "Braces enclosing the list of styling recipes for this selector."

            # Parse individual properties
            props = [p.strip() for p in body.split(";") if p.strip()]
            for p in props[:4]:
                if ":" in p:
                    prop_name, prop_val = p.split(":", 1)
                    prop_name = prop_name.strip()
                    prop_val = prop_val.strip()
                    if "display" in prop_name:
                        words_dict[p] = f"Controls the layout engine: '{prop_val}' arranges child elements."
                    elif "background" in prop_name:
                        words_dict[p] = f"Paints the surface with color or image: '{prop_val}'."
                    elif "padding" in prop_name:
                        words_dict[p] = f"Creates breathing room / pillow cushion inside the element ({prop_val})."
                    elif "margin" in prop_name:
                        words_dict[p] = f"Creates personal space outside the box pushing neighbors away ({prop_val})."
                    elif "border-radius" in prop_name:
                        words_dict[p] = f"Smoothes sharp pointy corners into rounded curves ({prop_val})."
                    elif "color" in prop_name:
                        words_dict[p] = f"Sets the text color to '{prop_val}'."
                    elif prop_name.startswith("--"):
                        words_dict[p] = f"Declares reusable theme variable '{prop_name}' with value '{prop_val}'."
                    else:
                        words_dict[p] = f"Sets CSS property '{prop_name}' to '{prop_val}'."

            analogy = (
                f"Think of `{selector}` like a costume dress-up card! Any element wearing the `{selector}` label "
                f"gets painted with these colors and given this exact shape."
            )
            screen_effect = f"Visually formats `{selector}` elements with custom layout, colors, and dimensions."
            removal_consequence = f"The `{selector}` elements will lose their custom colors, padding, and positioning."
            interconnection = f"Directly targets and styles matching elements in connected HTML and JSX files."

            snippet_text = f"{selector} {{ {'; '.join(props[:4])}; }}" if len(props) <= 4 else f"{selector} {{ {'; '.join(props[:3])}; ... }}"

            analysis.elements.append(ElementExplanation(
                name=f"Rule: {selector}",
                kind="rule",
                line_number=line_no,
                snippet=snippet_text,
                what_it_is=f"CSS styling rule targeting `{selector}` with {len(props)} property declarations.",
                how_it_is_used=f"Applied at line {line_no} to style elements matching `{selector}`.",
                where_it_is_used=f"Line {line_no} of `{relative_path}`.",
                why_it_works="The browser CSSOM engine matches the selector against DOM nodes and computes render styles.",
                best_practices_and_pitfalls="Avoid overly specific selectors. Prefer reusable utility or component class names.",
                simple_analogy=analogy,
                what_happens_on_screen=screen_effect,
                what_if_removed=removal_consequence,
                words_breakdown=words_dict,
                interconnection_note=interconnection
            ))

        # Add Concept Elements for Flexbox, Grid, Variables, Keyframes if present
        if has_flex:
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
                best_practices_and_pitfalls=kb["best_practices"],
                simple_analogy=kb["simple_analogy"],
                what_happens_on_screen=kb["what_happens_on_screen"],
                what_if_removed=kb["what_if_removed"]
            ))

        if has_grid:
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
                best_practices_and_pitfalls=kb["best_practices"],
                simple_analogy=kb["simple_analogy"],
                what_happens_on_screen=kb["what_happens_on_screen"],
                what_if_removed=kb["what_if_removed"]
            ))

        if has_variables:
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
                best_practices_and_pitfalls=kb["best_practices"],
                simple_analogy=kb["simple_analogy"],
                what_happens_on_screen=kb["what_happens_on_screen"],
                what_if_removed=kb["what_if_removed"]
            ))

        if keyframes:
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
                best_practices_and_pitfalls=kb["best_practices"],
                simple_analogy=kb["simple_analogy"],
                what_happens_on_screen=kb["what_happens_on_screen"],
                what_if_removed=kb["what_if_removed"]
            ))

        if media_queries:
            kb = CSS_CONCEPT_KNOWLEDGE["media_queries"]
            analysis.elements.append(ElementExplanation(
                name=f"@media Queries ({len(media_queries)} rules)",
                kind="concept",
                line_number=None,
                snippet=f"@media {media_queries[0].strip()[:40]}...",
                what_it_is=kb["what_it_is"],
                how_it_is_used="Adapts layout rules dynamically when screen width changes between mobile, tablet, and desktop viewports.",
                where_it_is_used="Encloses responsive breakpoint style overrides.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"],
                simple_analogy=kb["simple_analogy"],
                what_happens_on_screen=kb["what_happens_on_screen"],
                what_if_removed=kb["what_if_removed"]
            ))

        analysis.beginner_story = (
            f"Imagine your webpage is a paper doll. This CSS file `{relative_path}` is the doll's wardrobe and box of colored crayons! "
            f"It contains {rules_found} styling rule(s) that paint the background, dress up buttons with curved corners and shadows, "
            f"and arrange all the furniture in the room so nothing looks messy or cramped."
        )

        analysis.concepts_detected = detected_concepts
        analysis.role_in_codebase = "Visual Design Tokens, Layout Styling & Responsive Theming"
        analysis.summary = (
            f"Cascading Style Sheet defining {rules_found} style rule(s) across {len(analysis.raw_imports)} imported assets. "
            f"{'Configures Flexbox space distribution. ' if has_flex else ''}"
            f"{'Implements CSS Grid layouts. ' if has_grid else ''}"
            f"{'Declares custom CSS variables. ' if has_variables else ''}"
            f"{f'Defines {len(keyframes)} animation sequence(s). ' if keyframes else ''}"
            f"{f'Provides {len(media_queries)} responsive breakpoint(s). ' if media_queries else ''}"
        )
        return analysis
