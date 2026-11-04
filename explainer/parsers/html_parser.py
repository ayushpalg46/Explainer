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
        lines = content.splitlines()

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

        # Generate Detailed, Word-by-Word Line Explanations directly from the codefile
        seen_tags = set()
        for item in extractor.tags:
            tag = item["tag"]
            attrs = item["attrs"]
            line = item["line"]

            # Extract the exact line(s) from the codefile
            raw_line = ""
            end_line = line
            if 1 <= line <= len(lines):
                raw_line = lines[line - 1].strip()
                # If tag spans multiple lines in the codefile, gather them
                if ">" not in raw_line and line < len(lines):
                    parts = [raw_line]
                    for nxt in range(line, min(line + 8, len(lines))):
                        nxt_line = lines[nxt].strip()
                        parts.append(nxt_line)
                        end_line = nxt + 1
                        if ">" in nxt_line:
                            break
                    raw_line = " ".join(parts)
            
            if not raw_line:
                attr_parts = [f'{k}="{v}"' for k, v in attrs.items()]
                raw_line = f"<{tag} {' '.join(attr_parts)}>" if attr_parts else f"<{tag}>"

            line_display = f"{line}-{end_line}" if end_line > line else f"{line}"

            is_special = tag in ("link", "script", "button", "h1", "h2", "h3", "a", "img", "form", "input") or attrs.get("id") or "class" in attrs or "onclick" in attrs
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

            # Check for inner text on this line (e.g. <h1>My Toy Box</h1> or <button>Open Box!</button>)
            inner_text = ""
            text_m = re.search(r'>([^<]+)<', raw_line)
            if text_m:
                inner_text = text_m.group(1).strip()

            # Word-by-word breakdown dictionary
            words_dict: Dict[str, str] = {}
            if tag == "div":
                words_dict["div"] = 'Short for "division". An invisible cardboard box used to bundle things together.'
            elif tag == "h1":
                words_dict["h1"] = '"Heading 1" — the biggest, most important title on the page.'
            elif tag == "button":
                words_dict["button"] = "An interactive push-button."
            elif tag == "link":
                words_dict["link"] = "Connects an outside file to this HTML page."
            elif tag == "script":
                words_dict["script"] = 'Tells the browser: "Here is a book of code instructions."'
            elif tag == "span":
                words_dict["span"] = 'Short for "span". An inline container used to style words without breaking line flow.'
            elif tag == "p":
                words_dict["p"] = 'Short for "paragraph". A text block element with automatic margins.'
            elif tag == "a":
                words_dict["a"] = 'Short for "anchor". A clickable link that navigates to another page or section.'
            elif tag == "img":
                words_dict["img"] = "An image element that displays graphics or photos on the page."
            else:
                words_dict[tag] = kb["what_it_is"]

            conn_notes: List[str] = []

            # Populate attributes word-by-word
            if attrs:
                for k, v in attrs.items():
                    if k == "id":
                        words_dict[f'id="{v}"'] = f'A unique name-tag (like a personal ID card). There is only one "{v}" box in the whole world.'
                        if v in ("root", "app", "__next"):
                            conn_notes.append(f"app.js searches for this exact box using document.getElementById('{v}') to place the app inside it.")
                        else:
                            conn_notes.append(f"JavaScript can target this element via document.getElementById('{v}').")
                    elif k == "class":
                        words_dict[f'class="{v}"'] = f'A style group label / costume label. It tells CSS: "Treat this like a {v} box."'
                        if linked_css:
                            for css_file in linked_css:
                                conn_notes.append(f"{css_file} uses .{v.split()[0]} to apply styling and layout rules.")
                        else:
                            conn_notes.append(f"style.css uses .{v.split()[0]} to style and position this element.")
                    elif k == "rel":
                        words_dict[f'rel="{v}"'] = f'Tells the browser: "This outside file contains {v} rules."'
                    elif k == "href":
                        words_dict[f'href="{v}"'] = f'The address of the linked resource: "{v}".'
                        if attrs.get("rel") == "stylesheet":
                            conn_notes.append(f"Pulls all design rules, colors, and fonts from {v}.")
                    elif k == "src":
                        words_dict[f'src="{v}"'] = f'The file path where the brain code lives: "{v}".'
                        conn_notes.append(f"Directly loads and executes the JavaScript code inside {v}.")
                    elif k == "onclick":
                        words_dict[f'onclick="{v}"'] = f'An "ear" listening for clicks. The moment a finger or mouse clicks this button, it shouts: "Robot, run the {v} recipe now!"'
                        fn_name = v.replace("()", "")
                        conn_notes.append(f"Directly triggers the {fn_name}() function written inside connected JavaScript files.")
                    else:
                        words_dict[f'{k}="{v}"'] = f"Configures the attribute '{k}' with value '{v}'."

            if inner_text:
                words_dict[f'"{inner_text}"'] = "The actual words displayed to the user."

            # Construct plain English 'What is written?'
            if tag == "div" and attrs:
                attr_desc = " and ".join([f'{k}="{v}"' for k, v in attrs.items()])
                what_is_written = f"A <div> tag with {len(attrs)} label(s): {attr_desc}."
            elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                what_is_written = f"An <{tag}> heading with the text \"{inner_text or 'Title'}\"."
            elif tag == "button":
                call_desc = f" that runs {attrs['onclick']}" if "onclick" in attrs else ""
                what_is_written = f"A clickable button{call_desc}."
            elif tag == "link" and attrs.get("rel") == "stylesheet":
                what_is_written = f"A link tag importing {attrs.get('href', 'stylesheet')}."
            elif tag == "script" and "src" in attrs:
                what_is_written = f"A script tag loading the JavaScript code from {attrs.get('src', 'script')}."
            elif attrs:
                attr_desc = ", ".join([f'{k}="{v}"' for k, v in attrs.items()])
                what_is_written = f"A <{tag}> element configured with {attr_desc}."
            else:
                what_is_written = f"A standard <{tag}> element."

            # Specific beginner analogies and effects
            analogy = kb.get("simple_analogy", f"Think of `<{tag}>` like a Lego block building the page.")
            screen_effect = kb.get("what_happens_on_screen", "Draws or positions this element on screen.")
            breaks_if_removed = kb.get("what_if_removed", "This element will vanish from the page.")

            if tag == "div" and attrs.get("id") == "root":
                analogy = "Think of this like setting down an empty laundry basket before you put clothes in it."
                screen_effect = "Nothing visible yet! It creates an invisible box on a new line where child elements will sit."
                breaks_if_removed = 'The title and button lose their container, spill across the screen, and the JavaScript code crashes because it cannot find "root".'
            elif tag in ("h1", "h2", "h3"):
                analogy = "Like the big colorful title on the front cover of a storybook."
                screen_effect = f"Big, bold text appears on the screen reading: {inner_text or 'Title'}."
                breaks_if_removed = "Visitors won't see any title and won't know what this page is for."
            elif tag == "button":
                analogy = "Like a doorbell on a front door. When you push it, the bell rings inside the house!"
                screen_effect = "Renders a clickable rectangular button that sinks slightly when clicked."
                breaks_if_removed = "Users have no way to open the box or trigger the action."
            elif tag == "link" and attrs.get("rel") == "stylesheet":
                analogy = 'Like calling the painter: "Please bring your paint cans and dress up my toy box!"'
                screen_effect = "The plain black-and-white page transforms into beautiful colors, fonts, and shadows."
                breaks_if_removed = "All colors, fonts, centering, and button designs vanish, leaving bare, ugly text."
            elif tag == "script" and "src" in attrs:
                analogy = "Like inserting the batteries and brain chip into a toy robot so it can move and talk!"
                screen_effect = "Invisible on screen, but gives the page life so clicks actually do things."
                breaks_if_removed = "The page is frozen like a statue. Clicking the button does absolutely nothing."

            interconn_str = "\n".join(conn_notes) if conn_notes else None

            explanation = ElementExplanation(
                name=f"<{tag}>",
                kind="tag",
                line_number=line_display,
                snippet=raw_line,
                what_it_is=what_is_written,
                how_it_is_used=f"Written on line {line_display} as `{raw_line}`.",
                where_it_is_used=f"Line {line_display} of `{relative_path}`.",
                why_it_works=kb.get("why_it_works", "Parsed into DOM elements by the browser engine."),
                best_practices_and_pitfalls=kb.get("best_practices", "Follow standard HTML conventions."),
                simple_analogy=analogy,
                what_happens_on_screen=screen_effect,
                what_if_removed=breaks_if_removed,
                words_breakdown=words_dict,
                interconnection_note=interconn_str
            )
            analysis.elements.append(explanation)

        analysis.beginner_story = (
            "Imagine this code is a real physical toy box sitting on a stage. "
            "It puts down an empty box on the floor (<div>), paints a big sign above it that says 'My Toy Box' (<h1>), "
            "and puts a shiny red doorbell button on the front (<button>). "
            f"Then it calls the painter ({', '.join(linked_css) if linked_css else 'style.css'}) to paint it with colors, "
            f"and hires an invisible robot assistant ({', '.join(linked_scripts) if linked_scripts else 'app.js'}) to open the box whenever someone presses the doorbell!"
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

        return analysis
