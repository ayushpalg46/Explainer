import json
import subprocess
import shutil
import time
from pathlib import Path
import requests
from typing import Dict, List, Optional, Tuple, Callable
from ..models import CodebaseAnalysis, FileAnalysis, TechStackInfo, FileInterconnection
from .rule_engine import RuleExplainerEngine


class AIExplainerEngine:
    """
    Augments deterministic AST & Knowledge facts with real local AI model analysis
    (Ollama, LM Studio, or OpenAI-compatible local endpoints).
    Features native auto-detection for installed models (e.g. Qwen2.5-Coder and Qwen3.5).
    Performs true two-tier AI generation:
      1. High-level System Architecture & Technical Debt Review
      2. Per-file Deep Neural Code Analysis (Mechanics, Design Patterns, Interconnections)
    """

    DEFAULT_CODER_MODEL = "hf.co/BlossomsAI/Qwen2.5-Coder-7B-Instruct-Uncensored-GGUF:Q6_K"
    DEFAULT_GENERAL_MODEL = "qwen35-uncensored:latest"

    def __init__(
        self,
        endpoint_url: str = "http://localhost:11434/api/generate",
        model_name: Optional[str] = None,
        provider: str = "ollama"  # 'ollama' or 'openai_compatible'
    ):
        self.endpoint_url = endpoint_url
        self.provider = provider
        self.rule_engine = RuleExplainerEngine()

        # If model_name is not provided or generic, auto-resolve to best available local model
        if not model_name or model_name == "llama3":
            installed = self.list_installed_models()
            if installed:
                coder_candidates = [m for m in installed if "coder" in m.lower()]
                self.model_name = coder_candidates[0] if coder_candidates else installed[0]
            else:
                self.model_name = self.DEFAULT_CODER_MODEL
        else:
            self.model_name = model_name

    @classmethod
    def ensure_ollama_running(cls, host: str = "http://localhost:11434") -> bool:
        """Checks if Ollama server is responding; if not, attempts to start it in the background."""
        try:
            res = requests.get(f"{host.rstrip('/')}/api/tags", timeout=1.5)
            if res.status_code == 200:
                return True
        except Exception:
            pass

        ollama_bin = shutil.which("ollama")
        if not ollama_bin:
            import os
            appdata = os.environ.get("LOCALAPPDATA", "")
            candidate = os.path.join(appdata, "Programs", "Ollama", "ollama.exe")
            if os.path.exists(candidate):
                ollama_bin = candidate

        if ollama_bin:
            try:
                subprocess.Popen(
                    [ollama_bin, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                time.sleep(2.0)
                res = requests.get(f"{host.rstrip('/')}/api/tags", timeout=2.0)
                return res.status_code == 200
            except Exception:
                return False

        return False

    @classmethod
    def list_installed_models(cls, host: str = "http://localhost:11434") -> List[str]:
        """Fetches the list of all currently installed Ollama models."""
        cls.ensure_ollama_running(host)
        try:
            res = requests.get(f"{host.rstrip('/')}/api/tags", timeout=3.0)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", []) if m.get("name")]
        except Exception:
            pass
        return []

    def analyze_codebase(
        self,
        root_path: str,
        files: Dict[str, FileAnalysis],
        tech_stack: TechStackInfo,
        interconnections: List[FileInterconnection],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> CodebaseAnalysis:
        # Step 1: Compute high-precision baseline analysis using the static AST engine
        base_analysis = self.rule_engine.analyze_codebase(
            root_path, files, tech_stack, interconnections
        )
        base_analysis.engine_used = f"Local AI Model ({self.model_name} via {self.provider})"
        base_analysis.ai_model_name = self.model_name

        # Step 2: System-level AI Architectural Synthesis
        ai_narrative = self._query_architecture(base_analysis)
        if ai_narrative:
            base_analysis.ai_architecture_critique = ai_narrative

        # Step 3: Per-File Deep Neural Analysis
        file_items = list(base_analysis.files.items())
        total_files = len(file_items)

        for idx, (rel_path, fa) in enumerate(file_items, 1):
            if progress_callback:
                progress_callback(idx, total_files, rel_path)

            file_ai_insight = self._query_file_analysis(fa, base_analysis, root_path)
            if file_ai_insight:
                fa.ai_insights = file_ai_insight
                fa.ai_model_used = self.model_name

        return base_analysis

    def _query_architecture(self, base_analysis: CodebaseAnalysis) -> Optional[str]:
        """Queries the local AI model for deep codebase architectural synthesis."""
        prompt = (
            f"You are a principal software architect. Review this codebase structural profile and produce "
            f"a comprehensive, highly insightful architectural assessment:\n\n"
            f"Project: {base_analysis.project_name}\n"
            f"Total Files: {base_analysis.total_files}, Total Lines: {base_analysis.total_lines:,}\n"
            f"Detected Tech Stack: {base_analysis.tech_stack.compatibility_analysis}\n"
            f"Languages: {json.dumps(base_analysis.tech_stack.languages)}\n"
            f"Frameworks & Tooling: {', '.join(base_analysis.tech_stack.frameworks or ['None identified'])}\n"
            f"Cross-File Interconnections: {len(base_analysis.interconnections)} inter-module relationships.\n\n"
            f"In your response, explain:\n"
            f"1. **Architectural Paradigm**: Identify and justify the overall architecture pattern (e.g. Full-Stack Polyglot, Monolith, Component-Driven).\n"
            f"2. **Data & Execution Flow**: How runtime requests, styling, and data travel across these layers.\n"
            f"3. **Production Strengths & Recommendations**: Critical evaluation of scalability, testability, and edge cases.\n"
            f"Format clearly in GitHub Markdown with bullet points (under 250 words)."
        )

        return self._send_prompt(prompt, max_tokens=400, temperature=0.2)

    def _query_file_analysis(
        self,
        fa: FileAnalysis,
        codebase: CodebaseAnalysis,
        root_path: str
    ) -> Optional[str]:
        """Queries the local AI model for a deep, file-specific technical explanation."""
        # Read snippet of file content from disk safely
        content_snippet = ""
        try:
            full_path = Path(fa.file_path)
            if not full_path.is_absolute():
                full_path = Path(root_path) / fa.relative_path
            if full_path.exists():
                raw = full_path.read_text(encoding="utf-8", errors="replace")
                lines = raw.splitlines()
                # Feed first 120 lines or 4500 chars to avoid exceeding model context
                if len(lines) > 120:
                    content_snippet = "\n".join(lines[:120]) + f"\n... [Truncated: {len(lines) - 120} more lines]"
                else:
                    content_snippet = raw[:4500]
        except Exception:
            content_snippet = "(File content unavailable)"

        # Collect inbound & outbound relationship names
        outbound_desc = [f"{c.relation_type} -> {c.target_file}" for c in fa.outbound_connections] or ["None"]
        inbound_desc = [f"used by {c.source_file} ({c.relation_type})" for c in fa.inbound_connections] or ["None"]
        element_sample = [f"{e.kind}: {e.name}" for e in fa.elements[:8]]

        prompt = (
            f"You are a staff software engineer and technical educator. Perform a deep, authoritative code analysis "
            f"for this specific file in the '{codebase.project_name}' project:\n\n"
            f"File: `{fa.relative_path}`\n"
            f"Language: {fa.language} | Lines: {fa.line_count}\n"
            f"Role Identified: {fa.role_in_codebase}\n"
            f"Dependencies: Outbound: [{', '.join(outbound_desc)}] | Inbound: [{', '.join(inbound_desc)}]\n"
            f"Key Symbols Detected: [{', '.join(element_sample)}]\n\n"
            f"Source Code:\n```\n{content_snippet}\n```\n\n"
            f"Provide a structured Markdown breakdown:\n"
            f"- **Core Purpose & Engineering Rationale**: Why this file exists and how it contributes to the application.\n"
            f"- **Mechanics & Implementation Highlights**: Key logic flow, syntax techniques, state handling, or algorithms used.\n"
            f"- **Interconnection Rationale**: How and why it integrates with its dependencies ({', '.join(outbound_desc)}).\n"
            f"- **Production Considerations**: Edge cases, performance nuances, or best practices.\n"
            f"Keep it concise, highly technical, and directly tied to the code above."
        )

        return self._send_prompt(prompt, max_tokens=450, temperature=0.2)

    def _send_prompt(self, prompt: str, max_tokens: int = 350, temperature: float = 0.2) -> Optional[str]:
        """Sends a prompt to the local AI endpoint with robust timeout and error reporting."""
        try:
            if self.provider == "ollama":
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
                res = requests.post(self.endpoint_url, json=payload, timeout=120)
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "").strip()
                    if response_text:
                        return response_text
                else:
                    return f"*AI Generation Notice*: Ollama returned HTTP {res.status_code}: {res.text[:100]}"

            elif self.provider == "openai_compatible":
                url = self.endpoint_url
                if not url.endswith("/chat/completions"):
                    url = url.rstrip("/") + "/chat/completions"
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": "You are an expert software engineer and codebase explainer."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                res = requests.post(url, json=payload, timeout=120)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
                else:
                    return f"*AI Generation Notice*: Local AI server returned HTTP {res.status_code}: {res.text[:100]}"

        except requests.exceptions.Timeout:
            return "*AI Generation Notice*: Local model request timed out (>120s)."
        except requests.exceptions.ConnectionError:
            return "*AI Generation Notice*: Could not connect to local AI server at " + self.endpoint_url
        except Exception as e:
            return f"*AI Generation Notice*: Error querying local AI: {str(e)}"

        return None
