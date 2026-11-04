from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich.markdown import Markdown
from rich.markup import escape
from ..models import CodebaseAnalysis, FileAnalysis


class RichTerminalRenderer:
    def __init__(self):
        self.console = Console()

    def render(self, analysis: CodebaseAnalysis, inspect_file: str = None):
        c = self.console
        c.print()
        c.print(Panel.fit(
            f"[bold cyan]🔍 Codebase & File Explainer[/bold cyan]\n"
            f"[dim]Project:[/dim] [bold white]{analysis.project_name}[/bold white]  |  "
            f"[dim]Files:[/dim] [green]{analysis.total_files}[/green]  |  "
            f"[dim]Lines:[/dim] [green]{analysis.total_lines:,}[/green]\n"
            f"[dim]Engine:[/dim] [magenta]{analysis.engine_used}[/magenta]",
            border_style="cyan"
        ))

        # Architecture & Tech Stack Summary
        if analysis.beginner_codebase_story:
            c.print(Panel(
                f"[bold yellow]🏰 The Big Castle Story (Explain Like I'm 4 Years Old):[/bold yellow]\n\n{analysis.beginner_codebase_story}",
                title="Beginner Codebase Big Picture",
                border_style="cyan"
            ))

        arch_content = (
            f"[bold yellow]🏛 Architecture Style:[/bold yellow] {analysis.architecture_style}\n\n"
            f"{analysis.architecture_summary}\n\n"
            f"[bold cyan]Tech Stack Compatibility:[/bold cyan]\n{analysis.tech_stack.compatibility_analysis}"
        )
        if analysis.ai_architecture_critique:
            arch_content += f"\n\n[bold magenta]🧠 Neural AI Architectural Review ({analysis.ai_model_name or 'Local AI'}):[/bold magenta]\n{analysis.ai_architecture_critique}"

        c.print(Panel(
            arch_content,
            title="Project Architecture & Ecosystem",
            border_style="blue"
        ))

        # Tech Stack Breakdown Table
        table = Table(title="Technology & Tooling Breakdown", border_style="dim")
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Detected Items", style="white")

        table.add_row("Languages", ", ".join([f"{k} ({v})" for k, v in analysis.tech_stack.languages.items()]))
        if analysis.tech_stack.frameworks:
            table.add_row("Frameworks", ", ".join(analysis.tech_stack.frameworks))
        if analysis.tech_stack.build_tools:
            table.add_row("Build Tools", ", ".join(analysis.tech_stack.build_tools))
        if analysis.tech_stack.package_managers:
            table.add_row("Package Managers", ", ".join(analysis.tech_stack.package_managers))
        if analysis.tech_stack.runtimes:
            table.add_row("Runtimes", ", ".join(analysis.tech_stack.runtimes))

        c.print(table)
        c.print()

        # Files Summary Table
        file_table = Table(title="Files & Roles Summary", border_style="dim")
        file_table.add_column("File", style="bold green")
        file_table.add_column("Language", style="yellow")
        file_table.add_column("Lines", justify="right", style="cyan")
        file_table.add_column("Role / Summary", style="white")

        for rel_path, fa in sorted(analysis.files.items()):
            file_table.add_row(
                rel_path,
                fa.language,
                str(fa.line_count),
                fa.role_in_codebase
            )
        c.print(file_table)
        c.print()

        # If inspecting single file or show all files
        target_files = [inspect_file] if inspect_file and inspect_file in analysis.files else list(analysis.files.keys())
        
        for rel_path in target_files:
            fa = analysis.files[rel_path]
            self.render_single_file(fa, project_name=analysis.project_name)

        # Cross-File Interconnections Table
        if analysis.interconnections:
            dep_table = Table(title=f"Cross-File Interconnections ({len(analysis.interconnections)} Links)", border_style="magenta")
            dep_table.add_column("Source", style="cyan")
            dep_table.add_column("Target", style="green")
            dep_table.add_column("Type", style="yellow")
            dep_table.add_column("How & Why It Works", style="white")

            for conn in analysis.interconnections:
                how_why = f"[bold]How:[/bold] {conn.how_it_works}\n[bold]Why:[/bold] {conn.why_it_works}"
                dep_table.add_row(conn.source_file, conn.target_file, conn.relation_type, how_why)
            
            c.print(dep_table)
            c.print()

    def render_single_file(self, fa: FileAnalysis, project_name: str = "Codebase"):
        """Renders the standard line-by-line & word-by-word explanation for a single file in CLI."""
        c = self.console
        c.print()
        c.print(Panel(
            f"[bold green]📄 {fa.relative_path}[/bold green] ([dim]{fa.language} • {fa.line_count} lines • {fa.file_size_bytes} bytes[/dim])\n"
            f"[bold]Project:[/bold] {project_name}  |  [bold]Role:[/bold] {fa.role_in_codebase}\n"
            f"[bold]Summary:[/bold] {fa.summary}",
            title=f"File Overview: {fa.relative_path}",
            border_style="green"
        ))

        # 1. Big Picture Story
        story = fa.beginner_story or f"This {fa.language} file `{fa.relative_path}` acts like a dedicated tool fulfilling the role: {fa.role_in_codebase}."
        c.print(Panel(
            f"[italic white]\"{story}\"[/italic white]",
            title="🧸 1. The Big Picture Story (What is this code?)",
            border_style="yellow"
        ))

        # Neural AI Breakdown (if present)
        if fa.ai_insights:
            model_badge = fa.ai_model_used or "Local AI Model"
            c.print(Panel(
                Markdown(fa.ai_insights),
                title=f"🧠 Neural AI Code Analysis ({model_badge})",
                subtitle="Live Model Synthesized Breakdown",
                border_style="magenta"
            ))

        # 2. Line-by-Line & Word-by-Word Breakdown
        c.print("\n[bold cyan]🔍 2. Line-by-Line & Word-by-Word Breakdown[/bold cyan]\n")
        if fa.elements:
            for el in fa.elements:
                line_str = f"Line {el.line_number}" if el.line_number is not None else "Declaration"
                snippet_line = (el.snippet or el.name).strip()
                # Code line highlighted in blue as explicitly requested
                c.print(f"[bold cyan]#### {line_str}:[/bold cyan] [bold #3b82f6]{escape(snippet_line)}[/bold #3b82f6]\n")
                c.print(f"  • [bold]What is written?:[/bold] {escape(el.what_it_is)}")

                if el.words_breakdown:
                    c.print("  • [bold]What does every word mean?:[/bold]")
                    for w, meaning in el.words_breakdown.items():
                        c.print(f"      • [bold cyan]{escape(w)}[/bold cyan]: {escape(str(meaning))}")

                if el.simple_analogy:
                    c.print(f"  • [bold yellow]🧸 4-Year-Old Analogy:[/bold yellow] {escape(el.simple_analogy)}")

                screen_effect = el.what_happens_on_screen or "Executes instructions inside computer memory."
                c.print(f"  • [bold cyan]🖥️ What happens on screen?:[/bold cyan] {escape(screen_effect)}")

                if el.interconnection_note:
                    c.print("  • [bold magenta]🔗 Interconnection with other files:[/bold magenta]")
                    for conn in el.interconnection_note.strip().splitlines():
                        conn_clean = conn.strip().lstrip("•-* ")
                        if conn_clean:
                            c.print(f"      • {escape(conn_clean)}")

                if el.what_if_removed:
                    c.print(f"  • [bold red]💥 What breaks if deleted?:[/bold red] {escape(el.what_if_removed)}")

                c.print("[dim]  ────────────────────────────────────────────────────────────────────[/dim]\n")
        else:
            c.print("[dim]  • No parsed lines in this file.[/dim]\n")

        # 3. Cross-File Dependencies
        if fa.outbound_connections or fa.inbound_connections:
            c.print("[bold magenta]🔗 3. Cross-File Dependencies & Friendship Map[/bold magenta]")
            for outb in fa.outbound_connections:
                c.print(f"  ➡️ [bold]Depends on:[/bold] [green]{escape(outb.target_file)}[/green] [dim]({escape(outb.relation_type)})[/dim]")
                c.print(f"     [dim]• How:[/dim] {escape(outb.how_it_works)}")
                c.print(f"     [dim]• Why:[/dim] {escape(outb.why_it_works)}")
            for inb in fa.inbound_connections:
                c.print(f"  ⬅️ [bold]Referenced by:[/bold] [cyan]{escape(inb.source_file)}[/cyan] [dim]({escape(inb.relation_type)})[/dim]")
                c.print(f"     [dim]• How:[/dim] {escape(inb.how_it_works)}")
                c.print(f"     [dim]• Why:[/dim] {escape(inb.why_it_works)}")
            c.print()

    def render_diff(self, diff_analysis):
        """Renders the Git Diff line-by-line & word-by-word explanation in CLI."""
        c = self.console
        c.print()
        c.print(Panel(
            f"[bold cyan]🔍 Git Diff Architecture Explainer[/bold cyan]\n"
            f"[dim]Reference / Scope:[/dim] [bold white]{escape(diff_analysis.ref or 'Working Tree')}[/bold white]\n"
            f"[dim]Files Modified:[/dim] [green]{diff_analysis.total_files_changed}[/green]  |  "
            f"[dim]Lines Added:[/dim] [green]+{diff_analysis.total_lines_added}[/green]  |  "
            f"[dim]Lines Removed:[/dim] [red]-{diff_analysis.total_lines_deleted}[/red]",
            border_style="cyan"
        ))

        # 1. Big Picture Story
        if diff_analysis.big_picture_story:
            c.print(Panel(
                f"[italic white]\"{escape(diff_analysis.big_picture_story)}\"[/italic white]",
                title="🧸 1. The Big Picture Story (What is this code change?)",
                border_style="yellow"
            ))

        # AI Insights if available
        if diff_analysis.ai_insights:
            model_badge = diff_analysis.ai_model_used or "Local AI Model"
            c.print(Panel(
                Markdown(diff_analysis.ai_insights),
                title=f"🧠 Neural AI Diff Analysis ({model_badge})",
                subtitle="Live Model Synthesized Breakdown",
                border_style="magenta"
            ))

        # 2. Line-by-Line & Word-by-Word Breakdown
        c.print("\n[bold cyan]🔍 2. Line-by-Line & Word-by-Word Breakdown of Changed Code[/bold cyan]\n")
        if diff_analysis.line_explanations:
            for exp in diff_analysis.line_explanations:
                line_str = f"Line {exp.line_number}" if exp.line_number is not None else "Added Line"
                # Blue code line
                c.print(f"[bold cyan]#### {escape(exp.file_path)} [{line_str}]:[/bold cyan] [bold #3b82f6]{escape(exp.code_line)}[/bold #3b82f6]\n")
                c.print(f"  • [bold]What is written?:[/bold] {escape(exp.what_is_written)}")

                if exp.words_breakdown:
                    c.print("  • [bold]What does every word mean?:[/bold]")
                    for w, meaning in exp.words_breakdown.items():
                        c.print(f"      • [bold cyan]{escape(w)}[/bold cyan]: {escape(str(meaning))}")

                if exp.simple_analogy:
                    c.print(f"  • [bold yellow]🧸 4-Year-Old Analogy:[/bold yellow] {escape(exp.simple_analogy)}")

                if exp.what_happens_on_screen:
                    c.print(f"  • [bold cyan]🖥️ What happens on screen / in system?:[/bold cyan] {escape(exp.what_happens_on_screen)}")

                if exp.interconnection_note:
                    c.print(f"  • [bold magenta]🔗 Interconnection with other files:[/bold magenta] {escape(exp.interconnection_note)}")

                if exp.what_breaks_if_deleted:
                    c.print(f"  • [bold red]💥 What breaks if deleted?:[/bold red] {escape(exp.what_breaks_if_deleted)}")

                c.print("[dim]  ────────────────────────────────────────────────────────────────────[/dim]\n")
        else:
            c.print("[dim]  • No added lines to explain in this diff.[/dim]\n")


