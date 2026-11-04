"""
AI Model Integration & Adapter for Explainer.
Supports local Ollama servers, local GGUF models, and OpenAI-compatible endpoints.
Enriches the deterministic analysis when enabled, with automatic fallback when offline.
"""
import os
import json
from typing import Dict, Any, List, Optional
import httpx


class AIEngineAdapter:
    DEFAULT_OLLAMA_URL = "http://localhost:11434"
    KNOWN_MODEL_PATHS = [
        r"D:\AI\Models\Qwen35-Uncensored\Qwen3.5-9B-Uncensored-Q4_K_M.gguf",
    ]

    def __init__(self, endpoint_url: Optional[str] = None, model_name: Optional[str] = None):
        self.endpoint_url = endpoint_url or os.environ.get("OLLAMA_HOST", self.DEFAULT_OLLAMA_URL)
        self.model_name = model_name or os.environ.get("EXPLAINER_MODEL", "")
        self._is_available: Optional[bool] = None
        self._available_models: List[str] = []

    def check_availability(self) -> Dict[str, Any]:
        """Checks if local Ollama or AI endpoints are responding."""
        models = []
        status = "offline"

        # Check local files first
        local_ggufs = [p for p in self.KNOWN_MODEL_PATHS if os.path.exists(p)]

        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.endpoint_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    status = "online"
                    self._is_available = True
                    self._available_models = models
                    if not self.model_name and models:
                        self.model_name = models[0]
        except Exception:
            self._is_available = False

        return {
            "status": status,
            "endpoint": self.endpoint_url,
            "models": models,
            "active_model": self.model_name,
            "local_gguf_files": local_ggufs
        }

    def enrich_explanation(self, file_explanation: Dict[str, Any], prompt_style: str = "elaborated") -> Optional[str]:
        """
        Queries the local AI model to provide an augmented narrative explanation.
        """
        avail = self.check_availability()
        if avail["status"] != "online" or not self.model_name:
            return None

        prompt = (
            f"You are an expert software architect. Provide a super detailed, elaborated explanation "
            f"for this file based on its structural breakdown:\n\n"
            f"File: {file_explanation['header']['filename']}\n"
            f"Language: {file_explanation['header']['language']}\n"
            f"Role: {file_explanation['header']['role']}\n"
            f"Tech Stack: {', '.join(file_explanation['purpose_and_context']['tech_stack_ecosystem'])}\n"
            f"Key Symbols: {[s['name'] for s in file_explanation['symbol_breakdown'][:10]]}\n"
            f"Interconnections: {file_explanation['interconnections']['outgoing']}\n\n"
            f"Explain in deep detail: What this file does, how every key component works, how and why "
            f"it connects to other files, and its architectural significance."
        )

        try:
            with httpx.Client(timeout=30.0) as client:
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                }
                res = client.post(f"{self.endpoint_url}/api/generate", json=payload)
                if res.status_code == 200:
                    return res.json().get("response", "").strip()
        except Exception:
            return None

        return None
