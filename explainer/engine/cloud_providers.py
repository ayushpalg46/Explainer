import json
import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import requests


class CloudAIProvider:
    """
    Client for ultra-fast Cloud AI APIs (Groq, Google Gemini, OpenAI, OpenRouter)
    with real-time Server-Sent Events (SSE) token streaming.
    """

    CONFIG_FILE = Path.home() / ".explainer" / "cloud_config.json"

    SUPPORTED_PROVIDERS = {
        "groq": {
            "name": "Groq Cloud (Ultra-Fast 300+ tok/sec)",
            "default_model": "llama-3.3-70b-versatile",
            "env_var": "GROQ_API_KEY",
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "doc": "Get free API key at https://console.groq.com"
        },
        "gemini": {
            "name": "Google Gemini (Gemini 2.0 Flash)",
            "default_model": "gemini-2.0-flash",
            "env_var": "GEMINI_API_KEY",
            "url": "https://generativelanguage.googleapis.com/v1beta/models",
            "doc": "Get free API key at https://aistudio.google.com"
        },
        "openai": {
            "name": "OpenAI (GPT-4o-mini)",
            "default_model": "gpt-4o-mini",
            "env_var": "OPENAI_API_KEY",
            "url": "https://api.openai.com/v1/chat/completions",
            "doc": "Get API key at https://platform.openai.com"
        },
        "openrouter": {
            "name": "OpenRouter (Universal Open-Source Models)",
            "default_model": "meta-llama/llama-3.3-70b-instruct",
            "env_var": "OPENROUTER_API_KEY",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "doc": "Get API key at https://openrouter.ai"
        }
    }

    def __init__(
        self,
        provider: str = "groq",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.provider = provider.lower()
        if self.provider not in self.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported cloud provider: '{provider}'. Supported: {list(self.SUPPORTED_PROVIDERS.keys())}")

        self.info = self.SUPPORTED_PROVIDERS[self.provider]
        self.model = model or self.info["default_model"]
        self.api_key = api_key or self.get_saved_api_key(self.provider)

    @classmethod
    def get_saved_api_key(cls, provider: str) -> Optional[str]:
        """Loads API key from environment variable or ~/.explainer/cloud_config.json."""
        prov_info = cls.SUPPORTED_PROVIDERS.get(provider.lower())
        if prov_info:
            env_key = os.environ.get(prov_info["env_var"])
            if env_key:
                return env_key.strip()

        # Check local config file
        if cls.CONFIG_FILE.exists():
            try:
                cfg = json.loads(cls.CONFIG_FILE.read_text(encoding="utf-8"))
                return cfg.get(provider.lower())
            except Exception:
                pass
        return None

    @classmethod
    def save_api_key(cls, provider: str, api_key: str):
        """Persists API key to ~/.explainer/cloud_config.json for seamless future runs."""
        cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        cfg = {}
        if cls.CONFIG_FILE.exists():
            try:
                cfg = json.loads(cls.CONFIG_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        cfg[provider.lower()] = api_key.strip()
        cls.CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

    def stream_prompt(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int = 800,
        temperature: float = 0.3,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Routes prompt to the appropriate cloud provider with SSE token streaming."""
        if not self.api_key:
            return f"*Cloud AI Notice*: Missing API key for {self.info['name']}. Please set {self.info['env_var']} or enter it in CLI. {self.info['doc']}"

        if self.provider == "gemini":
            return self._stream_gemini(prompt, system_prompt, max_tokens, temperature, stream_callback)
        else:
            # Groq, OpenAI, and OpenRouter use standard OpenAI SSE format
            return self._stream_openai_compatible(prompt, system_prompt, max_tokens, temperature, stream_callback)

    def _stream_openai_compatible(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        stream_callback: Optional[Callable[[str], None]]
    ) -> Optional[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/ayushpalg46/Explainer"
            headers["X-Title"] = "CodeExplainer"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": bool(stream_callback)
        }

        try:
            res = requests.post(self.info["url"], headers=headers, json=payload, timeout=60, stream=bool(stream_callback))
            if res.status_code != 200:
                return f"*Cloud AI Notice ({self.provider})*: HTTP {res.status_code}: {res.text[:200]}"

            if stream_callback:
                full_tokens = []
                for line in res.iter_lines():
                    if line:
                        dec = line.decode("utf-8")
                        if dec.startswith("data: "):
                            d_str = dec[6:].strip()
                            if d_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(d_str)
                                tok = chunk["choices"][0].get("delta", {}).get("content", "")
                                if tok:
                                    full_tokens.append(tok)
                                    stream_callback(tok)
                            except Exception:
                                pass
                return "".join(full_tokens).strip()
            else:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.Timeout:
            return f"*Cloud AI Notice*: Request to {self.provider} timed out."
        except Exception as e:
            return f"*Cloud AI Notice*: Error querying {self.provider}: {str(e)}"

    def _stream_gemini(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int,
        temperature: float,
        stream_callback: Optional[Callable[[str], None]]
    ) -> Optional[str]:
        model_name = self.model
        url = f"{self.info['url']}/{model_name}:streamGenerateContent?alt=sse&key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60, stream=bool(stream_callback))
            if res.status_code != 200:
                return f"*Cloud AI Notice (Gemini)*: HTTP {res.status_code}: {res.text[:200]}"

            full_tokens = []
            for line in res.iter_lines():
                if line:
                    dec = line.decode("utf-8")
                    if dec.startswith("data: "):
                        d_str = dec[6:].strip()
                        try:
                            chunk = json.loads(d_str)
                            candidates = chunk.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    tok = p.get("text", "")
                                    if tok:
                                        full_tokens.append(tok)
                                        if stream_callback:
                                            stream_callback(tok)
                        except Exception:
                            pass
            return "".join(full_tokens).strip()
        except requests.exceptions.Timeout:
            return "*Cloud AI Notice*: Request to Gemini timed out."
        except Exception as e:
            return f"*Cloud AI Notice*: Error querying Gemini: {str(e)}"
