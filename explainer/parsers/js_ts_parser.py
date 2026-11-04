import re
from typing import List, Dict, Set
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import JS_REACT_KNOWLEDGE


class JsTsParser(BaseParser):
    def __init__(self, is_typescript: bool = False, is_jsx: bool = False):
        lang = "TypeScript" if is_typescript else "JavaScript"
        if is_jsx:
            lang += " (JSX/React)"
        super().__init__(language=lang)
        self.is_typescript = is_typescript
        self.is_jsx = is_jsx

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        # Extract Imports
        import_matches = list(re.finditer(r'import\s+((?:[a-zA-Z0-9_{}\s*,*]+)\s+from\s+)?["\']([^"\']+)["\']', content))
        for m in import_matches:
            target = m.group(2)
            imported_symbols = m.group(1).replace("from", "").strip() if m.group(1) else target
            analysis.raw_imports.append(target)
            line_no = content[:m.start()].count('\n') + 1

            analysis.elements.append(ElementExplanation(
                name=f"import from '{target}'",
                kind="import",
                line_number=line_no,
                snippet=m.group(0),
                what_it_is=f"Brings tools or components (`{imported_symbols}`) from the external file or library `{target}`.",
                how_it_is_used=f"Written at line {line_no} to import dependencies for this file.",
                where_it_is_used=f"Line {line_no} of `{relative_path}`.",
                why_it_works="The JavaScript module loader links the exported functions from the target module into this file's scope.",
                best_practices_and_pitfalls="Import only what you need and keep imports organized at the top of the file.",
                simple_analogy="Think of this like borrowing a toy or tool from your friend's room so you can build something cool here!",
                what_happens_on_screen="Doesn't show a picture directly, but makes the borrowed functions and buttons available to use.",
                what_if_removed=f"The file crashes with an error saying: 'I cannot find {imported_symbols}!'."
            ))

        # Extract Exports
        export_matches = re.finditer(r'export\s+(?:default\s+)?(?:const|let|var|function\*?|class|type|interface)?\s*([a-zA-Z0-9_$]+)?', content)
        for m in export_matches:
            exp_name = m.group(1)
            if exp_name and exp_name not in analysis.raw_exports:
                analysis.raw_exports.append(exp_name)

        # Detect Frameworks & Libraries
        detected_frameworks = []
        detected_concepts = []

        if any(lib in content for lib in ["react", "React", "useState", "jsx", "JSX"]):
            detected_frameworks.append("React.js")
        if any(lib in content for lib in ["next/", "next/router", "next/image"]):
            detected_frameworks.append("Next.js")
        if any(lib in content for lib in ["express", "app.use", "app.get", "express()"]):
            detected_frameworks.append("Express.js Backend Framework")
        if any(lib in content for lib in ["three", "THREE.", "Scene()", "PerspectiveCamera"]):
            detected_frameworks.append("Three.js 3D Engine")
        if any(lib in content for lib in ["gsap", "ScrollTrigger", "gsap.to"]):
            detected_frameworks.append("GSAP Animation Library")
        if self.is_typescript or "interface " in content or "type " in content:
            detected_concepts.append("Static TypeScript Type Contracts")

        # React Hooks Detection
        hooks_found = {}
        for hook_name in ["useState", "useEffect", "useContext", "useReducer", "useCallback", "useMemo", "useRef", "useId"]:
            matches = list(re.finditer(rf'\b({hook_name})\s*\(', content))
            if matches:
                hooks_found[hook_name] = len(matches)
                line_no = content[:matches[0].start()].count('\n') + 1
                kb = JS_REACT_KNOWLEDGE.get(hook_name, {})
                analysis.elements.append(ElementExplanation(
                    name=f"Hook: {hook_name}()",
                    kind="hook",
                    line_number=line_no,
                    snippet=f"const [...] = {hook_name}(...)",
                    what_it_is=kb.get("what_it_is", f"React standard hook `{hook_name}`."),
                    how_it_is_used=f"Invoked {len(matches)} time(s) to manage state or lifecycle.",
                    where_it_is_used=f"First invoked around line {line_no}.",
                    why_it_works=kb.get("why_it_works", "Manages state or effects via React's internal Fiber node tracking."),
                    best_practices_and_pitfalls=kb.get("best_practices", "Follow the Rules of Hooks: call only at the top level."),
                    simple_analogy=kb.get("simple_analogy", "Think of this like an erasable whiteboard scoreboard that redraws the screen whenever the score changes!"),
                    what_happens_on_screen=kb.get("what_happens_on_screen", "The number or item on screen instantly updates before your eyes."),
                    what_if_removed=kb.get("what_if_removed", "The computer forgets what you clicked and the screen never updates.")
                ))

        if hooks_found:
            detected_concepts.append(f"React State & Hooks Architecture ({', '.join(hooks_found.keys())})")

        # React Components Detection
        component_matches = re.finditer(r'(?:function\s+([A-Z][a-zA-Z0-9_]*)|(?:const|let)\s+([A-Z][a-zA-Z0-9_]*)\s*=\s*(?:\([^)]*\)|[a-zA-Z0-9_]+)\s*=>)', content)
        components = []
        for m in component_matches:
            cname = m.group(1) or m.group(2)
            if cname:
                components.append(cname)
                line_no = content[:m.start()].count('\n') + 1
                analysis.elements.append(ElementExplanation(
                    name=f"Component: <{cname} />",
                    kind="component",
                    line_number=line_no,
                    snippet=f"function {cname}(...) {{ return <...> }}",
                    what_it_is=f"Declarative React UI component `<{cname} />` building a section of the user interface.",
                    how_it_is_used="Receives props (settings), manages local state, and returns JSX elements to draw on screen.",
                    where_it_is_used=f"Defined at line {line_no}.",
                    why_it_works="React instantiates a fiber node for this component and reconciles its Virtual DOM against the real screen.",
                    best_practices_and_pitfalls="Keep components small and focused on one job.",
                    simple_analogy=f"Think of <{cname} /> like a specialized Lego workshop or toy factory! Whenever the app calls its name, it stamps out a brand new, interactive Lego block with buttons and text.",
                    what_happens_on_screen=f"Draws the `<{cname} />` component and all of its buttons, text, and pictures on the page.",
                    what_if_removed=f"The entire `{cname}` section will disappear from the screen."
                ))

        if components:
            detected_concepts.append(f"Modular React Component Hierarchy ({', '.join(components[:4])})")

        # Async / Await and Fetch detection
        has_async = bool(re.search(r'\basync\s+function|\basync\s*\([^)]*\)\s*=>|\bawait\s+', content))
        has_fetch = bool(re.search(r'\bfetch\s*\(|\baxios\.', content))
        if has_async or has_fetch:
            detected_concepts.append("Asynchronous Data Pipelines (Promises / async-await)")
            analysis.elements.append(ElementExplanation(
                name="Async / Await Flow",
                kind="concept",
                line_number=None,
                snippet="async () => { const res = await fetch(...); }",
                what_it_is="Non-blocking asynchronous control flow pattern.",
                how_it_is_used="Pauses execution non-blockingly while network or async tasks resolve.",
                where_it_is_used="Found in data retrieval, effect handlers, or API endpoints.",
                why_it_works="Operates over JavaScript Promises yielded back to the browser's event loop.",
                best_practices_and_pitfalls="Always handle rejections using try/catch blocks.",
                simple_analogy="Think of this like ordering food at a restaurant! You place your order, sit down and chat with friends, and when the chef rings the bell ('await'), your food is ready!",
                what_happens_on_screen="Allows the app to fetch data from the internet smoothly without freezing the buttons or screen.",
                what_if_removed="The screen would freeze like ice while waiting for internet data."
            ))

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks

        # Determine Role
        if components and any("React" in f for f in detected_frameworks):
            analysis.role_in_codebase = "React View Component & Interactive UI Controller"
        elif "Express.js Backend Framework" in detected_frameworks:
            analysis.role_in_codebase = "Backend Server / API Route Controller"
        elif "Three.js 3D Engine" in detected_frameworks:
            analysis.role_in_codebase = "3D Interactive Scene & WebGL Graphic Engine"
        else:
            analysis.role_in_codebase = "JavaScript/TypeScript Logic & Module Utility"

        # Beginner Friendly Story
        analysis.beginner_story = (
            f"Imagine this file `{relative_path}` is a lively workshop in a toy factory! "
            f"{'It builds interactive React Lego blocks with buttons and cards. ' if components else 'It provides smart tools and helper calculations. '}"
            f"Whenever a user touches a button or clicks their mouse on the screen, the functions inside this file wake up, "
            f"calculate new numbers, and update the screen so the user sees instant magic!"
        )

        analysis.summary = (
            f"{self.language} module containing {len(analysis.raw_imports)} imports, {len(components)} component(s), "
            f"and {len(analysis.raw_exports)} exported symbols. "
            f"{'Built with ' + ', '.join(detected_frameworks) + '. ' if detected_frameworks else ''}"
            f"{'Uses stateful hooks: ' + ', '.join(hooks_found.keys()) + '. ' if hooks_found else ''}"
        )

        return analysis
