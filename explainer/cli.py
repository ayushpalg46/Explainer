import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
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
from .diff.git_diff_explainer import GitDiffExplainer, DiffAnalysis
from .models import CodebaseAnalysis, TechStackInfo
from .scanner.remote_resolver import RemoteResolver
from .engine.cloud_providers import CloudAIProvider

console = Console()
_flush_token = lambda t: (sys.stdout.write(t), sys.stdout.flush())

AI_PROVIDER_CHOICES = ["ollama", "groq", "gemini", "openai", "openrouter", "openai_compatible"]


def resolve_file_key(arg: str, file_keys: List[str], files_dict: Dict) -> Optional[str]:
    """Resolves an index number or relative path to a valid file key in the codebase."""
    if arg.isdigit() and 1 <= int(arg) <= len(file_keys):
        return file_keys[int(arg) - 1]
    return arg if arg in files_dict else None


class ExplGroup(click.Group):
    """Custom Click Group that dynamically routes remote URLs or file paths directly."""
    def resolve_command(self, ctx, args):
        if not args:
            return super().resolve_command(ctx, args)
        cmd_name = args[0]
        cmd = self.get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd_name, cmd, args[1:]
        # If the argument is a remote Git or web URL, route to remote
        if RemoteResolver.is_remote_url(cmd_name):
            return "remote", self.get_command(ctx, "remote"), args
        # If the argument is an existing file, route to explain_file
        if Path(cmd_name).is_file():
            return "explain_file", self.get_command(ctx, "explain_file"), args
        return super().resolve_command(ctx, args)


@click.group(cls=ExplGroup, invoke_without_command=True)
@click.pass_context
def main(ctx):
    """⚡ EXPL / Explainer: Deep Codebase & Per-File Architecture Intelligence Engine."""
    if ctx.invoked_subcommand is None:
        interactive_wizard()


