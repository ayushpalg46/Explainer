"""
HTML Semantic & Structural Parser for Explainer.
Analyzes HTML tags, semantic landmarks, links, scripts, frameworks, styles, and accessibility.
"""
import re
from html.parser import HTMLParser
from typing import List, Dict, Any, Tuple, Optional
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class DetailedHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags_count: Dict[str, int] = {}
        self.tags_with_attrs: List[Dict[str, Any]] = []
        self.links: List[Dict[str, str]] = []
        self.scripts: List[Dict[str, str]] = []
        self.meta_tags: List[Dict[str, str]] = []
        self.ids_found: List[str] = []
        self.classes_found: set = set()
        self.aria_attributes: List[Dict[str, str]] = []
        self.has_root_container: bool = False
        self.root_container_id: str = ""
        self.current_line: int = 1

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        self.tags_count[tag] = self.tags_count.get(tag, 0) + 1
        
        line_num = self.getpos()[0]
        self.tags_with_attrs.append({
            "tag": tag,
            "attrs": attr_dict,
            "line": line_num
        })

        if "id" in attr_dict:
            elem_id = attr_dict["id"]
            self.ids_found.append(elem_id)
            if elem_id in ("root", "app", "__next", "main-app"):
                self.has_root_container = True
                self.root_container_id = elem_id

        if "class" in attr_dict:
            for cls in attr_dict["class"].split():
                self.classes_found.add(cls)

        for k, v in attr_dict.items():
            if k.startswith("aria-") or k == "role":
                self.aria_attributes.append({"tag": tag, "attr": k, "value": v, "line": line_num})

        if tag == "link":
            self.links.append({
                "rel": attr_dict.get("rel", ""),
                "href": attr_dict.get("href", ""),
                "type": attr_dict.get("type", ""),
                "line": line_num
            })
        elif tag == "script":
            self.scripts.append({
                "src": attr_dict.get("src", ""),
                "type": attr_dict.get("type", "text/javascript"),
                "async": "async" in attr_dict,
                "defer": "defer" in attr_dict,
                "line": line_num
            })
        elif tag == "meta":
            self.meta_tags.append(attr_dict)


class HTMLFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".html", ".htm"]

    @property
    def language_name(self) -> str:
        return "HTML"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        parser = DetailedHTMLParser()
        try:
            parser.feed(content)
        except Exception:
            pass  # Fallback gracefully on malformed HTML fragments

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["HTML5"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        # Analyze Title & Headings
        title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
        doc_title = title_match.group(1).strip() if title_match else "Untitled Document"

        # Check DOCTYPE
        if "<!doctype html>" in content.lower():
            concepts.append("HTML5 Standards Mode Document")
        else:
            concepts.append("HTML Partial or Legacy Document")

        # Process Linked Stylesheets & Assets
        for link in parser.links:
            rel = link.get("rel", "")
            href = link.get("href", "")
            line = link.get("line", 1)
            if href:
                imports.append(FileImport(
                    source=rel or "link",
                    target=href,
                    line=line,
                    import_type="stylesheet" if "stylesheet" in rel else "link"
                ))
                if "stylesheet" in rel:
                    connections.append(FileConnection(
                        source_file=filepath,
                        target_file=href,
                        relation_type="styles",
                        mechanism="<link rel='stylesheet' href='...'>",
                        rationale="Applies CSS visual styling, typography, responsive rules, and layout structures to this HTML DOM."
                    ))

        # Process Scripts
        for script in parser.scripts:
            src = script.get("src", "")
            script_type = script.get("type", "")
            line = script.get("line", 1)
            if src:
                imports.append(FileImport(
                    source=f"script ({script_type})",
                    target=src,
                    line=line,
                    import_type="script"
                ))
                connections.append(FileConnection(
                    source_file=filepath,
                    target_file=src,
                    relation_type="executes_script",
                    mechanism=f"<script src='{src}'> ({'ES Module' if 'module' in script_type else 'Global Script'})",
                    rationale="Injects runtime behavior, client-side interactivity, DOM event listeners, or single-page app mounting logic."
                ))

        # Detect Frameworks & Technologies
        content_lower = content.lower()
        if parser.has_root_container:
            concepts.append(f"Single Page App (SPA) Root Host (`#{parser.root_container_id}`)")
            if any("react" in s.get("src", "").lower() for s in parser.scripts) or "react" in content_lower:
                tech_stack.append("React")
            elif any("vue" in s.get("src", "").lower() for s in parser.scripts) or "vue" in content_lower:
                tech_stack.append("Vue.js")
            else:
                tech_stack.append("SPA Framework Host")

        # CSS Framework detection from classes
        tailwind_indicators = {"flex", "grid", "p-4", "m-2", "text-center", "bg-", "text-", "rounded", "shadow"}
        if any(cls.startswith(("p-", "m-", "text-", "bg-", "flex", "grid", "rounded-")) for cls in parser.classes_found):
            tech_stack.append("Tailwind CSS (Utility Classes)")
        if any(cls.startswith("btn-") or cls in ("container", "row", "col", "navbar") for cls in parser.classes_found):
            tech_stack.append("Bootstrap / Grid Framework")

        # Semantic Landmarks
        semantic_tags = {"header", "nav", "main", "article", "section", "aside", "footer", "dialog"}
        used_semantics = [t for t in semantic_tags if t in parser.tags_count]
        if used_semantics:
            concepts.append(f"Semantic HTML Landmarks: {', '.join(f'<{t}>' for t in used_semantics)}")

        # Forms & Interactivity
        if "form" in parser.tags_count:
            concepts.append(f"Interactive Form Engine ({parser.tags_count['form']} form(s), {parser.tags_count.get('input', 0)} inputs)")
        if "canvas" in parser.tags_count:
            concepts.append("HTML5 Canvas Graphics / WebGL Mount")
        if "svg" in parser.tags_count:
            concepts.append(f"Inline Scalable Vector Graphics ({parser.tags_count['svg']} SVG(s))")

        # Accessibility Assessment
        if parser.aria_attributes:
            concepts.append(f"Accessible Rich Internet Applications (ARIA) Coverage ({len(parser.aria_attributes)} ARIA declarations)")
        else:
            security_and_practices.append("Consider adding explicit ARIA roles/labels and semantic elements for enhanced accessibility (WCAG 2.2).")

        # Responsive Viewport Check
        has_viewport = any(m.get("name", "").lower() == "viewport" for m in parser.meta_tags)
        if has_viewport:
            concepts.append("Mobile-Responsive Viewport Meta Configured")
        else:
            security_and_practices.append("Missing `<meta name='viewport' content='width=device-width, initial-scale=1'>` tag for responsive mobile rendering.")

        # Build Tag Symbols & Detailed Breakdown
        for tag, count in sorted(parser.tags_count.items(), key=lambda x: -x[1]):
            role_desc = self._get_tag_explanation(tag)
            symbols.append(FileSymbol(
                name=f"<{tag}>",
                kind="html_element",
                line=1,
                signature=f"<{tag}> (used {count}x)",
                description=role_desc,
                attributes={"count": count}
            ))

        # Elaborated Components Breakdown
        components_breakdown.append({
            "section": "Document Metadata & Head",
            "details": f"Title: '{doc_title}'. Meta tags: {len(parser.meta_tags)}. Linked stylesheets: {len([l for l in parser.links if 'stylesheet' in l.get('rel', '')])}. Script references: {len(parser.scripts)}."
        })
        if parser.ids_found:
            components_breakdown.append({
                "section": "Key DOM IDs & Mount Points",
                "details": f"Configured DOM Identifiers: {', '.join(parser.ids_found[:15])}{'...' if len(parser.ids_found) > 15 else ''}"
            })
        if parser.classes_found:
            components_breakdown.append({
                "section": "Styling & UI Class Names",
                "details": f"Utilizes {len(parser.classes_found)} unique CSS classes across elements. Top sample: {', '.join(list(parser.classes_found)[:12])}"
            })

        # Summary & Architecture Role
        summary = (
            f"HTML document titled '{doc_title}' containing {loc} lines, {len(parser.tags_count)} distinct HTML tag types, "
            f"and {len(parser.scripts)} client scripts. "
        )
        if parser.has_root_container:
            summary += f"Functions as the primary single-page application (SPA) mounting shell host (`#{parser.root_container_id}`)."
            arch_role = "User Interface Entry Shell (SPA Host / Template Document)"
        else:
            summary += "Functions as a structured content markup page with semantic layout sections."
            arch_role = "View / Presentation Layer Document"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".html",
            language="HTML",
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
            tags=["markup", "frontend", "dom", "ui"]
        )

    def _get_tag_explanation(self, tag: str) -> str:
        explanations = {
            "html": "Root container element for the entire HTML document.",
            "head": "Container for document metadata, character encodings, title, and external stylesheets/scripts.",
            "body": "Container for all rendered document contents and visual UI elements.",
            "title": "Sets browser tab title and search engine result display text.",
            "meta": "Declares structured document metadata such as viewport, charset, SEO keywords, and OpenGraph tags.",
            "link": "Establishes relationships with external resources like CSS stylesheets, web fonts, and favicons.",
            "script": "Loads or embeds executable JavaScript/TypeScript/WebAssembly runtime code.",
            "style": "Embeds internal CSS rules and styles directly within the document.",
            "div": "Generic flow container used for structural layout, grouping, and styling blocks.",
            "span": "Generic inline container for grouping phrasing content or targeted styling.",
            "header": "Introductory container representing introductory content, branding, or navigational links.",
            "nav": "Major navigation block containing links to other pages or sections.",
            "main": "Encapsulates the dominant, non-repeated content unique to this document.",
            "section": "Represents a standalone thematic grouping of content, typically with a heading.",
            "article": "Represents a self-contained composition (post, card, widget) meant to be independently distributable.",
            "aside": "Contains complementary information tangentially related to surrounding content (sidebars, callouts).",
            "footer": "Represents footer content for its nearest section or the page (copyright, contacts, sitemaps).",
            "form": "Interactive document section for collecting, validating, and submitting user inputs to endpoints.",
            "input": "User-interactive control enabling data entry (text, passwords, checkboxes, file uploads).",
            "button": "Clickable control activating interactive behaviors, JavaScript events, or form submissions.",
            "textarea": "Multi-line plain-text editing control.",
            "select": "Dropdown menu control offering a list of selectable options.",
            "h1": "Top-level section heading establishing main topic hierarchy for screen readers and search engines.",
            "h2": "Secondary section heading dividing major themes under h1.",
            "h3": "Subheading providing detailed division under h2 sections.",
            "p": "Paragraph block representing contiguous text phrases and reading copy.",
            "ul": "Unordered list of items typically rendered with bullet points.",
            "ol": "Ordered sequential list of items rendered with numeric/alphabetic markers.",
            "li": "Individual list item element inside a list container.",
            "a": "Hyperlink anchor navigating to external URLs or internal page anchors via href.",
            "img": "Embeds image resources with source path, dimensions, and alternative descriptive text.",
            "canvas": "Bitmap rendering surface used for dynamic 2D/3D graphics, Three.js scenes, or charts.",
            "svg": "Vector graphic container with scalable vector shapes, paths, and icons.",
            "video": "HTML5 media player container for streaming and playing video content."
        }
        return explanations.get(tag, f"Standard HTML element <{tag}> providing structural/semantic content.")
