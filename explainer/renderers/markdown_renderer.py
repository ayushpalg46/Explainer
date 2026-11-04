from pathlib import Path
from ..models import CodebaseAnalysis, FileAnalysis


class MarkdownRenderer:
    def render(self, analysis: CodebaseAnalysis, output_path: str) -> str:
        out = []

        out.append(f"# Comprehensive Codebase & Architecture Dossier: `{analysis.project_name}`\n")
        out.append(f"> **Engine Used**: {analysis.engine_used}  \n")
        out.append(f"> **Scope**: {analysis.total_files} files | {analysis.total_lines:,} lines of code | {len(analysis.interconnections)} interconnections\n")
        out.append("---\n")

        # 1. Architecture & Tech Stack
        out.append("## 1. Architecture & Tech Stack Ecosystem\n")
        out.append(f"### Architectural Style: **{analysis.architecture_style}**\n")
        out.append(f"{analysis.architecture_summary}\n\n")

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
        out.append("\n---\n")

        # 2. Directory Structure & Folder Roles
        out.append("## 2. Directory Hierarchy & Subsystem Roles\n")
        out.append("| Directory / Subsystem | Purpose & Architectural Role |\n")
        out.append("| :--- | :--- |\n")
        for folder, role in sorted(analysis.folder_roles.items()):
            out.append(f"| `{folder}/` | {role} |\n")
        out.append("\n---\n")

        # 3. Cross-File Interconnection Graph & Mechanics
        out.append("## 3. Cross-File Interconnections & Dependency Graph\n")
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
        else:
            out.append("*No cross-file interconnections detected (single file or isolated modules).*\n\n")
        out.append("---\n")

        # 4. Deep File-by-File Explainer
        out.append("## 4. Deep File-by-File Analysis & Pedagogical Breakdown\n\n")
        for rel_path, fa in sorted(analysis.files.items()):
            out.append(f"### 📄 File: `{rel_path}`\n")
            out.append(f"- **Language**: `{fa.language}`\n")
            out.append(f"- **Size**: {fa.line_count} lines ({fa.file_size_bytes:,} bytes)\n")
            out.append(f"- **Codebase Role**: {fa.role_in_codebase}\n")
            out.append(f"- **Executive Summary**: {fa.summary}\n")
            if fa.concepts_detected:
                out.append(f"- **Concepts Identified**: {', '.join(fa.concepts_detected)}\n")
            if fa.frameworks_detected:
                out.append(f"- **Frameworks / Libraries**: {', '.join(fa.frameworks_detected)}\n")
            if fa.design_and_style_notes:
                out.append(f"- **Design & Styling Architecture**: {fa.design_and_style_notes}\n")
            if fa.animations_and_interactions:
                out.append(f"- **Animations & Motion**: {fa.animations_and_interactions}\n")

            if fa.inbound_connections or fa.outbound_connections:
                out.append("\n**File Dependencies**:\n")
                for outb in fa.outbound_connections:
                    out.append(f"- ➡️ *Depends on* `{outb.target_file}` ({outb.relation_type})\n")
                for inb in fa.inbound_connections:
                    out.append(f"- ⬅️ *Referenced by* `{inb.source_file}` ({inb.relation_type})\n")

            if fa.elements:
                out.append(f"\n#### Elements, Tags & Components in `{rel_path}`\n\n")
                out.append("| Element | Kind | Line | What It Is & How It's Used | Where It's Used | Why It Works & Best Practice |\n")
                out.append("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
                for el in fa.elements:
                    line_str = str(el.line_number) if el.line_number else "-"
                    what_how = f"**What:** {el.what_it_is}<br>**How:** {el.how_it_is_used}"
                    why_bp = f"**Why:** {el.why_it_works}<br>**Best Practice:** {el.best_practices_and_pitfalls or 'Standard conventions.'}"
                    # Escape pipes in markdown table
                    name_esc = el.name.replace("|", "\\|")
                    out.append(f"| `{name_esc}` | {el.kind} | {line_str} | {what_how} | {el.where_it_is_used} | {why_bp} |\n")

            out.append("\n---\n")

        content = "".join(out)
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(content, encoding="utf-8")
        return str(out_p)

