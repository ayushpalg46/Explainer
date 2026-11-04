import os
import sys
import webbrowser
from pathlib import Path
from typing import Optional, List, Dict
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel

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
    """⚡ EXPL / Explainer: Deep Codebase & Per-File Architecture Intelligence Engine."""
    if ctx.invoked_subcommand is None:
        interactive_wizard()


def interactive_wizard():
    console.print()
    console.print("[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold white] ⚡ EXPL - Codebase & File Architecture Explainer Engine[/bold white]")
    console.print("[dim]   Deep Code Architecture, Tech Stack & File-by-File Breakdown[/dim]")
    console.print("[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]")
    console.print()

    # Detect current working directory as the codebase folder
    current_cwd = Path.cwd().resolve()
    console.print(f"[bold]📁 Current Codebase:[/bold] [underline white]{current_cwd}[/underline white]")
    
    # 1. First Prompt: Choose between Without-AI and AI (Default: 1) with "GO BACK" support
    mode_choice = "1"
    ai_provider = "ollama"
    ai_endpoint = "http://localhost:11434/api/generate"
    ai_model = None

    while True:
        console.print("\n[bold yellow]Choose Explanation Mode:[/bold yellow]")
        console.print("  [cyan][1][/cyan] [bold]Without-AI Explanation[/bold] (Deterministic Pure AST & Knowledge Engine - 100% Offline & Precise) [bold green][Default][/bold green]")
        console.print("  [cyan][2][/cyan] [bold]AI Explanation[/bold] (Local Ollama / Qwen Model)")
        mode_choice = Prompt.ask("Select mode", choices=["1", "2"], default="1")

        if mode_choice == "1":
            # Proceed directly with Without-AI mode
            break

        elif mode_choice == "2":
            console.print("\n[bold yellow]Select Local AI Model:[/bold yellow]")
            detected_models = AIExplainerEngine.list_installed_models()
            
            if detected_models:
                console.print(f"[bold green]✓ Discovered {len(detected_models)} installed Ollama model(s):[/bold green]")
                model_choices = []
                def_choice = "1"
                
                for idx, m_name in enumerate(detected_models, 1):
                    is_coder = "coder" in m_name.lower()
                    badge = " [bold green]⭐ (Specialized Code Model)[/bold green]" if is_coder else ""
                    console.print(f"  [cyan][{idx}][/cyan] {m_name}{badge}")
                    model_choices.append(str(idx))
                    if is_coder:
                        def_choice = str(idx)

                manual_idx = str(len(detected_models) + 1)
                back_idx = str(len(detected_models) + 2)

                console.print(f"  [cyan][{manual_idx}][/cyan] Enter another model name manually")
                model_choices.append(manual_idx)

                console.print(f"  [cyan][{back_idx}][/cyan] [bold yellow]↩ GO BACK[/bold yellow] (Return to Main Menu)")
                model_choices.append(back_idx)

                m_select = Prompt.ask("Choose option", choices=model_choices, default=def_choice)
                
                if m_select == back_idx:
                    console.print("[dim]Returning to main menu...[/dim]")
                    continue  # Loops back to Choose Explanation Mode
                elif m_select == manual_idx:
                    ai_model = Prompt.ask("Enter model identifier")
                    break
                else:
                    ai_model = detected_models[int(m_select) - 1]
                    break
            else:
                console.print("[yellow]No local Ollama models detected automatically.[/yellow]")
                console.print("  [cyan][1][/cyan] Enter Ollama model name manually")
                console.print("  [cyan][2][/cyan] [bold yellow]↩ GO BACK[/bold yellow] (Return to Main Menu)")
                m_select = Prompt.ask("Choose option", choices=["1", "2"], default="1")
                
                if m_select == "2":
                    console.print("[dim]Returning to main menu...[/dim]")
                    continue  # Loops back to Choose Explanation Mode
                else:
                    ai_model = Prompt.ask(
                        "Enter Ollama model name",
                        default="hf.co/BlossomsAI/Qwen2.5-Coder-7B-Instruct-Uncensored-GGUF:Q6_K"
                    )
                    break

    # Automatically derive the folder name: (<Codebase folder-name>-EXPL)
    codebase_folder_name = current_cwd.name or "Codebase"
    expl_folder_name = f"{codebase_folder_name}-EXPL"
    expl_output_dir = current_cwd / expl_folder_name

    # 2. Run the analysis engine
    codebase_analysis = run_core_analysis(
        target_path=str(current_cwd),
        mode="ai" if mode_choice == "2" else "static",
        ai_provider=ai_provider,
        ai_endpoint=ai_endpoint,
        ai_model=ai_model
    )

    # 3. Generate the (<Codebase folder-name>-EXPL) folder structure
    with console.status("[bold green]Writing individual file explanations to folder...[/bold green]"):
        md_renderer = MarkdownRenderer()
        generated_files = md_renderer.render_multi_file_dossier(codebase_analysis, str(expl_output_dir))

        # Generate HTML Dashboard inside the folder
        html_renderer = HtmlDashboardRenderer()
        html_path = expl_output_dir / "dashboard.html"
        html_renderer.render(codebase_analysis, str(html_path))

    # 4. Notify user work has been done
    file_count = len(codebase_analysis.files)
    console.print()
    console.print("[bold green]════════════════════════════════════════════════════════════════════[/bold green]")
    console.print(f"[bold white] ✔ Work has been done successfully![/bold white]")
    console.print(f"[bold cyan] 📁 Created Folder:[/bold cyan] [bold white]{expl_folder_name}[/bold white]")
    console.print(f"[dim]    • Generated separate detailed explanations for each of the {file_count} files in:[/dim] [white]{expl_folder_name}/files/[/white]")
    console.print(f"[dim]    • Generated Master Architecture Index in:[/dim] [white]{expl_folder_name}/INDEX.md[/white]")
    console.print(f"[dim]    • Generated Interactive Visual Web GUI in:[/dim] [white]{expl_folder_name}/dashboard.html[/white]")
    console.print("[bold green]════════════════════════════════════════════════════════════════════[/bold green]")
    console.print()

    # 5. Second Prompt: Choose how to view (Default: 1)
    console.print("[bold yellow]How would you like to view the explanation?[/bold yellow]")
    console.print("  [cyan][1][/cyan] [bold]Want To See In Codebase Files Explanation In CLI[/bold] [bold green][Default][/bold green]")
    console.print("  [cyan][2][/cyan] [bold]Want To See In Codebase Files Explanation In Webpage (GUI)[/bold]")
    view_choice = Prompt.ask("Choose view format", choices=["1", "2"], default="1")

    if view_choice == "1":
        # Interactive CLI Viewer
        terminal_renderer = RichTerminalRenderer()
        terminal_renderer.render(codebase_analysis, inspect_file=None)
        run_cli_file_inspector(codebase_analysis)
    else:
        # Open in Web Browser
        console.print(f"\n[bold green]🌐 Opening Webpage GUI in your default browser...[/bold green]")
        webbrowser.open(html_path.resolve().as_uri())


