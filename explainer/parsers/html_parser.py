import re
from html.parser import HTMLParser
from typing import List, Dict, Tuple, Optional, Any
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import HTML_TAG_KNOWLEDGE


class TagExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: List[Dict[str, Any]] = []

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        attrs_dict = dict(attrs)
        self.tags.append({
            "tag": tag.lower(),
            "line": line,
            "col": col,
            "attrs": attrs_dict
        })


class HtmlParser(BaseParser):
    def __init__(self):
        super().__init__(language="HTML")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        
        extractor = TagExtractor()
        try:
            extractor.feed(content)
        except Exception:
            # Fallback regex tag matching if malformed html
            for m in re.finditer(r'<([a-zA-Z0-9\-]+)([^>]*)>', content):
                line = content[:m.start()].count('\n') + 1
                tag_name = m.group(1).lower()
                attrs_str = m.group(2)
                attrs_dict = dict(re.findall(r'([a-zA-Z0-9\-]+)=["\']([^"\']*)["\']', attrs_str))
                extractor.tags.append({
                    "tag": tag_name,
                    "line": line,
                    "col": 0,
                    "attrs": attrs_dict
                })

        tag_counts: Dict[str, int] = {}
        linked_css: List[str] = []
        linked_scripts: List[str] = []
        detected_frameworks: List[str] = []
        detected_concepts: List[str] = []
        has_react_root = False
        has_canvas = False
        has_svg = False

        for item in extractor.tags:
            tag = item["tag"]
            attrs = item["attrs"]
            line = item["line"]
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Detect CSS links
            if tag == "link" and attrs.get("rel") == "stylesheet" and "href" in attrs:
                linked_css.append(attrs["href"])
                analysis.raw_imports.append(attrs["href"])

            # Detect script links
            if tag == "script" and "src" in attrs:
                linked_scripts.append(attrs["src"])
                analysis.raw_imports.append(attrs["src"])

            # Detect React mount root
            if attrs.get("id") in ("root", "app", "__next"):
                has_react_root = True
                detected_frameworks.append("React / Modern SPA Mount Point")

            # Detect Canvas & SVG
            if tag == "canvas":
                has_canvas = True
            if tag == "svg":
                has_svg = True

            # Detect Tailwind or utility classes
            cls = attrs.get("class", "")
            if any(tw in cls for tw in ["flex", "grid", "p-", "m-", "text-", "bg-", "dark:"]):
                if "Tailwind CSS Utilities" not in detected_frameworks:
                    detected_frameworks.append("Tailwind CSS Utilities")

        if linked_css:
            detected_concepts.append(f"External Stylesheets ({len(linked_css)} referenced)")
        if linked_scripts:
            detected_concepts.append(f"External Script Bundles ({len(linked_scripts)} referenced)")
        if has_react_root:
            detected_concepts.append("Single Page Application (SPA) DOM Anchor")
        if has_canvas:
            detected_concepts.append("2D/3D WebGL Canvas Rendering")
        if has_svg:
            detected_concepts.append("Vector Iconography / Graphics (SVG)")

        # Generate ElementExplanations for unique tags
        for tag, count in tag_counts.items():
            kb = HTML_TAG_KNOWLEDGE.get(tag, {
                "what_it_is": f"Standard HTML5 element `<{tag}>` providing document structure or markup styling.",
                "why_it_works": "Parsed by the browser engine into DOM elements for styling, positioning, and script access.",
                "best_practices": "Ensure proper closing tags and valid semantic hierarchy."
            })
            
            # Find representative line
            rep_line = next((t["line"] for t in extractor.tags if t["tag"] == tag), None)
            
            # Where is it used context
            where_desc = f"Used {count} time(s) across the document. "
            if tag == "link":
                where_desc += f"Imports stylesheets/resources: {', '.join(linked_css[:3]) if linked_css else 'metadata'}. "
            elif tag == "script":
                where_desc += f"Loads scripts: {', '.join(linked_scripts[:3]) if linked_scripts else 'inline code'}. "
            elif tag == "div" and has_react_root:
                where_desc += "Contains the primary React/SPA root mount point (`#root`). "

            explanation = ElementExplanation(
                name=f"<{tag}>",
                kind="tag",
                line_number=rep_line,
                snippet=f"<{tag} ...> (count: {count})",
                what_it_is=kb["what_it_is"],
                how_it_is_used=f"Defined in the markup to structure content. Count in file: {count}.",
                where_it_is_used=where_desc,
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            )
            analysis.elements.append(explanation)

        # Summary & role
        analysis.summary = (
            f"HTML document containing {len(extractor.tags)} elements across {len(tag_counts)} distinct tag types. "
            f"Serves as the visual entrypoint or template. "
            f"{'Configured as a React/SPA application mount point. ' if has_react_root else ''}"
            f"References {len(linked_css)} stylesheet(s) and {len(linked_scripts)} script bundle(s)."
        )
        analysis.role_in_codebase = "Application Presentation & DOM Root Entrypoint" if has_react_root else "HTML Template / View"
        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks
        
        # Design & Animation notes
        analysis.design_and_style_notes = (
            f"Links {len(linked_css)} external stylesheet(s). "
            f"{'Utilizes Tailwind utility classes in markup. ' if 'Tailwind CSS Utilities' in detected_frameworks else 'Custom or standard semantic styling. '}"
            f"{'Contains hardware-accelerated canvas surfaces for interactive graphics. ' if has_canvas else ''}"
        )
        if has_canvas or has_svg:
            analysis.animations_and_interactions = "Interactive graphics pipeline detected via HTML5 Canvas or SVG vector elements."

        return analysis
