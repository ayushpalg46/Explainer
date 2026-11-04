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
    Instructs the AI model as a World-Class Senior Developer & System Architect
    explaining code to a complete beginner / 4-year-old child with zero prior knowledge.
    Walks through what is actually written on the codefile line-by-line, tag-by-tag,
    and class-by-class using fun real-world analogies.
    """

    DEFAULT_CODER_MODEL = "hf.co/BlossomsAI/Qwen2.5-Coder-7B-Instruct-Uncensored-GGUF:Q6_K"
    DEFAULT_GENERAL_MODEL = "qwen35-uncensored:latest"

    SYSTEM_PROMPT = (
        "You are an elite Senior Developer and Master System Architect. Your world-renowned "
        "talent is explaining software code to complete beginners and bright 4-year-old children "
        "who have zero prior programming knowledge. You NEVER use unexplained jargon or hand-waving "
        "abstractions. You explain what is actually WRITTEN on the code file, word-for-word, "
        "tag-for-tag, line-by-line, using fun, vivid real-world analogies (like toys, Lego blocks, "
        "recipe books, drawing easels, and helpful robots). Your explanations are deep, ultra-clear, "
        "patient, and comprehensive. You never give short or vague summaries."
    )

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
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> CodebaseAnalysis:
        # Step 1: Compute high-precision baseline analysis using the static AST engine
        base_analysis = self.rule_engine.analyze_codebase(
            root_path, files, tech_stack, interconnections
        )
        base_analysis.engine_used = f"Local AI Model ({self.model_name} via {self.provider})"
        base_analysis.ai_model_name = self.model_name

        # Step 2: System-level AI Architectural Synthesis (Beginner / Lego Factory Analogy)
        ai_narrative = self._query_architecture(base_analysis, stream_callback=stream_callback)
        if ai_narrative:
            base_analysis.ai_architecture_critique = ai_narrative

        # Step 3: Per-File Deep Neural Analysis (Line-by-line / block-by-block beginner walkthrough)
        file_items = list(base_analysis.files.items())
        total_files = len(file_items)

        for idx, (rel_path, fa) in enumerate(file_items, 1):
            if progress_callback:
                progress_callback(idx, total_files, rel_path)

            file_ai_insight = self._query_file_analysis(
                fa,
                base_analysis,
                root_path,
                stream_callback=stream_callback
            )
            if file_ai_insight:
                fa.ai_insights = file_ai_insight
                fa.ai_model_used = self.model_name

        return base_analysis

    def _query_architecture(
        self,
        base_analysis: CodebaseAnalysis,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Queries the local AI model for codebase architectural synthesis explained to a beginner."""
        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"You are explaining the big architecture of this entire software project '{base_analysis.project_name}' "
            f"to a beginner student / 4-year-old child:\n\n"
            f"Project Facts:\n"
            f"- Total Files: {base_analysis.total_files}\n"
            f"- Total Lines of Code: {base_analysis.total_lines:,}\n"
            f"- Languages Used: {json.dumps(base_analysis.tech_stack.languages)}\n"
            f"- Frameworks: {', '.join(base_analysis.tech_stack.frameworks or ['None detected'])}\n"
            f"- Inter-File Connections: {len(base_analysis.interconnections)} cross-file links\n\n"
            f"Explain the system architecture using the Lego Castle / Toy Factory analogy. "
            f"Structure your response with these exact sections:\n\n"
            f"### 🏰 1. The Big Castle Story (What is this whole project?)\n"
            f"Explain what this project actually is and what it does in fun, plain English.\n\n"
            f"### 🏭 2. The Toy Workshops (How Folders & Files Divide the Work)\n"
            f"Explain how the different files and languages work together like different rooms in a toy workshop.\n\n"
            f"### 🚂 3. The Information Highway (How a User Click Travels)\n"
            f"Trace what happens when a user touches the screen or clicks a button, and how data travels through the code.\n\n"
            f"### 🛡️ 4. How to Make It Even Stronger (Architectural Recommendations)\n"
            f"Give 2-3 friendly recommendations on how to keep the project clean, fast, and organized.\n"
        )

        return self._send_prompt(prompt, max_tokens=400, temperature=0.3, stream_callback=stream_callback)

    def _query_file_analysis(
        self,
        fa: FileAnalysis,
        codebase: CodebaseAnalysis,
        root_path: str,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Queries the local AI model for a deep, line-by-line file explanation for beginners."""
        content_snippet = ""
        try:
            full_path = Path(fa.file_path)
            if not full_path.is_absolute():
                full_path = Path(root_path) / fa.relative_path
            if full_path.exists():
                raw = full_path.read_text(encoding="utf-8", errors="replace")
                lines = raw.splitlines()
                # Feed first 100 lines or 3500 chars to provide full file visibility
                if len(lines) > 100:
                    content_snippet = "\n".join(lines[:100]) + f"\n... [Truncated: {len(lines) - 100} more lines]"
                else:
                    content_snippet = raw[:3500]
        except Exception:
            content_snippet = "(File content unavailable)"

        outbound_desc = [f"{c.relation_type} -> {c.target_file}" for c in fa.outbound_connections] or ["None"]

        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"You are teaching an absolute beginner (or a 4-year-old child) who knows NOTHING about programming. "
            f"You must explain what is actually WRITTEN on this code file: `{fa.relative_path}` ({fa.language}) from the project '{codebase.project_name}'.\n\n"
            f"CODE IN THIS FILE:\n"
            f"```\n{content_snippet}\n```\n\n"
            f"Cross-File Links: {', '.join(outbound_desc)}\n\n"
            f"You MUST format your output in this EXACT standard format:\n\n"
            f"#### 🧸 1. The Big Picture Story (What is this code?)\n\n"
            f"│ \"[A vivid 4-year-old real-world toy/kitchen/stage story explaining what this code does in 2-3 sentences]\"\n"
            f"──────\n"
            f"#### 🔍 2. Line-by-Line & Word-by-Word Breakdown\n\n"
            f"For every major line or block from the code file, write:\n\n"
            f"#### Line X: <span style=\"color: #3b82f6;\"><font color=\"#3b82f6\">`[exact code line from the codefile]`</font></span>\n\n"
            f"• What is written?: [Plain English description of what tag, function, or statement this is]\n"
            f"• What does every word mean?:\n"
            f"    • [word/tag/attr]: [What this exact word means in simple terms]\n"
            f"• 🧸 4-Year-Old Analogy: [Super simple toy or everyday object analogy]\n"
            f"• 🖥️ What happens on screen?: [What the user sees or what happens inside the computer]\n"
            f"• 🔗 Interconnection with other files:\n"
            f"    • [How this line talks to other files, e.g. imported or referenced]\n"
            f"• 💥 What breaks if deleted?: [What error, crash, or missing feature happens if removed]\n"
            f"──────\n"
        )

        return self._send_prompt(prompt, max_tokens=850, temperature=0.3, stream_callback=stream_callback)

    def _send_prompt(
        self,
        prompt: str,
        max_tokens: int = 650,
        temperature: float = 0.3,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> Optional[str]:
        """Sends a prompt to the local AI endpoint with robust timeout and optional token streaming."""
        try:
            if self.provider == "ollama":
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": bool(stream_callback),
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature
                    }
                }
                if stream_callback:
                    res = requests.post(self.endpoint_url, json=payload, timeout=180, stream=True)
                    if res.status_code == 200:
                        full_tokens = []
                        for line in res.iter_lines():
                            if line:
                                chunk = json.loads(line.decode("utf-8"))
                                tok = chunk.get("response", "")
                                if tok:
                                    full_tokens.append(tok)
                                    stream_callback(tok)
                        return "".join(full_tokens).strip()
                    else:
                        return f"*AI Generation Notice*: Ollama returned HTTP {res.status_code}: {res.text[:100]}"
                else:
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
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": bool(stream_callback)
                }
                if stream_callback:
                    res = requests.post(url, json=payload, timeout=180, stream=True)
                    if res.status_code == 200:
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
                        return f"*AI Generation Notice*: Local AI server returned HTTP {res.status_code}: {res.text[:100]}"
                else:
                    res = requests.post(url, json=payload, timeout=180)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "").strip()
                    else:
                        return f"*AI Generation Notice*: Local AI server returned HTTP {res.status_code}: {res.text[:100]}"

        except requests.exceptions.Timeout:
            return "*AI Generation Notice*: Local model request timed out (>180s)."
        except requests.exceptions.ConnectionError:
            return "*AI Generation Notice*: Could not connect to local AI server at " + self.endpoint_url
        except Exception as e:
            return f"*AI Generation Notice*: Error querying local AI: {str(e)}"

        return None
