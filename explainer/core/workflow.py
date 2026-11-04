"""
Workflow and Mode Selection Engine for Explainer.
Prompts users to choose between Deterministic Deep Mode (No AI) and AI-Powered Mode.
"""
from typing import Tuple
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from explainer.core.ai_engine import AIEngineAdapter


console = Console()


class WorkflowManager:
    @staticmethod
    def select_mode(cli_mode: str = "auto") -> Tuple[str, AIEngineAdapter]:
        """
        Resolves or prompts for the analysis mode.
        Returns: (mode, ai_adapter)
        """
        adapter = AIEngineAdapter()
        status = adapter.check_availability()

        if cli_mode in ("no-ai", "deterministic"):
            return "no-ai", adapter
        elif cli_mode == "ai":
            return "ai", adapter
        elif cli_mode == "hybrid":
            return "hybrid", adapter

        # Interactive Mode Selection
        has_ai = status["status"] == "online" and bool(status["models"])
        models_text = ", ".join(status["models"]) if status["models"] else "None currently active"
        gguf_info = f"\n[dim]Local model detected on disk: {status['local_gguf_files'][0]}[/dim]" if status["local_gguf_files"] else ""

        mode_intro = (
            f"[bold cyan]Explainer - Intelligent Codebase Engine[/bold cyan]\n"
            f"[dim]Select how you want Explainer to analyze and explain your codebase:[/dim]\n\n"
            f"[bold green]1) Deterministic Deep Engine (Without AI)[/bold green]\n"
            f"   • 100% Offline, Zero-Latency, Pure AST & Token Analysis\n"
            f"   • Identical structural depth, tag/symbol breakdown, and interconnection maps\n\n"
            f"[bold magenta]2) AI-Powered Engine (Local Ollama / Brain)[/bold magenta]\n"
            f"   • Status: [{'green' if has_ai else 'yellow'}]{status['status'].upper()}[/]\n"
            f"   • Available Models: {models_text}{gguf_info}\n\n"
            f"[bold blue]3) Hybrid Engine[/bold blue]\n"
            f"   • Combines high-precision AST rules with AI conversational synthesis\n"
        )
        console.print(Panel(mode_intro, border_style="cyan"))

        choice = Prompt.ask(
            "Choose execution mode",
            choices=["1", "2", "3"],
            default="1" if not has_ai else "3"
        )

        mapping = {"1": "no-ai", "2": "ai", "3": "hybrid"}
        chosen_mode = mapping.get(choice, "no-ai")

        if chosen_mode in ("ai", "hybrid") and not has_ai:
            console.print("[yellow]Notice: Local AI service is offline or unreachable. Falling back automatically to Deterministic Deep Engine (Parity Mode).[/yellow]")
            return "no-ai", adapter

        return chosen_mode, adapter
