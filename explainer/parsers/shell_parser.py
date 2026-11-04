import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import SHELL_KNOWLEDGE


class ShellParser(BaseParser):
    def __init__(self):
        super().__init__(language="Shell Script")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        shebang = lines[0] if lines and lines[0].startswith("#!") else None
        
        # Check strict mode flags
        has_strict_mode = bool(re.search(r'set\s+-[a-zA-Z]*e|set\s+-o\s+pipefail', content))
        
        # Functions defined in shell
        functions = re.findall(r'(?:function\s+)?([a-zA-Z0-9_\-]+)\s*\(\s*\)\s*\{', content)
        
        # Sourced or executed scripts: source ./... or . ./... or ./...
        sourced_files = re.findall(r'(?:source|\.)\s+([^\s;]+)', content)
        for s in sourced_files:
            if not s.startswith("-"):
                analysis.raw_imports.append(s)

        # Commands invoked
        common_cmds = ["docker", "docker-compose", "npm", "yarn", "pnpm", "python", "pytest", "curl", "git", "cargo", "go", "mvn", "gradle"]
        invoked_tools = []
        for tool in common_cmds:
            if re.search(rf'\b{tool}\b', content):
                invoked_tools.append(tool)

        has_pipes = "|" in content
        has_loops = bool(re.search(r'\bfor\s+|\bwhile\s+', content))

        detected_concepts = []
        if shebang:
            detected_concepts.append(f"Interpreter Shebang (`{shebang.strip()}`)")
            kb = SHELL_KNOWLEDGE.get("shebang", {})
            analysis.elements.append(ElementExplanation(
                name="Shebang Interpreter",
                kind="directive",
                line_number=1,
                snippet=shebang.strip(),
                what_it_is=kb["what_it_is"],
                how_it_is_used="Instructs the OS kernel which binary executes this script file.",
                where_it_is_used="First line of the script.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        if has_strict_mode:
            detected_concepts.append("Strict Shell Safety Mode (`set -e / pipefail`)")
            kb = SHELL_KNOWLEDGE.get("strict_mode", {})
            analysis.elements.append(ElementExplanation(
                name="Strict Mode Flag",
                kind="concept",
                line_number=None,
                snippet="set -euo pipefail",
                what_it_is=kb["what_it_is"],
                how_it_is_used="Configures bash runtime to fail fast on any error.",
                where_it_is_used="Initialization section of the script.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        if has_pipes:
            detected_concepts.append("Inter-process Pipe Streams (`|`)")
        if functions:
            detected_concepts.append(f"Modular Shell Functions ({', '.join(functions[:3])})")
        if invoked_tools:
            detected_concepts.append(f"Orchestrated External Tooling ({', '.join(invoked_tools)})")

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = [f"CLI / Tooling Automation ({', '.join(invoked_tools)})"] if invoked_tools else ["Unix Shell Environment"]
        analysis.role_in_codebase = "Build, Automation, CI/CD or Deployment Task Runner"
        analysis.summary = (
            f"Shell automation script containing {len(lines)} lines. "
            f"{f'Targets interpreter: `{shebang}`. ' if shebang else ''}"
            f"{'Enforces strict error trapping. ' if has_strict_mode else ''}"
            f"{f'Defines {len(functions)} modular shell routine(s): {', '.join(functions)}. ' if functions else ''}"
            f"{f'Orchestrates command-line tools: {', '.join(invoked_tools)}. ' if invoked_tools else ''}"
            f"Sources {len(sourced_files)} child configuration/script file(s)."
        )
        return analysis

