import re
from typing import List, Dict, Tuple
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import DOCKER_KNOWLEDGE


class DockerParser(BaseParser):
    def __init__(self, is_compose: bool = False):
        super().__init__(language="Docker Compose" if is_compose else "Dockerfile")
        self.is_compose = is_compose

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        if self.is_compose:
            return self._parse_compose(analysis, content)

        # Parse Dockerfile instructions
        instructions: List[Tuple[str, str, int]] = []
        stages = []
        copied_files = []
        exposed_ports = []

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue
            m = re.match(r'^([A-Z]+)\s+(.*)$', clean)
            if m:
                cmd = m.group(1).upper()
                arg = m.group(2).strip()
                instructions.append((cmd, arg, idx))

                if cmd == "FROM":
                    stages.append(arg)
                elif cmd in ("COPY", "ADD"):
                    # Source file usually the first argument
                    parts = arg.split()
                    if parts:
                        src = parts[0]
                        copied_files.append(src)
                        analysis.raw_imports.append(src)
                elif cmd == "EXPOSE":
                    exposed_ports.append(arg)

        is_multi_stage = len(stages) > 1
        detected_concepts = []
        if is_multi_stage:
            detected_concepts.append(f"Multi-Stage Build Pipeline ({len(stages)} stages)")
        else:
            detected_concepts.append("Single Stage Container Build")
        if exposed_ports:
            detected_concepts.append(f"Exposed Network Ports ({', '.join(exposed_ports)})")
        if copied_files:
            detected_concepts.append(f"Filesystem Context Injection ({len(copied_files)} COPY operations)")

        # Unique instructions to explain
        seen_cmds = set()
        for cmd, arg, line_no in instructions:
            if cmd in seen_cmds:
                continue
            seen_cmds.add(cmd)
            kb = DOCKER_KNOWLEDGE.get(cmd, {
                "what_it_is": f"Dockerfile build instruction `{cmd}`.",
                "why_it_works": "Builds a dedicated layer in the container image.",
                "best_practices": "Ensure efficient layer caching."
            })
            analysis.elements.append(ElementExplanation(
                name=f"Directive: {cmd}",
                kind="directive",
                line_number=line_no,
                snippet=f"{cmd} {arg[:50]}...",
                what_it_is=kb["what_it_is"],
                how_it_is_used=f"Executed at line {line_no} with arguments: `{arg[:60]}`.",
                where_it_is_used=f"Instruction in build stage at line {line_no}.",
                why_it_works=kb["why_it_works"],
                best_practices_and_pitfalls=kb["best_practices"]
            ))

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = ["Docker Engine Containerization"]
        analysis.role_in_codebase = "Containerization, Environment Isolation & Deployment Blueprint"
        analysis.summary = (
            f"Dockerfile defining container image build specifications. "
            f"{f'Uses a multi-stage build across {len(stages)} distinct stages to minimize image size. ' if is_multi_stage else 'Uses a single base stage. '}"
            f"Base image: `{stages[0] if stages else 'N/A'}`. "
            f"Exposes network port(s): {', '.join(exposed_ports) if exposed_ports else 'None explicit'}. "
            f"Injects {len(copied_files)} file/directory asset(s) from host context."
        )
        return analysis

    def _parse_compose(self, analysis: FileAnalysis, content: str) -> FileAnalysis:
        services = re.findall(r'^\s\s([a-zA-Z0-9_\-]+):\s*$', content, re.MULTILINE)
        analysis.frameworks_detected = ["Docker Compose Multi-Container Orchestration"]
        analysis.concepts_detected = [f"Multi-Service Architecture ({len(services)} services: {', '.join(services[:4])})"]
        analysis.role_in_codebase = "Local Multi-Container Development & Orchestration Topology"
        analysis.summary = (
            f"Docker Compose configuration coordinating {len(services)} microservice container(s): "
            f"{', '.join(services) if services else 'services defined'}. Sets up networking, volumes, and environment links."
        )
        return analysis
