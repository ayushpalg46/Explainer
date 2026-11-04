"""
Cross-File Interconnection & Dependency Graph Engine for Explainer.
Maps and explains HOW and WHY files interact, resolve relative paths, and detects architectural couplings.
"""
import os
from typing import Dict, List, Set, Tuple, Any, Optional
from explainer.core.parsers.base import FileAnalysis, FileConnection


class InterconnectionGraph:
    def __init__(self, analyses: List[FileAnalysis]):
        self.analyses = analyses
        self.file_map: Dict[str, FileAnalysis] = {
            self._norm_path(a.path): a for a in analyses
        }
        self.edges: List[Dict[str, Any]] = []

    def _norm_path(self, p: str) -> str:
        return p.replace("\\", "/").lstrip("./")

    def build_graph(self):
        """
        Resolves outgoing connections from all files against actual existing project files
        and populates both outgoing and incoming connections with elaborated rationale.
        """
        for source_path, source_analysis in self.file_map.items():
            resolved_outgoing: List[FileConnection] = []

            for conn in source_analysis.outgoing_connections:
                resolved_target = self._resolve_target_path(source_path, conn.target_file)
                
                if resolved_target and resolved_target in self.file_map:
                    target_analysis = self.file_map[resolved_target]
                    
                    # Elaborate WHY and HOW based on source & target types
                    elaborated_how, elaborated_why = self._elaborate_relationship(
                        source_analysis, target_analysis, conn.relation_type, conn.mechanism
                    )
                    
                    final_conn = FileConnection(
                        source_file=source_path,
                        target_file=resolved_target,
                        relation_type=conn.relation_type,
                        mechanism=elaborated_how,
                        rationale=elaborated_why,
                        confidence=1.0
                    )
                    resolved_outgoing.append(final_conn)

                    # Add reciprocal incoming connection on target file
                    incoming_conn = FileConnection(
                        source_file=source_path,
                        target_file=resolved_target,
                        relation_type=f"depended_on_by ({conn.relation_type})",
                        mechanism=elaborated_how,
                        rationale=f"Consumed by '{source_analysis.filename}' to fulfill: {elaborated_why}",
                        confidence=1.0
                    )
                    target_analysis.incoming_connections.append(incoming_conn)

                    self.edges.append({
                        "from": source_path,
                        "to": resolved_target,
                        "type": conn.relation_type,
                        "how": elaborated_how,
                        "why": elaborated_why
                    })
                else:
                    # Connection is external package or unresolvable
                    resolved_outgoing.append(conn)

            source_analysis.outgoing_connections = resolved_outgoing

    def _resolve_target_path(self, source_path: str, raw_target: str) -> Optional[str]:
        """Resolves relative paths, extensionless imports, and index files."""
        clean_target = raw_target.strip("'\"`")
        if not clean_target.startswith((".", "/")):
            # Check if matching any file by filename
            basename = clean_target.split("/")[-1]
            matches = [p for p in self.file_map if p.endswith(basename) or p.endswith(f"{basename}.js") or p.endswith(f"{basename}.py")]
            return matches[0] if matches else None

        source_dir = os.path.dirname(source_path)
        combined = os.path.normpath(os.path.join(source_dir, clean_target)).replace("\\", "/").lstrip("./")

        # 1. Exact match
        if combined in self.file_map:
            return combined

        # 2. Try common extensions
        for ext in (".js", ".jsx", ".ts", ".tsx", ".py", ".rs", ".java", ".go", ".css", ".html", ".sh"):
            candidate = f"{combined}{ext}"
            if candidate in self.file_map:
                return candidate

        # 3. Try index files inside directory
        for idx in ("index.js", "index.ts", "index.jsx", "index.tsx", "mod.rs", "__init__.py"):
            candidate = f"{combined}/{idx}".replace("//", "/")
            if candidate in self.file_map:
                return candidate

        return None

    def _elaborate_relationship(
        self, source: FileAnalysis, target: FileAnalysis, rel_type: str, raw_mechanism: str
    ) -> Tuple[str, str]:
        """Synthesizes deep architectural explanations for why two files interact."""
        s_lang = source.language
        t_lang = target.language

        # HTML -> CSS
        if s_lang == "HTML" and t_lang == "CSS":
            how = f"Linked via `<link rel='stylesheet' href='{target.filename}'>` in HTML `<head>`"
            why = (
                f"Separates structural markup from presentation rules. '{target.filename}' supplies the color palette, "
                f"typography hierarchy, and responsive layout classes needed to render '{source.filename}' visually."
            )
            return how, why

        # HTML -> JS / JSX
        if s_lang == "HTML" and ("JavaScript" in t_lang or "TypeScript" in t_lang):
            how = f"Script invocation via `<script src='{target.filename}'>`"
            why = (
                f"Injects dynamic client-side interactivity, event listeners, or bootstraps the single-page application "
                f"by mounting component trees into '{source.filename}' DOM nodes (e.g. `#root`)."
            )
            return how, why

        # JS / JSX -> JS / JSX Component or Utility
        if ("JavaScript" in s_lang or "TypeScript" in s_lang) and ("JavaScript" in t_lang or "TypeScript" in t_lang):
            how = f"Static module dependency import: `{raw_mechanism}`"
            why = (
                f"Decomposes monolithic UI logic into reusable functional units. '{source.filename}' delegates specific "
                f"rendering, state calculations, or data fetching duties to '{target.filename}'."
            )
            return how, why

        # Dockerfile -> Source file
        if source.language == "Dockerfile":
            how = f"Filesystem injection directive: `{raw_mechanism}`"
            why = (
                f"Transfers essential host dependencies, build manifests, or binaries ('{target.filename}') "
                f"into the isolated container image filesystem for compilation or deployment."
            )
            return how, why

        # Shell -> File
        if source.language == "Shell Script":
            how = f"Process invocation or environment sourcing: `{raw_mechanism}`"
            why = (
                f"Orchestrates project automation pipelines, loading configurations or executing '{target.filename}' "
                f"as a sequential build/deployment step."
            )
            return how, why

        # Python -> Python
        if s_lang == "Python" and t_lang == "Python":
            how = f"Module import hierarchy: `{raw_mechanism}`"
            why = (
                f"Encapsulates domain responsibilities. '{source.filename}' accesses helper functions, data schemas, "
                f"or business services exported by '{target.filename}'."
            )
            return how, why

        # Generic fallback
        how = raw_mechanism or f"{s_lang} consumes {t_lang}"
        why = f"Integrates capabilities of '{target.filename}' to satisfy computational or structural requirements of '{source.filename}'."
        return how, why

    def get_top_central_files(self) -> List[Tuple[str, int]]:
        """Finds the most relied-upon files in the codebase (highest in-degree)."""
        counts = [(a.filename, len(a.incoming_connections)) for a in self.analyses]
        return sorted(counts, key=lambda x: -x[1])
