"""
Rich Terminal Reporter for Explainer.
Renders beautiful interactive summaries, tables, trees, and detailed file cards directly in the console.
"""
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.text import Text
from rich.syntax import Syntax
from explainer.core.parsers.base import FileAnalysis


class TerminalReporter:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def print_project_overview(self, arch_data: Dict[str, Any], compatibility: List[Dict[str, str]]):
        """Prints top-level codebase architecture, languages, and compatibility."""
        self.console.print("\n")
        overview_text = Text()
        overview_text.append(f"Architecture: {arch_data['architecture_type']}\n", style="bold cyan")
        overview_text.append(f"{arch_data['architecture_description']}\n\n", style="dim")
        overview_text.append(f"Total Scanned Files: {arch_data['total_files']}  |  Total Lines of Code: {arch_data['total_loc']:,}\n", style="bold white")
        overview_text.append(f"Detected Ecosystems: {', '.join(arch_data['detected_technologies'])}\n", style="green")

        self.console.print(Panel(overview_text, title="[bold magenta]Codebase Overview[/bold magenta]", border_style="magenta"))

        # Language distribution table
        lang_table = Table(title="Language Distribution", border_style="cyan", show_lines=False)
        lang_table.add_column("Language", style="bold white")
        lang_table.add_column("Lines of Code", justify="right", style="cyan")
        lang_table.add_column("Percentage", justify="right", style="green")

        tot = arch_data["total_loc"] or 1
        for lang, count in sorted(arch_data["languages"].items(), key=lambda x: -x[1]):
            pct = (count / tot) * 100
            lang_table.add_row(lang, f"{count:,}", f"{pct:.1f}%")

        self.console.print(lang_table)

        # Compatibility table
        comp_table = Table(title="Tech Stack Compatibility & Configuration Matrix", border_style="yellow")
        comp_table.add_column("Status", justify="center", width=8)
        comp_table.add_column("Category", style="dim")
        comp_table.add_column("Check", style="bold white")
        comp_table.add_column("Details", style="white")

        for c in compatibility:
            badge = "[bold green]PASS[/bold green]" if c["status"] == "PASS" else "[bold yellow]WARN[/bold yellow]"
            comp_table.add_row(badge, c["category"], c["title"], c["details"])

        self.console.print(comp_table)
        self.console.print("\n")

    def print_file_explanation(self, file_exp: Dict[str, Any], ai_narrative: Optional[str] = None):
        """Prints a comprehensive, elaborated breakdown for an individual file."""
        h = file_exp["header"]
        p = file_exp["purpose_and_context"]

        title = f"[bold cyan]{h['filename']}[/bold cyan] [dim]({h['path']})[/dim] - {h['language']}"
        header_text = (
            f"[bold]Role:[/bold] {h['role']}\n"
            f"[bold]Size:[/bold] {h['loc']} LOC ({h['size_bytes']} bytes)  |  "
            f"[bold]Tech Stack:[/bold] {', '.join(p['tech_stack_ecosystem'])}\n\n"
            f"[bold]Summary:[/bold] {p['summary']}\n\n"
            f"[bold]Architectural Significance:[/bold] {p['architectural_significance']}"
        )
        self.console.print(Panel(header_text, title=title, border_style="blue"))

        # Key Concepts & Patterns
        if file_exp["concepts_and_patterns"]:
            c_table = Table(title=f"Architectural Concepts & Design Patterns ({h['filename']})", border_style="cyan")
            c_table.add_column("Concept / Pattern", style="bold yellow", width=30)
            c_table.add_column("Detailed Explanation & Implementation", style="white")

            for item in file_exp["concepts_and_patterns"]:
                c_table.add_row(item["concept"], item["explanation"])

            self.console.print(c_table)

        # Exhaustive Symbols & Components Breakdown
        if file_exp["symbol_breakdown"]:
            sym_table = Table(title=f"Symbols & Component Elements Breakdown ({len(file_exp['symbol_breakdown'])} items)", border_style="green")
            sym_table.add_column("Line", justify="right", style="dim", width=6)
            sym_table.add_column("Kind", style="magenta", width=18)
            sym_table.add_column("Name / Signature", style="bold white", width=35)
            sym_table.add_column("Role & Description", style="white")

            for sym in file_exp["symbol_breakdown"][:25]:
                sym_table.add_row(str(sym["line"]), sym["kind"], sym["signature"][:35], sym["description"])

            self.console.print(sym_table)
            if len(file_exp["symbol_breakdown"]) > 25:
                self.console.print(f"[dim]... and {len(file_exp['symbol_breakdown']) - 25} more elements documented in full report.[/dim]")

        # Interconnections (How & Why)
        conns = file_exp["interconnections"]
        if conns["outgoing"] or conns["incoming"]:
            conn_table = Table(title=f"Cross-File Interconnections (HOW & WHY it works)", border_style="magenta")
            conn_table.add_column("Direction", style="bold yellow", width=10)
            conn_table.add_column("Connected File", style="bold white", width=25)
            conn_table.add_column("Relation Type", style="cyan", width=18)
            conn_table.add_column("HOW it works (Mechanism)", style="dim white", width=30)
            conn_table.add_column("WHY it works (Architectural Rationale)", style="white")

            for o in conns["outgoing"]:
                conn_table.add_row("OUTGOING ➔", o["target"], o["relation"], o["how"], o["why"])

            for i in conns["incoming"]:
                conn_table.add_row("INCOMING ⬅", i["source"], i["relation"], i["how"], i["why"])

            self.console.print(conn_table)
            self.console.print(f"[dim]Coupling Metric: {conns['coupling_assessment']}[/dim]\n")

        # Best Practices & Security
        if file_exp["best_practices"]:
            bp_text = "\n".join(f"• {bp}" for bp in file_exp["best_practices"])
            self.console.print(Panel(bp_text, title="Best Practices & Code Hygiene", border_style="yellow"))

        # Optional AI Narrative if available
        if ai_narrative:
            self.console.print(Panel(ai_narrative, title="[bold magenta]AI Deep Insight & Analogy[/bold magenta]", border_style="magenta"))

        self.console.print("\n" + "="*80 + "\n")