def run_cli_file_inspector(codebase_analysis):
    """Allows user to interactively inspect any file explanation in terminal."""
    file_keys = sorted(list(codebase_analysis.files.keys()))
    if not file_keys:
        return

    terminal_renderer = RichTerminalRenderer()

    while True:
        console.print("\n[bold cyan]🔎 Inspect Individual File Breakdown in CLI:[/bold cyan]")
        console.print("Enter file number, file path, 'all', or 'q' to quit:")
        for idx, f_path in enumerate(file_keys, 1):
            fa = codebase_analysis.files[f_path]
            console.print(f"  [cyan][{idx}][/cyan] {f_path} [dim]({fa.language} • {fa.line_count} LOC)[/dim]")

        user_input = Prompt.ask("\nSelect file to inspect", default="q")
        if user_input.strip().lower() in ("q", "quit", "exit"):
            console.print("[dim]Exiting CLI Inspector. All files remain saved in your `-EXPL` folder.[/dim]\n")
            break
        elif user_input.strip().lower() == "all":
            for f_path in file_keys:
                terminal_renderer.render(codebase_analysis, inspect_file=f_path)
            break
        elif user_input.isdigit() and 1 <= int(user_input) <= len(file_keys):
            selected_path = file_keys[int(user_input) - 1]
            terminal_renderer.render(codebase_analysis, inspect_file=selected_path)
        elif user_input in codebase_analysis.files:
            terminal_renderer.render(codebase_analysis, inspect_file=user_input)
        else:
            console.print("[red]Invalid selection. Please choose a valid file number or 'q'.[/red]")