def select_mode_interactive() -> Tuple[str, str, Optional[str]]:
    """Prompt user to choose between Without-AI, Local AI (GPU), and Cloud AI mode.
    Returns (mode, ai_provider, ai_model).
    """
    while True:
        console.print("\n[bold yellow]Choose Explanation Mode:[/bold yellow]")
        console.print("  [cyan][1][/cyan] [bold]Without-AI Explanation[/bold] (Deterministic Pure AST & Knowledge Engine - 100% Offline & Precise) [bold green][Default][/bold green]")
        console.print("  [cyan][2][/cyan] [bold]Local AI Explanation[/bold] (Local Ollama on GPU - 100% Offline & Private)")
        console.print("  [cyan][3][/cyan] [bold]Cloud AI Explanation[/bold] (Free Ultra-Fast Groq / Google Gemini / OpenAI - 300+ tok/sec Live Streaming)")
        mode_choice = Prompt.ask("Select mode", choices=["1", "2", "3"], default="1")

        if mode_choice == "1":
            return "static", "ollama", None

        elif mode_choice == "2":
            console.print("\n[bold yellow]Select Local AI Model (Ollama on GPU):[/bold yellow]")
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
                    continue
                elif m_select == manual_idx:
                    ai_model = Prompt.ask("Enter model identifier")
                    return "ai", "ollama", ai_model
                else:
                    ai_model = detected_models[int(m_select) - 1]
                    return "ai", "ollama", ai_model
            else:
                console.print("[yellow]No local Ollama models detected automatically.[/yellow]")
                console.print("  [cyan][1][/cyan] Enter Ollama model name manually")
                console.print("  [cyan][2][/cyan] [bold yellow]↩ GO BACK[/bold yellow] (Return to Main Menu)")
                m_select = Prompt.ask("Choose option", choices=["1", "2"], default="1")

                if m_select == "2":
                    console.print("[dim]Returning to main menu...[/dim]")
                    continue
                else:
                    ai_model = Prompt.ask(
                        "Enter Ollama model name",
                        default="hf.co/BlossomsAI/Qwen2.5-Coder-7B-Instruct-Uncensored-GGUF:Q6_K"
                    )
                    return "ai", "ollama", ai_model

        elif mode_choice == "3":
            console.print("\n[bold yellow]Select Cloud AI Provider:[/bold yellow]")
            console.print("  [cyan][1][/cyan] [bold]Groq Cloud[/bold] (⚡ 300+ tok/s - llama-3.3-70b-versatile) [bold green][Free][/bold green]")
            console.print("  [cyan][2][/cyan] [bold]Google Gemini[/bold] (gemini-2.0-flash / gemini-1.5-pro) [bold green][Free Tier][/bold green]")
            console.print("  [cyan][3][/cyan] [bold]OpenAI[/bold] (gpt-4o-mini / gpt-4o)")
            console.print("  [cyan][4][/cyan] [bold]OpenRouter[/bold] (meta-llama/llama-3.3-70b-instruct)")
            console.print("  [cyan][5][/cyan] [bold yellow]↩ GO BACK[/bold yellow] (Return to Main Menu)")
            cloud_choice = Prompt.ask("Choose cloud provider", choices=["1", "2", "3", "4", "5"], default="1")

            if cloud_choice == "5":
                continue

            provider_map = {
                "1": ("groq", "llama-3.3-70b-versatile"),
                "2": ("gemini", "gemini-2.0-flash"),
                "3": ("openai", "gpt-4o-mini"),
                "4": ("openrouter", "meta-llama/llama-3.3-70b-instruct"),
            }
            provider, default_model = provider_map[cloud_choice]

            # Check if API key exists
            api_key = CloudAIProvider.get_saved_api_key(provider)
            if not api_key:
                prov_info = CloudAIProvider.SUPPORTED_PROVIDERS.get(provider, {})
                env_var = prov_info.get("env_var", f"{provider.upper()}_API_KEY")
                doc_url = prov_info.get("doc", "")
                console.print(f"\n[yellow]No API key found in environment ({env_var}) or config file.[/yellow]")
                if doc_url:
                    console.print(f"[dim]{doc_url}[/dim]")
                api_key = Prompt.ask(f"Enter {provider.capitalize()} API key", password=True)
                if not api_key:
                    console.print("[red]API key is required for Cloud AI. Returning to menu...[/red]")
                    continue
                save_key = Prompt.ask("Save key locally in ~/.explainer/cloud_config.json for future use?", choices=["y", "n"], default="y")
                if save_key.lower() == "y":
                    CloudAIProvider.save_api_key(provider, api_key)
                    console.print("[green]✓ Key saved successfully.[/green]")
                else:
                    os.environ[env_var] = api_key

            custom_model = Prompt.ask(f"Model to use (Press Enter for default: [bold cyan]{default_model}[/bold cyan])", default=default_model)
            return "ai", provider, custom_model


def interactive_wizard():
    console.print()
    console.print("[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold white] ⚡ EXPL - Codebase & File Architecture Explainer Engine[/bold white]")
    console.print("[dim]   Deep Code Architecture, Tech Stack & File-by-File Breakdown[/dim]")
    console.print("[bold cyan]════════════════════════════════════════════════════════════════════[/bold cyan]")
    console.print()

    current_cwd = Path.cwd().resolve()
    console.print(f"[bold]📁 Current Codebase:[/bold] [underline white]{current_cwd}[/underline white]")

    # Select Mode
    mode, ai_provider, ai_model = select_mode_interactive()
    ai_endpoint = "http://localhost:11434/api/generate"

    codebase_folder_name = current_cwd.name or "Codebase"
    expl_folder_name = f"{codebase_folder_name}-EXPL"
    expl_output_dir = current_cwd / expl_folder_name

    if expl_output_dir.exists():
        console.print()
        console.print(f"[bold yellow]📁 Existing explanation folder '[white]{expl_folder_name}[/white]' already exists.[/bold yellow]")
        console.print("  [cyan][1][/cyan] [bold green]Update & refresh existing folder[/bold green] [dim](Default / Clean update)[/dim]")
        console.print("  [cyan][2][/cyan] [bold cyan]Create a new timestamped folder[/bold cyan] [dim](Keep both)[/dim]")
        folder_choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")
        if folder_choice == "2":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            expl_folder_name = f"{codebase_folder_name}-EXPL-{timestamp}"
            expl_output_dir = current_cwd / expl_folder_name
            console.print(f"[bold cyan]📁 Will generate new folder:[/bold cyan] [bold white]{expl_folder_name}[/bold white]")
        else:
            console.print(f"[bold green]🔄 Will update existing folder:[/bold green] [bold white]{expl_folder_name}[/bold white]")

    codebase_analysis = run_core_analysis(
        target_path=str(current_cwd),
        mode=mode,
        ai_provider=ai_provider,
        ai_endpoint=ai_endpoint,
        ai_model=ai_model
    )

    with console.status("[bold green]Writing individual file explanations to folder...[/bold green]"):
        md_renderer = MarkdownRenderer()
        md_renderer.render_multi_file_dossier(codebase_analysis, str(expl_output_dir))

    file_count = len(codebase_analysis.files)
    console.print()
    console.print("[bold green]════════════════════════════════════════════════════════════════════[/bold green]")
    console.print(f"[bold white] ✔ Work has been done successfully![/bold white]")
    console.print(f"[bold cyan] 📁 Created Folder:[/bold cyan] [bold white]{expl_folder_name}[/bold white]")
    console.print(f"[dim]    • Generated separate detailed explanations for each of the {file_count} files in:[/dim] [white]{expl_folder_name}/files/[/white]")
    console.print(f"[dim]    • Generated Master Architecture Index in:[/dim] [white]{expl_folder_name}/INDEX.md[/white]")
    console.print("[bold green]════════════════════════════════════════════════════════════════════[/bold green]")
    console.print()

    console.print("[bold cyan]🔍 Opening Codebase Explanation in CLI Interface...[/bold cyan]\n")
    terminal_renderer = RichTerminalRenderer()
    terminal_renderer.render(codebase_analysis, inspect_file=None)
    run_cli_file_inspector(codebase_analysis)


