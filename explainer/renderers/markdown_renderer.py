from pathlib import Path
from typing import Dict, List
from ..models import CodebaseAnalysis, FileAnalysis


class MarkdownRenderer:
    def render(self, analysis: CodebaseAnalysis, output_path: str) -> str:
        """Renders a single consolidated Markdown report."""
        content = self._build_full_markdown(analysis)
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(content, encoding="utf-8")
        return str(out_p)

    def render_multi_file_dossier(self, analysis: CodebaseAnalysis, output_dir: str) -> Dict[str, str]:
        """
        Renders a structured folder containing:
        - INDEX.md: Architecture, Lego Big Picture, Tech Stack, Folder Roles, Interconnection Graph, and File Index.
        - FULL_REPORT.md: The complete monolithic dossier.
        - files/<relative_path>.md: Dedicated, exhaustive explanation for each file individually.
        """
        out_dir = Path(output_dir).resolve()
        files_dir = out_dir / "files"
        if files_dir.exists():
            # Clean old markdown files so deleted or renamed source files do not linger as stale artifacts
            for old_md in files_dir.glob("*.md"):
                try:
                    old_md.unlink()
                except Exception:
                    pass
        files_dir.mkdir(parents=True, exist_ok=True)

        generated_files = {}

        # 1. Render individual file explanations
        for rel_path, fa in sorted(analysis.files.items()):
            file_md = self._build_single_file_markdown(rel_path, fa, analysis)
            safe_name = rel_path.replace("/", "_").replace("\\", "_") + ".md"
            file_path = files_dir / safe_name
            file_path.write_text(file_md, encoding="utf-8")
            generated_files[rel_path] = str(file_path)

        # 2. Render INDEX.md
        index_md = self._build_index_markdown(analysis, generated_files)
        index_path = out_dir / "INDEX.md"
        index_path.write_text(index_md, encoding="utf-8")
        generated_files["__index__"] = str(index_path)

        # 3. Render FULL_REPORT.md
        full_md = self._build_full_markdown(analysis)
        full_path = out_dir / "FULL_REPORT.md"
        full_path.write_text(full_md, encoding="utf-8")
        generated_files["__full__"] = str(full_path)

        return generated_files

    def _build_index_markdown(self, analysis: CodebaseAnalysis, file_map: Dict[str, str]) -> str:
        out = []
        out.append(f"# Codebase Architecture & Technical Index: `{analysis.project_name}`\n")
        out.append(f"> **Engine Used**: {analysis.engine_used}  \n")
        out.append(f"> **Scope**: {analysis.total_files} files | {analysis.total_lines:,} lines of code | {len(analysis.interconnections)} cross-file interconnections\n")
        out.append("---\n\n")

        # 0. Beginner Castle Story
        if analysis.beginner_codebase_story:
            out.append("## 🏰 1. The Big Castle Story (Explain Like I'm 4 Years Old)\n")
            out.append(f"> {analysis.beginner_codebase_story}\n\n")
            out.append("---\n\n")

        # 1. Architecture Style
        out.append("## 2. System Architecture & Tech Stack\n")
        out.append(f"### Architectural Style: **{analysis.architecture_style}**\n")
        out.append(f"{analysis.architecture_summary}\n\n")

        if analysis.ai_architecture_critique and analysis.ai_architecture_critique != analysis.architecture_summary:
            model_lbl = analysis.ai_model_name or "Local AI Model"
            out.append(f"### 🧠 Neural AI Architectural Review (`{model_lbl}`)\n")
            out.append(f"{analysis.ai_architecture_critique}\n\n")

        out.append("### Technology Compatibility Analysis\n")
        out.append(f"{analysis.tech_stack.compatibility_analysis}\n\n")

        out.append("| Category | Detected Technologies & Tooling |\n")
        out.append("| :--- | :--- |\n")
        langs_str = ", ".join([f"`{k}` ({v} files)" for k, v in analysis.tech_stack.languages.items()])
        out.append(f"| **Languages** | {langs_str} |\n")
        if analysis.tech_stack.frameworks:
            out.append(f"| **Frameworks** | {', '.join([f'`{f}`' for f in analysis.tech_stack.frameworks])} |\n")
        if analysis.tech_stack.build_tools:
            out.append(f"| **Build Tools** | {', '.join([f'`{b}`' for b in analysis.tech_stack.build_tools])} |\n")
        if analysis.tech_stack.package_managers:
            out.append(f"| **Package Managers** | {', '.join([f'`{p}`' for p in analysis.tech_stack.package_managers])} |\n")
        if analysis.tech_stack.runtimes:
            out.append(f"| **Runtimes** | {', '.join([f'`{r}`' for r in analysis.tech_stack.runtimes])} |\n")
        out.append("\n---\n\n")

        # 2. Directory Roles
        out.append("## 3. Directory Subsystem Roles\n")
        out.append("| Directory / Subsystem | Purpose & Architectural Role |\n")
        out.append("| :--- | :--- |\n")
        for folder, role in sorted(analysis.folder_roles.items()):
            out.append(f"| `{folder}/` | {role} |\n")
        out.append("\n---\n\n")

        # 3. Interconnection Graph
        out.append("## 4. Cross-File Interconnection Graph & Mechanics\n")
        if analysis.interconnections:
            out.append("```mermaid\ngraph LR\n")
            for conn in analysis.interconnections:
                src_safe = conn.source_file.replace("/", "_").replace(".", "_").replace("-", "_")
                tgt_safe = conn.target_file.replace("/", "_").replace(".", "_").replace("-", "_")
                out.append(f"    {src_safe}[\"{conn.source_file}\"] -->|{conn.relation_type}| {tgt_safe}[\"{conn.target_file}\"]\n")
            out.append("```\n\n")

            out.append("### Detailed Interconnection Rationale (How & Why They Work)\n\n")
            for conn in analysis.interconnections:
                out.append(f"#### 🔗 `{conn.source_file}` ➔ `{conn.target_file}` (`{conn.relation_type}`)\n")
                if conn.code_reference:
                    out.append(f"- **Code Reference**: `{conn.code_reference}`\n")
                out.append(f"- **How It Works**: {conn.how_it_works}\n")
                out.append(f"- **Why It Works**: {conn.why_it_works}\n\n")
        out.append("---\n\n")

        # 4. Table of All Files with Links to Dedicated File Explanations
        out.append("## 5. File-by-File Detailed Explanation Catalog\n")
        out.append("Each file below has its own dedicated, beginner-friendly analysis document:\n\n")
        out.append("| File | Language | Lines | Role | Individual Explanation Link |\n")
        out.append("| :--- | :--- | :---: | :--- | :---: |\n")
        for rel_path, fa in sorted(analysis.files.items()):
            safe_name = rel_path.replace("/", "_").replace("\\", "_") + ".md"
            link = f"files/{safe_name}"
            out.append(f"| **`{rel_path}`** | `{fa.language}` | {fa.line_count} | {fa.role_in_codebase} | [📄 View Explanation]({link}) |\n")
        out.append("\n> You can also view the complete consolidated dossier in [FULL_REPORT.md](FULL_REPORT.md) or launch the interactive GUI in [dashboard.html](dashboard.html).\n")

        return "".join(out)

    def _build_single_file_markdown(self, rel_path: str, fa: FileAnalysis, analysis: CodebaseAnalysis) -> str:
        out = []
        out.append(f"# Deep File Explanation: `{rel_path}`\n")
        out.append(f"> **Project**: `{analysis.project_name}` | **Language**: `{fa.language}` | **Size**: {fa.line_count} lines ({fa.file_size_bytes:,} bytes)\n")
        out.append(f"> [⬅ Back to Main Index](../INDEX.md) | [🌐 Open Interactive GUI Dashboard](../dashboard.html)\n\n")
        out.append("──────\n\n")

        # 1. Big Picture Story
        story = fa.beginner_story or f"This {fa.language} file `{rel_path}` acts like a dedicated tool in the project workshop, fulfilling the role: {fa.role_in_codebase}."
        out.append("#### 🧸 1. The Big Picture Story (What is this code?)\n\n")
        out.append(f'│ "{story}"\n')
        out.append("──────\n\n")

        # Neural AI Breakdown (if in AI mode)
        if fa.ai_insights:
            model_badge = fa.ai_model_used or analysis.ai_model_name or "Local AI Model"
            out.append(f"### 🧠 Neural AI Deep Code Analysis (`{model_badge}`)\n\n")
            out.append(f"{fa.ai_insights}\n\n")
            out.append("──────\n\n")

        # 2. Line-by-Line & Word-by-Word Breakdown
        out.append("#### 🔍 2. Line-by-Line & Word-by-Word Breakdown\n\n")
        if fa.elements:
            for el in fa.elements:
                line_str = f"Line {el.line_number}" if el.line_number is not None else "Declaration"
                snippet_line = (el.snippet or el.name).strip()
                out.append(f"#### {line_str}: {snippet_line}\n\n")

                out.append(f"• What is written?: {el.what_it_is}\n")

                if el.words_breakdown:
                    out.append("• What does every word mean?:\n")
                    for w, meaning in el.words_breakdown.items():
                        out.append(f"    • {w}: {meaning}\n")

                if el.simple_analogy:
                    out.append(f"• 🧸 4-Year-Old Analogy: {el.simple_analogy}\n")

                screen_effect = el.what_happens_on_screen or "Executes instructions inside computer memory."
                out.append(f"• 🖥️ What happens on screen?: {screen_effect}\n")

                if el.interconnection_note:
                    out.append("• 🔗 Interconnection with other files:\n")
                    for conn in el.interconnection_note.strip().splitlines():
                        conn_clean = conn.strip().lstrip("•-* ")
                        if conn_clean:
                            out.append(f"    • {conn_clean}\n")

                if el.what_if_removed:
                    out.append(f"• 💥 What breaks if deleted?: {el.what_if_removed}\n")

                out.append("──────\n")
        else:
            out.append("• No parsed lines in this file.\n──────\n")

        # 3. Cross-File Dependencies Summary
        out.append("\n### 🔗 3. Cross-File Dependencies & Friendship Map\n")
        if fa.outbound_connections or fa.inbound_connections:
            if fa.outbound_connections:
                out.append("#### Outbound Connections (Files this file depends on)\n")
                for outb in fa.outbound_connections:
                    out.append(f"- ➡️ **Depends on** `{outb.target_file}` (`{outb.relation_type}`)\n")
                    out.append(f"  - **How It Works**: {outb.how_it_works}\n")
                    out.append(f"  - **Why It Works**: {outb.why_it_works}\n")
                out.append("\n")
            if fa.inbound_connections:
                out.append("#### Inbound Connections (Files that depend on this file)\n")
                for inb in fa.inbound_connections:
                    out.append(f"- ⬅️ **Referenced by** `{inb.source_file}` (`{inb.relation_type}`)\n")
                    out.append(f"  - **How It Works**: {inb.how_it_works}\n")
                    out.append(f"  - **Why It Works**: {inb.why_it_works}\n")
                out.append("\n")
        else:
            out.append("*Isolated or standalone file with no direct internal codebase dependencies.*\n\n")

        out.append("──────\n")
        out.append(f"> [⬅ Back to Main Index](../INDEX.md)\n")
        return "".join(out)

    def _build_full_markdown(self, analysis: CodebaseAnalysis) -> str:
        out = []
        out.append(f"# Comprehensive Codebase & Architecture Dossier: `{analysis.project_name}`\n")
        out.append(f"> **Engine Used**: {analysis.engine_used}  \n")
        out.append(f"> **Scope**: {analysis.total_files} files | {analysis.total_lines:,} lines of code | {len(analysis.interconnections)} interconnections\n")
        out.append("---\n")

        if analysis.beginner_codebase_story:
            out.append("## 🏰 1. The Big Castle Story (Explain Like I'm 4 Years Old)\n")
            out.append(f"> {analysis.beginner_codebase_story}\n\n---\n\n")

        # 1. Architecture & Tech Stack
        out.append("## 2. Architecture & Tech Stack Ecosystem\n")
        out.append(f"### Architectural Style: **{analysis.architecture_style}**\n")
        out.append(f"{analysis.architecture_summary}\n\n")

        if analysis.ai_architecture_critique and analysis.ai_architecture_critique != analysis.architecture_summary:
            model_lbl = analysis.ai_model_name or "Local AI Model"
            out.append(f"### 🧠 Neural AI Architectural Review (`{model_lbl}`)\n")
            out.append(f"{analysis.ai_architecture_critique}\n\n")

        out.append("### Technology Compatibility Analysis\n")
        out.append(f"{analysis.tech_stack.compatibility_analysis}\n\n")

        # 2. Directory Roles
        out.append("## 3. Directory Subsystem Roles\n")
        for folder, role in sorted(analysis.folder_roles.items()):
            out.append(f"- `{folder}/`: {role}\n")
        out.append("\n---\n")

        # 3. Interconnection Graph
        out.append("## 4. Cross-File Interconnection Graph & Mechanics\n")
        if analysis.interconnections:
            out.append("```mermaid\ngraph LR\n")
            for conn in analysis.interconnections:
                src_safe = conn.source_file.replace("/", "_").replace(".", "_").replace("-", "_")
                tgt_safe = conn.target_file.replace("/", "_").replace(".", "_").replace("-", "_")
                out.append(f"    {src_safe}[\"{conn.source_file}\"] -->|{conn.relation_type}| {tgt_safe}[\"{conn.target_file}\"]\n")
            out.append("```\n\n")

            for conn in analysis.interconnections:
                out.append(f"#### 🔗 `{conn.source_file}` ➔ `{conn.target_file}` (`{conn.relation_type}`)\n")
                out.append(f"- **How It Works**: {conn.how_it_works}\n")
                out.append(f"- **Why It Works**: {conn.why_it_works}\n\n")
        out.append("---\n")

        # 5. Deep File-by-File Explainer
        out.append("## 5. Deep File-by-File Analysis & Pedagogical Breakdown\n\n")
        for rel_path, fa in sorted(analysis.files.items()):
            out.append(f"### 📄 File: `{rel_path}`\n")
            out.append(f"- **Language**: `{fa.language}` | **Size**: {fa.line_count} lines ({fa.file_size_bytes:,} bytes)\n")
            out.append(f"- **Codebase Role**: {fa.role_in_codebase}\n")
            if fa.beginner_story:
                out.append(f"> 🧸 **Beginner Story**: {fa.beginner_story}\n\n")
            out.append(f"- **Executive Summary**: {fa.summary}\n")

            if fa.ai_insights:
                model_lbl = fa.ai_model_used or analysis.ai_model_name or "Local AI Model"
                out.append(f"\n> **🧠 Neural AI Insights ({model_lbl})**:\n> " + fa.ai_insights.replace("\n", "\n> ") + "\n\n")

            if fa.elements:
                out.append(f"\n#### Elements Written in `{rel_path}`\n")
                for el in fa.elements:
                    line_str = f"Line {el.line_number}" if el.line_number else "-"
                    out.append(f"- **`{el.name}`** ({el.kind}, {line_str}): {el.what_it_is} ")
                    if el.simple_analogy:
                        out.append(f"*(🧸 {el.simple_analogy})* ")
                    out.append("\n")

            out.append("\n---\n")

        return "".join(out)
