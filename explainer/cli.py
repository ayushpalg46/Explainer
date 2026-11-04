import os
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

from .scanner.workspace_scanner import WorkspaceScanner
from .scanner.tech_stack import TechStackAnalyzer
from .parsers.registry import ParserRegistry
from .graph.dependency_builder import DependencyGraphBuilder
from .engine.rule_engine import RuleExplainerEngine
from .engine.ai_engine import AIExplainerEngine
from .renderers.rich_terminal import RichTerminalRenderer
from .renderers.markdown_renderer import MarkdownRenderer
from .renderers.html_dashboard import HtmlDashboardRenderer

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Dual-Engine Codebase & File Explainer Tool."""
    if ctx.invoked_subcommand is None:
        interactive_wizard()


def interactive_wizard():
    console.print()
    console.print("[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold white] 🔍 Welcome to the Dual-Engine Codebase & File Explainer Tool[/bold white]")
    console.print("[dim]   Deep Code Architecture, Tech Stack & File-by-File Breakdown[/dim]")
    console.print("[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]")
    console.print()

    # 1. Target directory
    default_dir = os.getcwd()
    target_dir = Prompt.ask(
        "[bold green]Enter codebase directory or file path[/bold green]",
        default=default_dir
    )

    # 2. Engine Mode Choice
    console.print("\n[bold yellow]Select Analysis Engine:[/bold yellow]")
    console.print("  [cyan][1][/cyan] [bold]Pure Knowledge & AST Engine (Zero-AI)[/bold] - 100% Deterministic, Fast, Deep Grammar & Architecture Analysis")
    console.print("  [cyan][2][/cyan] [bold]Local AI Model Engine[/bold] - Connects to local Ollama or LM Studio model")
    mode_choice = Prompt.ask("Choose mode", choices=["1", "2"], default="1")

    ai_provider = "ollama"
    ai_endpoint = "http://localhost:11434/api/generate"
    ai_model = "llama3"

    if mode_choice == "2":
        console.print("\n[bold yellow]Local AI Model Configuration:[/bold yellow]")
        console.print("  [cyan][1][/cyan] Ollama (Default: http://localhost:11434)")
        console.print("  [cyan][2][/cyan] LM Studio / Local OpenAI Compatible Server (Default: http://localhost:1234/v1)")
        p_choice = Prompt.ask("Choose runner", choices=["1", "2"], default="1")
        if p_choice == "1":
            ai_provider = "ollama"
            ai_endpoint = Prompt.ask("Ollama endpoint URL", default="http://localhost:11434/api/generate")
            ai_model = Prompt.ask("Model name (e.g. llama3, mistral, deepseek-coder)", default="llama3")
        else:
            ai_provider = "openai_compatible"
            ai_endpoint = Prompt.ask("Server endpoint URL", default="http://localhost:1234/v1")
            ai_model = Prompt.ask("Model name or path", default="local-model")

    # 3. Output Format Choice
    console.print("\n[bold yellow]Select Output Format:[/bold yellow]")
    console.print("  [cyan][1][/cyan] Terminal Interactive UI Only")
    console.print("  [cyan][2][/cyan] Markdown Report (`EXPLAINER_REPORT.md`)")
    console.print("  [cyan][3][/cyan] Interactive HTML Visual Dashboard (`explainer_dashboard.html`)")
    console.print("  [cyan][4][/cyan] [bold green]All Formats (Terminal + Markdown + HTML Dashboard)[/bold green] [Recommended]")
    format_choice = Prompt.ask("Choose format", choices=["1", "2", "3", "4"], default="4")

    run_pipeline(
        target_path=target_dir,
        mode="ai" if mode_choice == "2" else "static",
        fmt="all" if format_choice == "4" else {"1": "terminal", "2": "markdown", "3": "html"}[format_choice],
        ai_provider=ai_provider,
        ai_endpoint=ai_endpoint,
        ai_model=ai_model
    )


@main.command(name="analyze")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["static", "ai"]), default="static", help="Engine mode: 'static' (Zero-AI) or 'ai' (Local LLM).")
@click.option("--format", "fmt", type=click.Choice(["terminal", "markdown", "html", "all"]), default="all", help="Output format.")
@click.option("--ai-provider", type=click.Choice(["ollama", "openai_compatible"]), default="ollama", help="Local AI provider.")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default="llama3", help="AI model identifier.")
@click.option("--inspect", default=None, help="Specific relative file to inspect deeply in terminal.")
@click.option("--output-dir", default=".", help="Directory to save generated markdown and HTML reports.")
def analyze_cmd(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir):
    """Analyze a repository or individual file from CLI flags."""
    run_pipeline(
        target_path=path,
        mode=mode,
        fmt=fmt,
        ai_provider=ai_provider,
        ai_endpoint=ai_endpoint,
        ai_model=ai_model,
        inspect_file=inspect,
        output_dir=output_dir
    )


@main.command(name="scan")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["static", "ai"]), default="static", help="Engine mode: 'static' (Zero-AI) or 'ai' (Local LLM).")
@click.option("--format", "fmt", type=click.Choice(["terminal", "markdown", "html", "all"]), default="all", help="Output format.")
@click.option("--ai-provider", type=click.Choice(["ollama", "openai_compatible"]), default="ollama", help="Local AI provider.")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default="llama3", help="AI model identifier.")
@click.option("--inspect", default=None, help="Specific relative file to inspect deeply in terminal.")
@click.option("--output-dir", default=".", help="Directory to save generated markdown and HTML reports.")
def scan_cmd(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir):
    """Scan and explain a codebase (alias for analyze)."""
    run_pipeline(
        target_path=path,
        mode=mode,
        fmt=fmt,
        ai_provider=ai_provider,
        ai_endpoint=ai_endpoint,
        ai_model=ai_model,
        inspect_file=inspect,
        output_dir=output_dir
    )



def run_pipeline(
    target_path: str,
    mode: str = "static",
    fmt: str = "all",
    ai_provider: str = "ollama",
    ai_endpoint: str = "http://localhost:11434/api/generate",
    ai_model: str = "llama3",
    inspect_file: Optional[str] = None,
    output_dir: str = "."
):
    target_p = Path(target_path).resolve()
    with console.status("[bold green]Scanning workspace and source files...[/bold green]"):
        scanner = WorkspaceScanner(str(target_p))
        scanned_files = scanner.scan()

    if not scanned_files:
        console.print("[bold red]❌ No readable source files detected at specified path.[/bold red]")
        sys.exit(1)

    console.print(f"[bold cyan]✓[/bold cyan] Discovered [bold]{len(scanned_files)}[/bold] source files to analyze.")

    # Parse all files
    registry = ParserRegistry()
    analyzed_files = {}

    with console.status("[bold green]Extracting AST, tags, components, and concepts...[/bold green]"):
        for fpath, rel_path in scanned_files:
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
                parser = registry.get_parser_for_path(fpath)
                analysis = parser.parse(str(fpath), content, rel_path)
                analyzed_files[rel_path] = analysis
            except Exception as e:
                console.print(f"[dim yellow]Warning: Failed to parse {rel_path}: {e}[/dim yellow]")

    # Build Dependency & Interconnection Graph
    with console.status("[bold green]Resolving cross-file dependency graph and mechanics...[/bold green]"):
        dep_builder = DependencyGraphBuilder(analyzed_files)
        interconnections = dep_builder.build_interconnections()

    # Analyze Tech Stack
    with console.status("[bold green]Analyzing technology stack & ecosystem compatibility...[/bold green]"):
        ts_analyzer = TechStackAnalyzer(str(target_p if target_p.is_dir() else target_p.parent))
        tech_stack = ts_analyzer.analyze(analyzed_files)

    # Execute Explainer Engine
    if mode == "ai":
        console.print(f"[bold magenta]🧠 Running Local AI Engine ({ai_model} via {ai_provider})...[/bold magenta]")
        engine = AIExplainerEngine(
            endpoint_url=ai_endpoint,
            model_name=ai_model,
            provider=ai_provider
        )
    else:
        console.print("[bold green]⚡ Running Pure Knowledge & AST Engine (Zero-AI Deterministic Mode)...[/bold green]")
        engine = RuleExplainerEngine()

    with console.status("[bold green]Synthesizing deep pedagogical dossier...[/bold green]"):
        codebase_analysis = engine.analyze_codebase(
            root_path=str(target_p),
            files=analyzed_files,
            tech_stack=tech_stack,
            interconnections=interconnections
        )

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Render Outputs
    if fmt in ("terminal", "all"):
        terminal_renderer = RichTerminalRenderer()
        terminal_renderer.render(codebase_analysis, inspect_file=inspect_file)

    if fmt in ("markdown", "all"):
        md_path = out_dir / "EXPLAINER_REPORT.md"
        md_renderer = MarkdownRenderer()
        written_md = md_renderer.render(codebase_analysis, str(md_path))
        console.print(f"[bold green]✓ Markdown Report generated:[/bold green] [underline cyan]{written_md}[/underline cyan]")

    if fmt in ("html", "all"):
        html_path = out_dir / "explainer_dashboard.html"
        html_renderer = HtmlDashboardRenderer()
        written_html = html_renderer.render(codebase_analysis, str(html_path))
        console.print(f"[bold green]✓ Interactive Visual Dashboard generated:[/bold green] [underline cyan]{written_html}[/underline cyan]")


if __name__ == "__main__":
    main()