def run_cli_file_inspector(codebase_analysis):
    """Allows user to interactively inspect any file explanation in terminal."""
    file_keys = sorted(list(codebase_analysis.files.keys()))
    if not file_keys:
        return

    terminal_renderer = RichTerminalRenderer()

    while True:
        console.print("\n[bold cyan]🔎 Inspect Individual File Breakdown in CLI:[/bold cyan]")
        console.print("Enter file number, 'ai <num>' for live AI streaming, 'all', or 'q' to quit:")
        for idx, f_path in enumerate(file_keys, 1):
            fa = codebase_analysis.files[f_path]
            console.print(f"  [cyan][{idx}][/cyan] {f_path} [dim]({fa.language} • {fa.line_count} LOC)[/dim]")

        user_input = Prompt.ask("\nSelect file to inspect", default="q")
        u_clean = user_input.strip()
        if u_clean.lower() in ("q", "quit", "exit"):
            console.print("[dim]Exiting CLI Inspector. All files remain saved in your `-EXPL` folder.[/dim]\n")
            break
        elif u_clean.lower().startswith("ai "):
            arg = u_clean[3:].strip()
            target_f = resolve_file_key(arg, file_keys, codebase_analysis.files)
            if target_f:
                fa = codebase_analysis.files[target_f]
                run_single_file_cli(
                    filepath=fa.file_path,
                    mode="ai",
                    ai_provider=codebase_analysis.ai_provider or "ollama",
                    ai_model=codebase_analysis.ai_model_name,
                    stream=True
                )
            else:
                console.print(f"[red]Invalid file selection: '{arg}'.[/red]")
            continue
        elif u_clean.lower() == "all":
            for f_path in file_keys:
                terminal_renderer.render(codebase_analysis, inspect_file=f_path)
            break
        else:
            selected_path = resolve_file_key(u_clean, file_keys, codebase_analysis.files)
            if selected_path:
                terminal_renderer.render(codebase_analysis, inspect_file=selected_path)
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

    registry = ParserRegistry()
    analyzed_files = {}

    with console.status("[bold green]Extracting AST, tags, components, and concepts across all files...[/bold green]"):
        for fpath, rel_path in scanned_files:
            if "-EXPL" in rel_path:
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
                parser = registry.get_parser_for_path(fpath)
                analysis = parser.parse(str(fpath), content, rel_path)
                analyzed_files[rel_path] = analysis
            except Exception as e:
                console.print(f"[dim yellow]Warning: Failed to parse {rel_path}: {e}[/dim yellow]")

    with console.status("[bold green]Resolving cross-file dependency graph and mechanics...[/bold green]"):
        dep_builder = DependencyGraphBuilder(analyzed_files)
        interconnections = dep_builder.build_interconnections()

    with console.status("[bold green]Analyzing technology stack & ecosystem compatibility...[/bold green]"):
        ts_analyzer = TechStackAnalyzer(str(target_p if target_p.is_dir() else target_p.parent))
        tech_stack = ts_analyzer.analyze(analyzed_files)

    if mode == "ai":
        engine = AIExplainerEngine(
            endpoint_url=ai_endpoint,
            model_name=ai_model,
            provider=ai_provider
        )
        if ai_provider == "ollama":
            engine.ensure_ollama_running()
            console.print(f"\n[bold magenta]🧠 Connected to Local AI Model: [bold white]{engine.model_name}[/bold white] via {ai_provider}[/bold magenta]")
        else:
            console.print(f"\n[bold magenta]⚡ Connected to Cloud AI Provider: [bold white]{ai_provider.upper()} ({engine.model_name})[/bold white][/bold magenta]")
        console.print("[dim]Streaming neural architecture synthesis and per-file breakdowns word-by-word...[/dim]\n")

        def on_ai_file_progress(curr: int, total: int, fpath: str):
            console.print(f"\n\n[bold magenta]════════════════════════════════════════════════════════════════════\n  🧠 [AI {curr}/{total}] Live Streaming Breakdown for: [bold white]{fpath}[/bold white] [cyan]({engine.model_name})[/cyan]\n════════════════════════════════════════════════════════════════════[/bold magenta]\n")

        console.print("[bold cyan]🏛️ Synthesizing System Architecture Review (Streaming Live):[/bold cyan]\n")
        codebase_analysis = engine.analyze_codebase(
            root_path=str(target_p),
            files=analyzed_files,
            tech_stack=tech_stack,
            interconnections=interconnections,
            progress_callback=on_ai_file_progress,
            stream_callback=_flush_token
        )
        console.print("\n")
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


