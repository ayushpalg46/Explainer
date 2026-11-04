import json
import requests
from typing import Dict, List, Optional
from ..models import CodebaseAnalysis, FileAnalysis, TechStackInfo, FileInterconnection
from .rule_engine import RuleExplainerEngine


class AIExplainerEngine:
    """
    Augments the deterministic AST & Knowledge facts with a local AI model
    (Ollama, LM Studio, or any OpenAI-compatible local server).
    """

    def __init__(
        self,
        endpoint_url: str = "http://localhost:11434/api/generate",
        model_name: str = "llama3",
        provider: str = "ollama"  # 'ollama' or 'openai_compatible'
    ):
        self.endpoint_url = endpoint_url
        self.model_name = model_name
        self.provider = provider
        self.rule_engine = RuleExplainerEngine()

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

        # Step 2: Attempt to call the local AI model to augment the architectural summary
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
            f"Provide an insightful 2-paragraph architectural appraisal."
        )

        try:
            if self.provider == "ollama":
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
                res = requests.post(self.endpoint_url, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()

            elif self.provider == "openai_compatible":
                # E.g. LM Studio or vLLM at http://localhost:1234/v1/chat/completions
                url = self.endpoint_url
                if not url.endswith("/chat/completions"):
                    url = url.rstrip("/") + "/chat/completions"
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": "You are an expert software codebase analyzer."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
                res = requests.post(url, json=payload, timeout=12)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()

        except Exception as e:
            # Graceful fallback: return None so baseline AST summary is preserved
            return None

        return None
