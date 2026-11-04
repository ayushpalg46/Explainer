"""
JavaScript, TypeScript, JSX, and TSX Parser for Explainer.
Analyzes imports/exports, React components, hooks, state, props, JSX nodes, API calls, and lifecycle patterns.
"""
import re
from typing import List, Dict, Any, Set
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class JSTSJSXFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]

    @property
    def language_name(self) -> str:
        return "JavaScript / TypeScript"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]
        ext = "." + filename.split(".")[-1] if "." in filename else ""

        is_ts = ext in (".ts", ".tsx")
        is_jsx = ext in (".jsx", ".tsx") or "import React" in content or "<" in content and "/>" in content

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["TypeScript" if is_ts else "JavaScript (ES6+)"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        # 1. Parse ES Module Imports
        # import defaultExport, { namedA, namedB as aliasB } from 'module_or_path';
        esm_import_pattern = re.compile(
            r"import\s+(?:(?:type\s+)?([a-zA-Z0-9_$,\s{}*]+)\s+from\s+)?['\"]([^'\"]+)['\"];?"
        )
        for m in esm_import_pattern.finditer(content):
            imported_symbols = (m.group(1) or "*").strip()
            module_path = m.group(2).strip()
            line_num = content[:m.start()].count("\n") + 1

            imports.append(FileImport(
                source=imported_symbols,
                target=module_path,
                line=line_num,
                import_type="esm"
            ))

            # If it's a relative path (local file)
            if module_path.startswith((".", "/")):
                connections.append(FileConnection(
                    source_file=filepath,
                    target_file=module_path,
                    relation_type="imports_code",
                    mechanism=f"ESM Import: import {imported_symbols} from '{module_path}'",
                    rationale="Imports components, utility functions, types, or services to compose application functionality."
                ))
            else:
                # External dependency
                self._classify_external_package(module_path, tech_stack)

        # 2. Parse CommonJS requires
        cjs_pattern = re.compile(r"(?:const|let|var)\s+([a-zA-Z0-9_{}\s,]+)\s*=\s*require\(['\"]([^'\"]+)['\"]\)")
        for m in cjs_pattern.finditer(content):
            var_name = m.group(1).strip()
            mod_path = m.group(2).strip()
            line_num = content[:m.start()].count("\n") + 1
            imports.append(FileImport(source=var_name, target=mod_path, line=line_num, import_type="commonjs"))
            if mod_path.startswith((".", "/")):
                connections.append(FileConnection(
                    source_file=filepath,
                    target_file=mod_path,
                    relation_type="imports_code",
                    mechanism=f"CommonJS require: require('{mod_path}')",
                    rationale="Synchronously loads module export object."
                ))
            else:
                self._classify_external_package(mod_path, tech_stack)

        # 3. Parse Exports
        # export default function/class/identifier
        export_default_match = re.search(r"export\s+default\s+(?:function\s+([a-zA-Z0-9_]+)|class\s+([a-zA-Z0-9_]+)|([a-zA-Z0-9_]+))", content)
        if export_default_match:
            exp_name = export_default_match.group(1) or export_default_match.group(2) or export_default_match.group(3) or "default"
            line_num = content[:export_default_match.start()].count("\n") + 1
            exports.append(FileExport(name=exp_name, kind="default_export", line=line_num))

        # export const/function/class named exports
        named_export_pattern = re.finditer(r"export\s+(?:const|let|var|function|class|interface|type)\s+([a-zA-Z0-9_]+)", content)
        for m in named_export_pattern:
            exp_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            exports.append(FileExport(name=exp_name, kind="named_export", line=line_num))

        # 4. React Components & Functional Declarations
        react_components: List[Dict[str, Any]] = []
        component_candidates = re.finditer(
            r"(?:export\s+)?(?:default\s+)?(?:function|const)\s+([A-Z][a-zA-Z0-9_]*)\s*(?:=\s*(?:\([^)]*\)|[a-zA-Z0-9_]+)\s*=>|\([^)]*\))",
            content
        )
        for m in component_candidates:
            comp_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            react_components.append({"name": comp_name, "line": line_num})
            symbols.append(FileSymbol(
                name=comp_name,
                kind="react_component" if is_jsx else "class_or_factory",
                line=line_num,
                signature=f"Component <{comp_name} />",
                description=f"UI Component rendering visual elements and managing local presentation logic."
            ))

        if react_components:
            tech_stack.append("React")
            concepts.append(f"React Component Architecture ({len(react_components)} component(s): {', '.join(c['name'] for c in react_components)})")

        # 5. React Hooks Detection
        hooks_found = re.findall(r"\b(use[A-Z][a-zA-Z0-9_]+)\b", content)
        unique_hooks = sorted(list(set(hooks_found)))
        if unique_hooks:
            concepts.append(f"React Hooks Flow: {', '.join(unique_hooks)}")
            for h in unique_hooks:
                hook_desc = self._get_hook_explanation(h)
                symbols.append(FileSymbol(
                    name=h,
                    kind="react_hook",
                    line=1,
                    description=hook_desc
                ))

        # 6. State Management & Side Effects
        has_state = "useState" in unique_hooks
        has_effect = "useEffect" in unique_hooks
        has_context = "useContext" in unique_hooks or "createContext" in content

        if has_state:
            concepts.append("Reactive Local State Management (useState)")
        if has_effect:
            concepts.append("Component Lifecycle & Side Effects Pipeline (useEffect)")
        if has_context:
            concepts.append("React Context Shared State Pipeline")

        # 7. Network / API Calls
        api_calls = re.findall(r"(?:fetch|axios\.(?:get|post|put|delete|patch))\s*\(\s*['\"`]([^'\"`]+)['\"`]", content)
        if api_calls:
            concepts.append(f"Client-Side Remote API Integration ({len(api_calls)} endpoint(s) called)")
            for endpoint in api_calls:
                connections.append(FileConnection(
                    source_file=filepath,
                    target_file=endpoint,
                    relation_type="calls_api",
                    mechanism=f"HTTP API Request to '{endpoint}'",
                    rationale="Transfers business data between client interface and backend API service."
                ))

        # 8. JSX Rendered Tags
        if is_jsx:
            jsx_tags = re.findall(r"<([A-Z][a-zA-Z0-9_.]*)", content)
            unique_jsx_tags = sorted(list(set(jsx_tags)))
            if unique_jsx_tags:
                concepts.append(f"Component Hierarchy Compositions: {', '.join(f'<{t}>' for t in unique_jsx_tags[:8])}")

        # 9. TypeScript Interfaces & Types
        if is_ts:
            ts_types = re.findall(r"(?:interface|type)\s+([A-Z][a-zA-Z0-9_]+)", content)
            if ts_types:
                concepts.append(f"Strong Typing Contracts ({len(ts_types)} type/interface definitions)")
                for t_name in ts_types[:10]:
                    symbols.append(FileSymbol(
                        name=t_name,
                        kind="typescript_type",
                        line=1,
                        description=f"TypeScript data contract defining shape and constraints for {t_name}."
                    ))

        # 10. Security & Quality Practices
        if "dangerouslySetInnerHTML" in content:
            security_and_practices.append("Caution: Uses `dangerouslySetInnerHTML`. Ensure input is sanitized to prevent Cross-Site Scripting (XSS).")
        if "eval(" in content:
            security_and_practices.append("Warning: Avoid `eval()` usage for code execution due to injection vulnerabilities.")
        if "any" in content and is_ts:
            any_count = len(re.findall(r":\s*any\b", content))
            if any_count > 3:
                security_and_practices.append(f"Found {any_count} usages of `: any`. Refine types for stricter compiler safety.")

        # Components Breakdown
        components_breakdown.append({
            "section": "Imported Dependencies & Modules",
            "details": f"Imports {len(imports)} modules ({len([i for i in imports if i.target.startswith('.')])} local project files, {len([i for i in imports if not i.target.startswith('.')])} external libraries)."
        })
        if react_components:
            components_breakdown.append({
                "section": "UI Components & Render Tree",
                "details": f"Implements component units: {', '.join(c['name'] for c in react_components)} with lifecycle and state hooks."
            })
        if exports:
            components_breakdown.append({
                "section": "Public API & Exports",
                "details": f"Exports {len(exports)} symbols: {', '.join(e.name for e in exports)}."
            })

        # Summary and Role
        summary = (
            f"{'TypeScript' if is_ts else 'JavaScript'} {'JSX' if is_jsx else 'module'} ({filename}) containing {loc} lines. "
        )
        if react_components:
            summary += f"Defines React component(s) {', '.join(c['name'] for c in react_components)} handling UI presentation and reactive state."
            arch_role = "Frontend UI Component / View Logic"
        elif "express" in content.lower() or "router" in content.lower():
            summary += "Configures HTTP routing, middleware, and request/response handlers."
            arch_role = "Backend Controller / HTTP Router"
        elif exports:
            summary += f"Provides reusable utility functions, state managers, or data contracts."
            arch_role = "Business Logic / Service Utility"
        else:
            summary += "Executable application script or entry point."
            arch_role = "Script / Entrypoint"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=ext,
            language="TypeScript" if is_ts else "JavaScript",
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
            tags=["javascript", "typescript", "frontend" if is_jsx else "module"]
        )

    def _classify_external_package(self, pkg: str, stack: List[str]):
        pkg_lower = pkg.lower()
        if "react" in pkg_lower:
            stack.append("React")
        elif "vue" in pkg_lower:
            stack.append("Vue.js")
        elif "next" in pkg_lower:
            stack.append("Next.js")
        elif "redux" in pkg_lower or "zustand" in pkg_lower:
            stack.append("State Management")
        elif "axios" in pkg_lower:
            stack.append("Axios HTTP Client")
        elif "tailwindcss" in pkg_lower:
            stack.append("Tailwind CSS")
        elif "express" in pkg_lower:
            stack.append("Express.js")
        elif "lodash" in pkg_lower:
            stack.append("Lodash Utilities")
        elif "three" in pkg_lower:
            stack.append("Three.js 3D Engine")
        elif "gsap" in pkg_lower:
            stack.append("GSAP Animation Library")

    def _get_hook_explanation(self, hook: str) -> str:
        hooks_dict = {
            "useState": "Manages reactive state variable with automatic component re-rendering upon value changes.",
            "useEffect": "Executes asynchronous side-effects (data fetching, DOM mutations, subscriptions) after rendering.",
            "useContext": "Subscribes to React Context to access global data without prop drilling.",
            "useReducer": "Manages complex state transitions using a Redux-like action reducer pattern.",
            "useCallback": "Memoizes callback functions to prevent unnecessary child re-renders on parent updates.",
            "useMemo": "Caches the result of an expensive calculation between renders.",
            "useRef": "Preserves a mutable reference across renders without triggering a re-render cycle.",
            "useLayoutEffect": "Fires synchronously immediately after DOM mutations before browser paint."
        }
        return hooks_dict.get(hook, f"React hook `{hook}` managing stateful or lifecycle behavior.")