def run_single_file_cli(
    filepath: str,
    mode: Optional[str] = None,
    ai_provider: str = "ollama",
    ai_endpoint: str = "http://localhost:11434/api/generate",
    ai_model: Optional[str] = None,
    stream: bool = True
):
    """Direct single-file explainer with live streaming and line-by-line breakdown."""
    if RemoteResolver.is_remote_url(filepath):
        local_path, _, _ = RemoteResolver.resolve(filepath)
        file_path = local_path.resolve()
    else:
        file_path = Path(filepath).resolve()

    if not file_path.exists() or not file_path.is_file():
        console.print(f"[bold red]❌ Error: File '{filepath}' does not exist or is not a valid file.[/bold red]")
        sys.exit(1)

    registry = ParserRegistry()
    parser = registry.get_parser_for_path(file_path)
    content = file_path.read_text(encoding="utf-8", errors="replace")
    fa = parser.parse(str(file_path), content, file_path.name)

    # Prompt for mode if not provided via flags
    if not mode:
        console.print(f"\n[bold cyan]📄 Direct File Explainer:[/bold cyan] [bold white]{file_path.name}[/bold white] [dim]({fa.language} • {fa.line_count} LOC)[/dim]")
        mode, ai_provider, ai_model = select_mode_interactive()

    terminal_renderer = RichTerminalRenderer()

    if mode == "ai":
        engine = AIExplainerEngine(
            endpoint_url=ai_endpoint,
            model_name=ai_model,
            provider=ai_provider
        )
        if ai_provider == "ollama":
            engine.ensure_ollama_running()
            console.print(f"\n[bold magenta]🧠 Querying Local AI Model: [bold white]{engine.model_name}[/bold white][/bold magenta]")
        else:
            console.print(f"\n[bold magenta]⚡ Querying Cloud AI ({ai_provider.upper()}): [bold white]{engine.model_name}[/bold white][/bold magenta]")
        console.print("[dim]Streaming live token-by-token line walkthrough...[/dim]\n")

        # Create dummy codebase wrapper for prompt context
        dummy_codebase = CodebaseAnalysis(
            root_path=str(file_path.parent),
            project_name=file_path.parent.name or "Project",
            total_files=1,
            total_lines=fa.line_count,
            tech_stack=TechStackInfo(languages={fa.language: 1}),
            files={fa.relative_path: fa},
            architecture_style="Modular File Component",
            architecture_summary=f"Single source file ({fa.language}) within {file_path.parent.name}."
        )

        ai_out = engine._query_file_analysis(
            fa=fa,
            codebase=dummy_codebase,
            root_path=str(file_path.parent),
            stream_callback=_flush_token if stream else None
        )
        console.print("\n")
        fa.ai_insights = ai_out
        fa.ai_model_used = engine.model_name

        # Also render standard AST elements if present
        if not stream:
            terminal_renderer.render_single_file(fa, project_name=file_path.parent.name)
    else:
        # Deterministic Without-AI mode
        terminal_renderer.render_single_file(fa, project_name=file_path.parent.name)


