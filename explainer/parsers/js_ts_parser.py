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

        # Extract Imports:
        # 1. ES6 import ... from '...'
        import_matches = re.finditer(r'import\s+(?:(?:(?:[a-zA-Z0-9_{}\s*,*]+)\s+from\s+)?["\']([^"\']+)["\'])', content)
        for m in import_matches:
            analysis.raw_imports.append(m.group(1))

        # 2. CommonJS require('...')
        require_matches = re.finditer(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
        for m in require_matches:
            if m.group(1) not in analysis.raw_imports:
                analysis.raw_imports.append(m.group(1))

        # 3. Dynamic import('...')
        dyn_import_matches = re.finditer(r'import\s*\(\s*["\']([^"\']+)["\']\s*\)', content)
        for m in dyn_import_matches:
            if m.group(1) not in analysis.raw_imports:
                analysis.raw_imports.append(m.group(1))

        # Extract Exports:
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
                    best_practices_and_pitfalls=kb.get("best_practices", "Follow the Rules of Hooks: call only at the top level.")
                ))

        if hooks_found:
            detected_concepts.append(f"React State & Hooks Architecture ({', '.join(hooks_found.keys())})")

        # React Components Detection
        # Functional components e.g. function MyComponent() or const MyComponent = () =>
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
                    snippet=f"function {cname}(...) {{ ... return <...> }}",
                    what_it_is=f"Declarative React UI component `<{cname} />` encapsulating presentation and interactive behavior.",
                    how_it_is_used="Receives props, maintains local state, and returns a JSX Virtual DOM subtree.",
                    where_it_is_used=f"Defined at line {line_no}.",
                    why_it_works="React instantiates a fiber node for this component, executing render and reconciliation algorithms whenever inputs change.",
                    best_practices_and_pitfalls="Keep components focused on a single UI responsibility. Extract pure business logic into custom hooks or utility helpers."
                ))

        if components:
            detected_concepts.append(f"Modular React Component Hierarchy ({', '.join(components[:4])})")

        # Async / Await and Fetch detection
        has_async = bool(re.search(r'\basync\s+function|\basync\s*\([^)]*\)\s*=>|\bawait\s+', content))
        has_fetch = bool(re.search(r'\bfetch\s*\(|\baxios\.', content))
        if has_async or has_fetch:
            detected_concepts.append("Asynchronous Data Pipelines (Promises / async-await)")
            kb = JS_REACT_KNOWLEDGE.get("async_await", {})
            analysis.elements.append(ElementExplanation(
                name="Async / Await Flow",
                kind="concept",
                line_number=None,
                snippet="async () => { const res = await fetch(...); }",
                what_it_is=kb.get("what_it_is", "Non-blocking asynchronous control flow pattern."),
                how_it_is_used="Pauses execution non-blockingly while network or async tasks resolve.",
                where_it_is_used="Found in data retrieval, effect handlers, or API endpoints.",
                why_it_works=kb.get("why_it_works", "Operates over JavaScript Promises yielded back to the browser's event loop."),
                best_practices_and_pitfalls=kb.get("best_practices", "Always handle rejections using try/catch blocks.")
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

        analysis.summary = (
            f"{self.language} module containing {len(analysis.raw_imports)} external/internal import references "
            f"and exporting {len(analysis.raw_exports)} symbol(s) ({', '.join(analysis.raw_exports[:3]) if analysis.raw_exports else 'internal module'}). "
            f"{f'Declares {len(components)} UI component(s): {', '.join(components[:3])}. ' if components else ''}"
            f"{f'Utilizes {len(hooks_found)} React hook type(s): {', '.join(hooks_found.keys())}. ' if hooks_found else ''}"
            f"{'Features asynchronous promise and fetch workflows. ' if has_async or has_fetch else ''}"
        )

        if "Three.js 3D Engine" in detected_frameworks or "GSAP Animation Library" in detected_frameworks:
            analysis.animations_and_interactions = (
                f"Interactive animation integration detected: "
                f"{'Three.js 3D render loop & viewport controls. ' if 'Three.js 3D Engine' in detected_frameworks else ''}"
                f"{'GSAP timeline sequences & scroll triggers. ' if 'GSAP Animation Library' in detected_frameworks else ''}"
            )

        return analysis
