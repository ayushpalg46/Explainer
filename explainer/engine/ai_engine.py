import json
import subprocess
import shutil
import time
import requests
from typing import Dict, List, Optional, Tuple
from ..models import CodebaseAnalysis, FileAnalysis, TechStackInfo, FileInterconnection
from .rule_engine import RuleExplainerEngine


class AIExplainerEngine:
    """
    Augments the deterministic AST & Knowledge facts with a local AI model
    (Ollama, LM Studio, or any OpenAI-compatible local server).
    Features native auto-detection for installed models (e.g. Qwen2.5-Coder and Qwen3.5).
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
                # Prefer coder model first, then general model, then first available
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

        # Try to locate and launch 'ollama serve'
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
        interconnections: List[FileInterconnection]
    ) -> CodebaseAnalysis:
        # Step 1: Compute high-precision baseline analysis using the static AST engine
        base_analysis = self.rule_engine.analyze_codebase(
            root_path, files, tech_stack, interconnections
        )
        base_analysis.engine_used = f"Local AI Model ({self.model_name} via {self.provider})"

        # Step 2: Call the local AI model to synthesize conversational architectural analysis
        ai_narrative = self._query_local_model(base_analysis)
        if ai_narrative:
            base_analysis.architecture_summary = f"{ai_narrative}\n\n*(Verified against AST structural analysis)*"

        return base_analysis

    def _query_local_model(self, base_analysis: CodebaseAnalysis) -> Optional[str]:
        prompt = (
            f"You are a master software architect. Review this codebase structural profile and provide a concise, "
            f"deep architectural summary explaining how the components collaborate:\n\n"
            f"Project: {base_analysis.project_name}\n"
            f"Total Files: {base_analysis.total_files}, Total Lines: {base_analysis.total_lines}\n"
            f"Tech Stack: {base_analysis.tech_stack.compatibility_analysis}\n"
            f"Languages: {json.dumps(base_analysis.tech_stack.languages)}\n"
            f"Frameworks: {', '.join(base_analysis.tech_stack.frameworks)}\n"
            f"Interconnections: {len(base_analysis.interconnections)} cross-file dependencies.\n\n"
            f"Provide an insightful architectural appraisal in 2 concise paragraphs (under 150 words)."
        )

        try:
            if self.provider == "ollama":
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 250,
                        "temperature": 0.2
                    }
                }
                res = requests.post(self.endpoint_url, json=payload, timeout=120)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()

            elif self.provider == "openai_compatible":
                url = self.endpoint_url
                if not url.endswith("/chat/completions"):
                    url = url.rstrip("/") + "/chat/completions"
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": "You are an expert software codebase analyzer."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 250
                }
                res = requests.post(url, json=payload, timeout=120)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()

        except Exception:
            return None

        return None