def run_git_diff_cli(
    ref: Optional[str] = None,
    mode: Optional[str] = None,
    staged: bool = False,
    ai_provider: str = "ollama",
    ai_endpoint: str = "http://localhost:11434/api/generate",
    ai_model: Optional[str] = None,
    stream: bool = True
):
    """Executes git diff analysis line-by-line & word-by-word."""
    explainer = GitDiffExplainer()
    raw_diff, ref_label = explainer.get_git_diff(ref=ref, staged=staged)

    if not raw_diff.strip():
        console.print(f"[bold green]✓ No code changes detected in Git diff ({ref_label}). Working tree clean![/bold green]")
        return

    diff_files = explainer.parse_diff(raw_diff)
    if not diff_files:
        console.print("[bold yellow]No source file changes detected in diff.[/bold yellow]")
        return

    total_added = sum(len(f.added_lines) for f in diff_files)
    console.print(f"\n[bold cyan]🔍 Git Diff Detected:[/bold cyan] [bold white]{len(diff_files)} file(s) changed[/bold white], [bold green]+{total_added} added lines[/bold green] [dim]({ref_label})[/dim]")

    if not mode:
        mode, ai_provider, ai_model = select_mode_interactive()

    ai_engine = None
    if mode == "ai":
        ai_engine = AIExplainerEngine(
            endpoint_url=ai_endpoint,
            model_name=ai_model,
            provider=ai_provider
        )
        if ai_provider == "ollama":
            ai_engine.ensure_ollama_running()
            console.print(f"\n[bold magenta]🧠 Streaming Git Diff AI Walkthrough with: [bold white]{ai_engine.model_name}[/bold white][/bold magenta]\n")
        else:
            console.print(f"\n[bold magenta]⚡ Streaming Git Diff Cloud AI Walkthrough ({ai_provider.upper()}): [bold white]{ai_engine.model_name}[/bold white][/bold magenta]\n")

    analysis = explainer.analyze_diff(
        files=diff_files,
        ref_label=ref_label,
        mode=mode or "static",
        ai_engine=ai_engine,
        stream_callback=_flush_token if stream else None
    )

    console.print()
    terminal_renderer = RichTerminalRenderer()
    terminal_renderer.render_diff(analysis)


def run_remote_cli(
    url: str,
    mode: Optional[str] = None,
    ai_provider: str = "ollama",
    ai_endpoint: str = "http://localhost:11434/api/generate",
    ai_model: Optional[str] = None,
    stream: bool = True,
    fmt: str = "all",
    output_dir: Optional[str] = None
):
    """Resolves a remote URL (Git repo or raw file) and explains it."""
    console.print(f"\n[bold cyan]🌐 Fetching remote source:[/bold cyan] [underline white]{url}[/underline white]")
    try:
        with console.status("[bold green]Resolving remote Git repo / file...[/bold green]"):
            local_path, is_single_file, label = RemoteResolver.resolve(url)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to resolve remote URL:[/bold red] {e}")
        sys.exit(1)

    console.print(f"[bold green]✓ Downloaded/Cloned successfully:[/bold green] [white]{label}[/white]")
    console.print(f"[dim]Cached at: {local_path}[/dim]\n")

    if is_single_file:
        run_single_file_cli(
            filepath=str(local_path),
            mode=mode,
            ai_provider=ai_provider,
            ai_endpoint=ai_endpoint,
            ai_model=ai_model,
            stream=stream
        )
    else:
        run_cli_scan(
            path=str(local_path),
            mode=mode or "static",
            fmt=fmt,
            ai_provider=ai_provider,
            ai_endpoint=ai_endpoint,
            ai_model=ai_model,
            inspect=None,
            output_dir=output_dir
        )