def run_core_analysis(
    target_path: str,
    mode: str = "static",
    ai_provider: str = "ollama",
    ai_endpoint: str = "http://localhost:11434/api/generate",
    ai_model: Optional[str] = None
):
    """Core analysis orchestrator returning a CodebaseAnalysis object."""
    target_p = Path(target_path).resolve()
    with console.status("[bold green]Scanning codebase source files...[/bold green]"):
        scanner = WorkspaceScanner(str(target_p))
        scanned_files = scanner.scan()

    if not scanned_files:
        console.print("[bold red]❌ No readable source files detected in codebase directory.[/bold red]")
        sys.exit(1)

    console.print(f"[bold cyan]✓[/bold cyan] Discovered [bold]{len(scanned_files)}[/bold] files to analyze.")

    # Parse all files
    registry = ParserRegistry()
    analyzed_files = {}

    with console.status("[bold green]Extracting AST, tags, components, and concepts across all files...[/bold green]"):
        for fpath, rel_path in scanned_files:
            # Skip previously generated EXPL folders
            if "-EXPL" in rel_path:
                continue
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
        engine = AIExplainerEngine(
            endpoint_url=ai_endpoint,
            model_name=ai_model,
            provider=ai_provider
        )
        console.print(f"[bold magenta]🧠 Running Local AI Engine ({engine.model_name} via {ai_provider})...[/bold magenta]")
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

    return codebase_analysis


def run_cli_scan(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir):
    """Executes analysis and writes out the (<Codebase folder-name>-EXPL) multi-file dossier."""
    target_p = Path(path).resolve()
    codebase_name = target_p.name or "Codebase"
    out_dir = Path(output_dir) if output_dir else (target_p / f"{codebase_name}-EXPL")

    analysis = run_core_analysis(
        target_path=str(target_p),
        mode=mode,
        ai_provider=ai_provider,
        ai_endpoint=ai_endpoint,
        ai_model=ai_model
    )

    md_renderer = MarkdownRenderer()
    md_renderer.render_multi_file_dossier(analysis, str(out_dir))

    html_renderer = HtmlDashboardRenderer()
    html_renderer.render(analysis, str(out_dir / "dashboard.html"))

    if fmt in ("terminal", "all"):
        terminal_renderer = RichTerminalRenderer()
        terminal_renderer.render(analysis, inspect_file=inspect)

    console.print(f"[bold green]✔ Complete multi-file dossier generated in:[/bold green] [underline white]{out_dir}[/underline white]")
    return analysis, out_dir


@main.command(name="analyze")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["static", "ai"]), default="static", help="Engine mode: 'static' (Zero-AI) or 'ai' (Local LLM).")
@click.option("--format", "fmt", type=click.Choice(["terminal", "markdown", "html", "all"]), default="all", help="Output format.")
@click.option("--ai-provider", type=click.Choice(["ollama", "openai_compatible"]), default="ollama", help="Local AI provider.")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default=None, help="AI model identifier.")
@click.option("--inspect", default=None, help="Specific relative file to inspect deeply in terminal.")
@click.option("--output-dir", default=None, help="Directory to save generated markdown and HTML reports.")
def analyze_cmd(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir):
    """Analyze a repository or individual file from CLI flags."""
    run_cli_scan(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir)


@main.command(name="scan")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["static", "ai"]), default="static", help="Engine mode: 'static' (Zero-AI) or 'ai' (Local LLM).")
@click.option("--format", "fmt", type=click.Choice(["terminal", "markdown", "html", "all"]), default="all", help="Output format.")
@click.option("--ai-provider", type=click.Choice(["ollama", "openai_compatible"]), default="ollama", help="Local AI provider.")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default=None, help="AI model identifier.")
@click.option("--inspect", default=None, help="Specific relative file to inspect deeply in terminal.")
@click.option("--output-dir", default=None, help="Directory to save generated markdown and HTML reports.")
def scan_cmd(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir):
    """Scan and explain a codebase (alias for analyze)."""
    run_cli_scan(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir)


if __name__ == "__main__":
    main()
