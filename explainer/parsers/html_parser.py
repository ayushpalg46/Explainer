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

            if tag == "link" and attrs.get("rel") == "stylesheet" and "href" in attrs:
                linked_css.append(attrs["href"])
                analysis.raw_imports.append(attrs["href"])

            if tag == "script" and "src" in attrs:
                linked_scripts.append(attrs["src"])
                analysis.raw_imports.append(attrs["src"])

            if attrs.get("id") in ("root", "app", "__next"):
                has_react_root = True
                detected_frameworks.append("React / Modern SPA Mount Point")

            if tag == "canvas":
                has_canvas = True
            if tag == "svg":
                has_svg = True

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

        # Generate Detailed, Word-by-Word Line Explanations
        seen_tags = set()
        for item in extractor.tags:
            tag = item["tag"]
            attrs = item["attrs"]
            line = item["line"]
            
            attr_parts = [f'{k}="{v}"' for k, v in attrs.items()]
            snippet_str = f"<{tag} {' '.join(attr_parts)}>" if attr_parts else f"<{tag}>"

            is_special = tag in ("link", "script") or attrs.get("id") or "class" in attrs or "onclick" in attrs
            if tag in seen_tags and not is_special:
                continue
            seen_tags.add(tag)

            kb = HTML_TAG_KNOWLEDGE.get(tag, {
                "what_it_is": f"Standard HTML5 element `<{tag}>` providing document structure or markup styling.",
                "simple_analogy": f"Think of `<{tag}>` like a Lego brick that holds a piece of your webpage in place.",
                "what_happens_on_screen": "Displays or organizes content on the page.",
                "what_if_removed": f"The `<{tag}>` section will disappear from the screen.",
                "why_it_works": "Parsed by the browser engine into DOM elements for styling, positioning, and script access.",
                "best_practices": "Ensure proper closing tags and valid semantic hierarchy."
            })

            # Word-by-word breakdown
            words_dict: Dict[str, str] = {
                tag: kb["what_it_is"]
            }
            conn_note: Optional[str] = None

            if attrs:
                for k, v in attrs.items():
                    if k == "id":
                        words_dict[f'id="{v}"'] = f"A unique name-tag. There is only one '{v}' element in the document, allowing code to find this exact box."
                        if v in ("root", "app", "__next"):
                            conn_note = f"Mount point anchor where client-side JavaScript (e.g. React/app.js) attaches and renders the interactive UI."
                    elif k == "class":
                        words_dict[f'class="{v}"'] = f"A style costume label. Connects this element to CSS styling rules (like colors, paddings, and borders) defined in stylesheets."
                    elif k == "src":
                        words_dict[f'src="{v}"'] = f"The source path. Tells the browser where to fetch this script file or image from disk."
                        conn_note = f"Directly loads and executes the external JavaScript bundle '{v}'."
                    elif k == "href":
                        words_dict[f'href="{v}"'] = f"Hyperlink reference. Points the browser to the address of the linked file '{v}'."
                        if attrs.get("rel") == "stylesheet":
                            conn_note = f"Loads external stylesheet '{v}', applying all design tokens, fonts, and colors to this page."
                    elif k == "rel":
                        words_dict[f'rel="{v}"'] = f"Specifies the relationship between this HTML page and the linked file."
                    elif k == "onclick":
                        words_dict[f'onclick="{v}"'] = f"An 'ear' listening for clicks. The moment a user clicks, it shouts: 'Run the {v} recipe now!'"
                        conn_note = f"Directly calls the interactive function '{v}' defined in the connected JavaScript code."
                    else:
                        words_dict[f'{k}="{v}"'] = f"Configures the attribute '{k}' with value '{v}'."

            explanation = ElementExplanation(
                name=f"<{tag}>",
                kind="tag",
                line_number=line,
                snippet=snippet_str,
                what_it_is=kb["what_it_is"],
                how_it_is_used=f"Written on line {line} as `{snippet_str}`.",
                where_it_is_used=f"Line {line} of `{relative_path}`. Total `<{tag}>` tags in file: {tag_counts.get(tag, 1)}.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb.get("best_practices", "Follow standard HTML conventions."),
                simple_analogy=kb.get("simple_analogy", f"Think of `<{tag}>` like a Lego block building the page."),
                what_happens_on_screen=kb.get("what_happens_on_screen", "Draws or positions this element on screen."),
                what_if_removed=kb.get("what_if_removed", "This element will vanish from the page."),
                words_breakdown=words_dict,
                interconnection_note=conn_note
            )
            analysis.elements.append(explanation)

        analysis.beginner_story = (
            f"Imagine this HTML file `{relative_path}` is a real physical toy box sitting on a stage! "
            f"It sets up the roof and secret rules in `<head>`, the big living room where all the toys perform in `<body>`, "
            f"{'and builds an empty stage `<div id=\"root\">` waiting for your React code to jump in and build the whole interactive world!' if has_react_root else 'and organizes the buttons, text, and pictures on the page.'}"
        )

        analysis.summary = (
            f"HTML document containing {len(extractor.tags)} elements across {len(tag_counts)} distinct tag types. "
            f"Serves as the visual entrypoint or template. "
            f"{'Configured as a React/SPA application mount point. ' if has_react_root else ''}"
            f"References {len(linked_css)} stylesheet(s) and {len(linked_scripts)} script bundle(s)."
        )
        analysis.role_in_codebase = "Application Presentation & DOM Root Entrypoint" if has_react_root else "HTML Template / View"
        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks
        
        analysis.design_and_style_notes = (
            f"Links {len(linked_css)} external stylesheet(s). "
            f"{'Utilizes Tailwind utility classes in markup. ' if 'Tailwind CSS Utilities' in detected_frameworks else 'Custom or standard semantic styling. '}"
            f"{'Contains hardware-accelerated canvas surfaces for interactive graphics. ' if has_canvas else ''}"
        )
        if has_canvas or has_svg:
            analysis.animations_and_interactions = "Interactive graphics pipeline detected via HTML5 Canvas or SVG vector elements."

        return analysis
