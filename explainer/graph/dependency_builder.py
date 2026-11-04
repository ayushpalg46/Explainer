from pathlib import Path
from typing import Dict, List, Optional, Tuple
from ..models import FileAnalysis, FileInterconnection


class DependencyGraphBuilder:
    def __init__(self, files: Dict[str, FileAnalysis]):
        self.files = files
        # Index files by stem and lowercase relative path for robust matching
        self._by_path = {f.relative_path.lower(): f.relative_path for f in files.values()}
        self._by_stem: Dict[str, List[str]] = {}
        for rel_path in files.keys():
            stem = Path(rel_path).stem.lower()
            self._by_stem.setdefault(stem, []).append(rel_path)

    def build_interconnections(self) -> List[FileInterconnection]:
        interconnections: List[FileInterconnection] = []

        for src_path, src_analysis in self.files.items():
            src_p = Path(src_path)
            src_dir = src_p.parent

            for raw_ref in src_analysis.raw_imports:
                target_rel = self._resolve_target(src_dir, raw_ref)
                if not target_rel or target_rel == src_path:
                    continue

                relation_type, how, why = self._determine_mechanics(
                    src_analysis.language, self.files[target_rel].language, src_path, target_rel, raw_ref
                )

                conn = FileInterconnection(
                    source_file=src_path,
                    target_file=target_rel,
                    relation_type=relation_type,
                    how_it_works=how,
                    why_it_works=why,
                    code_reference=raw_ref
                )

                interconnections.append(conn)
                src_analysis.outbound_connections.append(conn)
                self.files[target_rel].inbound_connections.append(conn)

        return interconnections

    def _resolve_target(self, src_dir: Path, raw_ref: str) -> Optional[str]:
        # Clean query strings / hashes
        clean_ref = raw_ref.split("?")[0].split("#")[0].strip()
        if clean_ref.startswith("/") or clean_ref.startswith("./") or clean_ref.startswith("../"):
            # Relative resolution
            candidate = (src_dir / clean_ref).as_posix().lstrip("./")
            # Exact match
            if candidate.lower() in self._by_path:
                return self._by_path[candidate.lower()]
            # Try with extensions
            for ext in [".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".py", ".rs", ".go", "/index.js", "/index.ts", "/index.tsx"]:
                cand_ext = candidate + ext
                if cand_ext.lower() in self._by_path:
                    return self._by_path[cand_ext.lower()]

        # Try matching by filename stem
        stem = Path(clean_ref).stem.lower()
        if stem in self._by_stem and len(self._by_stem[stem]) == 1:
            return self._by_stem[stem][0]

        return None

    def _determine_mechanics(
        self,
        src_lang: str,
        target_lang: str,
        src_file: str,
        target_file: str,
        raw_ref: str
    ) -> Tuple[str, str, str]:
        # HTML -> CSS
        if "HTML" in src_lang and "CSS" in target_lang:
            return (
                "styles",
                f"The HTML document references `{target_file}` via `<link rel='stylesheet' href='{raw_ref}'>`. "
                f"The browser engine dispatches an HTTP request, parses the CSS rules, and constructs the CSSOM (CSS Object Model).",
                f"Applies visual presentation, responsive layouts, color themes, and typography to the DOM nodes defined in `{src_file}`."
            )
        # HTML -> JS
        elif "HTML" in src_lang and ("JavaScript" in target_lang or "TypeScript" in target_lang):
            return (
                "scripts",
                f"The HTML file loads `{target_file}` via `<script src='{raw_ref}'>`. "
                f"The browser script engine compiles and executes the bundle, attaching event listeners and mounting dynamic views into the DOM.",
                f"Transforms the static HTML scaffold into an interactive application, initializing state management and dynamic UI lifecycle."
            )
        # JS/TS -> JS/TS Component or Utility
        elif ("JavaScript" in src_lang or "TypeScript" in src_lang) and ("JavaScript" in target_lang or "TypeScript" in target_lang):
            return (
                "imports",
                f"`{src_file}` imports symbols from `{target_file}` using module syntax `{raw_ref}`. "
                f"The bundler or module loader resolves the file export dictionary and binds exported components or functions into the caller's local scope.",
                f"Enforces clean separation of concerns: `{target_file}` encapsulates reusable UI or business logic, allowing `{src_file}` to compose it without code duplication."
            )
        # JS/TS -> CSS
        elif ("JavaScript" in src_lang or "TypeScript" in src_lang) and "CSS" in target_lang:
            return (
                "styles",
                f"`{src_file}` imports stylesheet `{target_file}` directly. "
                f"The bundler (e.g. Vite or Webpack) injects the stylesheet into a `<style>` tag in the document `<head>` during runtime hydration.",
                f"Enables component-scoped or module-level styling, ensuring styling rules are automatically bundled whenever the component is used."
            )
        # Python -> Python
        elif "Python" in src_lang and "Python" in target_lang:
            return (
                "imports",
                f"`{src_file}` imports module `{target_file}` via `import` or `from ... import`. "
                f"Python's import system searches `sys.modules`, compiles bytecode if needed, and binds the module namespace.",
                f"Promotes modular architecture by delegating domain services, helper routines, or data models to dedicated modules."
            )
        # Docker -> Source
        elif "Docker" in src_lang:
            return (
                "docker_builds",
                f"The Dockerfile copies `{target_file}` into the container filesystem via `COPY` or `ADD`. "
                f"Creates an immutable container layer containing the code needed for runtime execution.",
                f"Isolates the application runtime environment, ensuring identical deployment regardless of host OS dependencies."
            )
        # Shell -> Script
        elif "Shell" in src_lang:
            return (
                "executes",
                f"The shell script executes or sources `{target_file}`. "
                f"The shell forks a subshell or evaluates variables in the current environment.",
                f"Orchestrates multi-step build, migration, or environment bootstrapping pipelines."
            )
        else:
            return (
                "references",
                f"`{src_file}` directly references `{target_file}` via `{raw_ref}`.",
                f"Establishes a structural dependency required for project execution and data flow."
            )
