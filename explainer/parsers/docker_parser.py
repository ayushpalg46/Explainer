import re
from typing import List, Dict, Tuple
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import DOCKER_KNOWLEDGE


class DockerParser(BaseParser):
    """
    Parses Dockerfiles and Docker Compose files line-by-line with
    word-by-word symbol breakdowns, 4-year-old beginner analogies,
    what happens on screen/in container, what breaks if deleted,
    and cross-file injection references.
    """

    DIRECTIVE_DESCRIPTIONS = {
        "FROM": ("Base Image Declaration", "Starts a new build stage and selects the starting base operating system image."),
        "WORKDIR": ("Working Directory", "Sets the active directory inside the container for all following commands."),
        "COPY": ("Asset Injection", "Copies files or folders from your local computer into the container filesystem."),
        "ADD": ("Enhanced File Copy", "Copies local files or extracts tar archives into the container."),
        "RUN": ("Build-Time Command Execution", "Runs commands (like installing packages or compiling code) during build time."),
        "ENV": ("Environment Variable", "Sets persistent environment variables inside the container."),
        "ARG": ("Build Argument", "Defines a variable that users can pass at build-time to docker build."),
        "EXPOSE": ("Port Exposure Documentation", "Documents the network port number the container listens on."),
        "ENTRYPOINT": ("Fixed Container Entrypoint", "Configures the container to run as a fixed executable command."),
        "CMD": ("Default Execution Command", "Specifies the default command that runs when the container starts up."),
        "USER": ("Container User Context", "Sets the user name or UID to use when running subsequent commands."),
        "VOLUME": ("Persistent Storage Mount", "Creates a mount point with the specified path for persistent storage."),
        "HEALTHCHECK": ("Container Health Diagnostic", "Tells Docker how to test a container to check that it is still working."),
    }

    def __init__(self, is_compose: bool = False):
        super().__init__(language="Docker Compose" if is_compose else "Dockerfile")
        self.is_compose = is_compose

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        if self.is_compose:
            return self._parse_compose(analysis, content, lines)

        stages = []
        copied_files = []
        exposed_ports = []

        analysis.beginner_story = (
            "Think of a Dockerfile like a secret magical recipe card for building a brand new mini-computer! "
            "You write down instructions in order: first pick which mini-computer to start with, make a neat room "
            "called /app, pack your toys (your code files) into that room, install some tools, and finally press "
            "the big green START button so the mini-computer runs your software anywhere in the whole wide world!"
        )

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue

            m = re.match(r'^([A-Z]+)\s+(.*)$', clean)
            if not m:
                continue

            cmd = m.group(1).upper()
            arg = m.group(2).strip()

            words_breakdown: Dict[str, str] = {cmd: self.DIRECTIVE_DESCRIPTIONS.get(cmd, ("Dockerfile Instruction", f"Instruction `{cmd}`"))[1]}

            # Extract words / tokens from arguments
            arg_tokens = arg.split()
            for tok in arg_tokens[:6]:
                tok_clean = tok.strip("[],\"'")
                if tok_clean and tok_clean != cmd:
                    if tok_clean.startswith("--"):
                        words_breakdown[tok_clean] = f"Build flag or configuration option for `{cmd}`."
                    elif "/" in tok_clean or "." in tok_clean:
                        words_breakdown[tok_clean] = f"File or folder filesystem path: `{tok_clean}`."
                    elif tok_clean.isdigit():
                        words_breakdown[tok_clean] = f"Numeric network port or identifier: `{tok_clean}`."
                    else:
                        words_breakdown[tok_clean] = f"Parameter or command token `{tok_clean}`."

            kb = DOCKER_KNOWLEDGE.get(cmd, {
                "what_it_is": f"Dockerfile build instruction `{cmd}`.",
                "simple_analogy": f"Think of {cmd} like a dedicated step in an assembly line instruction manual.",
                "what_happens_on_screen": f"Executes instruction {cmd} and commits a new layer to the image.",
                "what_if_removed": f"The container image will be missing this configuration step.",
                "why_it_works": "Builds a dedicated cached layer in the container image.",
                "best_practices": "Ensure efficient layer caching by placing less frequently changed commands first."
            })

            interconnection_note = ""
            if cmd == "FROM":
                stages.append(arg)
                interconnection_note = f"Initializes the base operating environment needed by code files in this project."
            elif cmd in ("COPY", "ADD"):
                parts = arg.split()
                if parts:
                    src = parts[0]
                    copied_files.append(src)
                    analysis.raw_imports.append(src)
                    interconnection_note = f"Injects local codebase asset `{src}` into container destination `{parts[-1] if len(parts) > 1 else '.'}`."
            elif cmd == "EXPOSE":
                exposed_ports.append(arg)
                interconnection_note = f"Documents that external web traffic on port {arg} connects to server processes in this codebase."
            elif cmd in ("CMD", "ENTRYPOINT"):
                interconnection_note = f"Starts the application entrypoint command: `{arg}`."

            analysis.elements.append(ElementExplanation(
                name=f"{cmd} {arg[:30]}{'...' if len(arg) > 30 else ''}",
                kind="directive",
                line_number=idx,
                snippet=clean,
                what_it_is=f"Dockerfile instruction `{cmd}`: {kb.get('what_it_is', 'Container build directive')}",
                how_it_is_used=f"Executed at line {idx} with parameter: `{arg}`",
                where_it_is_used=f"Build instruction at line {idx}",
                why_it_works=kb.get("why_it_works", "Evaluated by BuildKit/Docker Engine to create a cacheable layer."),
                best_practices_and_pitfalls=kb.get("best_practices", "Keep layers clean and minimize layer count."),
                simple_analogy=kb.get("simple_analogy", f"Like step #{idx} in assembling your Lego castle."),
                what_happens_on_screen=kb.get("what_happens_on_screen", f"Docker terminal displays `RUNNING [{idx}] {cmd} {arg[:30]}`."),
                what_if_removed=kb.get("what_if_removed", "The container build loses this step and subsequent commands may fail."),
                words_breakdown=words_breakdown,
                interconnection_note=interconnection_note
            ))

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

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = ["Docker Engine Containerization"]
        analysis.role_in_codebase = "Containerization, Environment Isolation & Deployment Blueprint"
        analysis.summary = (
            f"Dockerfile defining container image build specifications with {len(lines)} lines. "
            f"{f'Uses a multi-stage build across {len(stages)} distinct stages. ' if is_multi_stage else 'Uses a single base stage. '}"
            f"Base image: `{stages[0] if stages else 'N/A'}`. "
            f"Exposes network port(s): {', '.join(exposed_ports) if exposed_ports else 'None explicit'}. "
            f"Injects {len(copied_files)} file/directory asset(s) from host context."
        )
        return analysis

    def _parse_compose(self, analysis: FileAnalysis, content: str, lines: List[str]) -> FileAnalysis:
        analysis.beginner_story = (
            "Think of Docker Compose like a friendly town mayor! Instead of just one house, "
            "the town mayor looks at a big map and tells all the houses (like the web shop, "
            "the database warehouse, and the redis mail carrier) how to talk to each other, "
            "which roads (ports) to connect, and keeps the whole town running together happily!"
        )

        services = []
        current_service = None
        current_service_line = 0

        for idx, line in enumerate(lines, 1):
            m_svc = re.match(r'^\s{2}([a-zA-Z0-9_\-]+):\s*$', line)
            if m_svc:
                svc_name = m_svc.group(1)
                services.append(svc_name)
                current_service = svc_name
                current_service_line = idx

                words_breakdown = {
                    svc_name: f"The unique name of this microservice container.",
                    ":": "YAML colon indicating the start of this service's configuration properties."
                }

                analysis.elements.append(ElementExplanation(
                    name=f"Service: {svc_name}",
                    kind="service",
                    line_number=idx,
                    snippet=line.strip(),
                    what_it_is=f"Docker Compose microservice container definition `{svc_name}`.",
                    how_it_is_used=f"Orchestrates a dedicated container named `{svc_name}` on the private bridge network.",
                    where_it_is_used=f"Services block at line {idx}.",
                    why_it_works="Docker Compose creates a private DNS network where services resolve each other by container name.",
                    best_practices_and_pitfalls="Explicitly declare health checks and volume mounts to avoid data loss.",
                    simple_analogy=f"Think of service '{svc_name}' like a dedicated workshop in Santa's toy factory with its own job!",
                    what_happens_on_screen=f"When running `docker compose up`, you see `[+] Running {svc_name} Started`.",
                    what_if_removed=f"The `{svc_name}` container won't boot, and any service that talks to `{svc_name}` will report connection errors.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Creates a DNS hostname `{svc_name}` accessible by other containers in this compose stack."
                ))
            elif current_service and re.match(r'^\s{4}(ports|image|build|volumes|environment|depends_on):', line):
                prop_match = re.match(r'^\s{4}([a-zA-Z0-9_\-]+):\s*(.*)$', line)
                if prop_match:
                    prop_name = prop_match.group(1)
                    prop_val = prop_match.group(2).strip()
                    analysis.elements.append(ElementExplanation(
                        name=f"{current_service}.{prop_name}",
                        kind="configuration",
                        line_number=idx,
                        snippet=line.strip(),
                        what_it_is=f"Configuration parameter `{prop_name}` for service `{current_service}`.",
                        how_it_is_used=f"Configures `{prop_name}` with value: `{prop_val or 'nested definition'}`.",
                        where_it_is_used=f"Under service `{current_service}` at line {idx}.",
                        why_it_works="Supplies container runtime parameters to Docker daemon during startup.",
                        best_practices_and_pitfalls="Use `.env` files rather than hardcoding passwords in environment keys.",
                        simple_analogy=f"Like setting a rule on how service '{current_service}' is dressed and where its door leads.",
                        what_happens_on_screen=f"Applies runtime property `{prop_name}` when booting `{current_service}`.",
                        what_if_removed=f"Service `{current_service}` uses default settings or loses its port forwarding/volume.",
                        words_breakdown={prop_name: f"Compose property key for `{prop_name}`.", prop_val or ":": "Value or nested block mapping."} if prop_val else {prop_name: "Property key."},
                        interconnection_note=f"Connects `{current_service}` to external ports or shared volumes."
                    ))

        analysis.frameworks_detected = ["Docker Compose Multi-Container Orchestration"]
        analysis.concepts_detected = [f"Multi-Service Architecture ({len(services)} services: {', '.join(services[:4])})"]
        analysis.role_in_codebase = "Local Multi-Container Development & Orchestration Topology"
        analysis.summary = (
            f"Docker Compose configuration coordinating {len(services)} microservice container(s): "
            f"{', '.join(services) if services else 'services defined'}. Sets up networking, volumes, and environment links."
        )
        return analysis