@main.command(name="explain_file")
@click.argument("filepath", type=click.Path())
@click.option("--mode", type=click.Choice(["static", "ai"]), default=None, help="Explanation mode: 'static' (Without-AI) or 'ai' (LLM).")
@click.option("--ai-provider", type=click.Choice(AI_PROVIDER_CHOICES), default="ollama", help="AI provider (local Ollama or cloud).")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default=None, help="AI model identifier.")
@click.option("--stream/--no-stream", default=True, help="Enable live token streaming for AI mode.")
def explain_file_cmd(filepath, mode, ai_provider, ai_endpoint, ai_model, stream):
    """Direct line-by-line & word-by-word explanation of an individual file."""
    run_single_file_cli(filepath, mode, ai_provider, ai_endpoint, ai_model, stream)


@main.command(name="diff")
@click.argument("ref", required=False, default=None)
@click.option("--mode", type=click.Choice(["static", "ai"]), default=None, help="Explanation mode: 'static' or 'ai'.")
@click.option("--staged", is_flag=True, help="Explain staged git changes.")
@click.option("--ai-provider", type=click.Choice(AI_PROVIDER_CHOICES), default="ollama", help="AI provider (local Ollama or cloud).")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default=None, help="AI model identifier.")
@click.option("--stream/--no-stream", default=True, help="Enable live token streaming for AI mode.")
def diff_cmd(ref, mode, staged, ai_provider, ai_endpoint, ai_model, stream):
    """Explain Git diff changes line-by-line & word-by-word for modified/added lines."""
    run_git_diff_cli(ref, mode, staged, ai_provider, ai_endpoint, ai_model, stream)


@main.command(name="remote")
@click.argument("url")
@click.option("--mode", type=click.Choice(["static", "ai"]), default=None, help="Explanation mode: 'static' or 'ai'.")
@click.option("--ai-provider", type=click.Choice(AI_PROVIDER_CHOICES), default="ollama", help="AI provider (local Ollama or cloud).")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default=None, help="AI model identifier.")
@click.option("--stream/--no-stream", default=True, help="Enable live token streaming for AI mode.")
@click.option("--format", "fmt", type=click.Choice(["terminal", "markdown", "all"]), default="all", help="Output format.")
@click.option("--output-dir", default=None, help="Directory to save generated markdown files.")
def remote_cmd(url, mode, ai_provider, ai_endpoint, ai_model, stream, fmt, output_dir):
    """Explain a remote Git repository or single file from a URL."""
    run_remote_cli(url, mode, ai_provider, ai_endpoint, ai_model, stream, fmt, output_dir)


main.add_command(remote_cmd, name="explain_remote")


@main.command(name="analyze")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["static", "ai"]), default="static", help="Engine mode: 'static' (Zero-AI) or 'ai' (LLM).")
@click.option("--format", "fmt", type=click.Choice(["terminal", "markdown", "all"]), default="all", help="Output format.")
@click.option("--ai-provider", type=click.Choice(AI_PROVIDER_CHOICES), default="ollama", help="AI provider (local Ollama or cloud).")
@click.option("--ai-endpoint", default="http://localhost:11434/api/generate", help="Local AI endpoint URL.")
@click.option("--ai-model", default=None, help="AI model identifier.")
@click.option("--inspect", default=None, help="Specific relative file to inspect deeply in terminal.")
@click.option("--output-dir", default=None, help="Directory to save generated markdown files.")
def analyze_cmd(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir):
    """Analyze a repository or folder from CLI flags."""
    run_cli_scan(path, mode, fmt, ai_provider, ai_endpoint, ai_model, inspect, output_dir)


main.add_command(analyze_cmd, name="scan")


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

    if fmt in ("terminal", "all"):
        terminal_renderer = RichTerminalRenderer()
        terminal_renderer.render(analysis, inspect_file=inspect)

    console.print(f"[bold green]✔ Complete multi-file dossier generated in:[/bold green] [underline white]{out_dir}[/underline white]")
    return analysis, out_dir


if __name__ == "__main__":
    main()
