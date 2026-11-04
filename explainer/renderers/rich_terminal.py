from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich.markdown import Markdown
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
        c.print(Panel(
            f"[bold yellow]🏛 Architecture Style:[/bold yellow] {analysis.architecture_style}\n\n"
            f"{analysis.architecture_summary}\n\n"
            f"[bold cyan]Tech Stack Compatibility:[/bold cyan]\n{analysis.tech_stack.compatibility_analysis}",
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
            self._render_file_deep_dive(fa)

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

    def _render_file_deep_dive(self, fa: FileAnalysis):
        c = self.console
        c.print(Panel(
            f"[bold green]📄 {fa.relative_path}[/bold green] ([dim]{fa.language}, {fa.line_count} lines, {fa.file_size_bytes} bytes[/dim])\n"
            f"[bold]Role:[/bold] {fa.role_in_codebase}\n"
            f"[bold]Summary:[/bold] {fa.summary}\n"
            f"{f'[bold yellow]Concepts:[/bold yellow] ' + ', '.join(fa.concepts_detected) if fa.concepts_detected else ''}\n"
            f"{f'[bold cyan]Design & Styling:[/bold cyan] ' + fa.design_and_style_notes if fa.design_and_style_notes else ''}\n"
            f"{f'[bold magenta]Motion & Interactions:[/bold magenta] ' + fa.animations_and_interactions if fa.animations_and_interactions else ''}",
            title=f"Deep File Explainer: {fa.relative_path}",
            border_style="green"
        ))

        if fa.elements:
            elem_table = Table(title=f"Elements Breakdown ({len(fa.elements)} elements in {fa.relative_path})", border_style="dim")
            elem_table.add_column("Name", style="bold cyan")
            elem_table.add_column("Kind", style="yellow")
            elem_table.add_column("Line", justify="right", style="dim")
            elem_table.add_column("What & How", style="white")
            elem_table.add_column("Why & Best Practice", style="green")

            for el in fa.elements[:15]:  # Display top 15 in terminal to keep readable
                what_how = f"[bold]What:[/bold] {el.what_it_is}\n[bold]How:[/bold] {el.how_it_is_used}\n[bold]Where:[/bold] {el.where_it_is_used}"
                why_bp = f"[bold]Why:[/bold] {el.why_it_works}\n[bold]Best Practice:[/bold] {el.best_practices_and_pitfalls or 'Follow framework standards.'}"
                elem_table.add_row(
                    el.name,
                    el.kind,
                    str(el.line_number) if el.line_number else "-",
                    what_how,
                    why_bp
                )
            c.print(elem_table)
            c.print()

