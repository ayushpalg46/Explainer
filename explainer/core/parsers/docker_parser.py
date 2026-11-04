"""
Dockerfile & Container Specification Parser for Explainer.
Analyzes multi-stage build pipelines, base images, dependencies, exposed ports, security risks, and file copies.
"""
import re
from typing import List, Dict, Any
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class DockerFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".dockerfile", "dockerfile", ".docker"]

    @property
    def language_name(self) -> str:
        return "Dockerfile"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["Docker Containerization"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        stages: List[Dict[str, str]] = []
        exposed_ports: List[str] = []
        env_vars: List[str] = []
        commands: List[Dict[str, Any]] = []
        has_non_root_user: bool = False

        for i, line in enumerate(lines, 1):
            line_strip = line.strip()
            if not line_strip or line_strip.startswith("#"):
                continue

            parts = line_strip.split(maxsplit=1)
            inst = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ""

            commands.append({"instruction": inst, "args": args, "line": i})

            if inst == "FROM":
                stage_match = re.match(r"(\S+)(?:\s+[aA][sS]\s+(\S+))?", args)
                if stage_match:
                    image = stage_match.group(1)
                    alias = stage_match.group(2) or ""
                    stages.append({"image": image, "alias": alias, "line": i})
                    imports.append(FileImport(
                        source=alias or "base_image",
                        target=image,
                        line=i,
                        import_type="docker_base_image"
                    ))
                    symbols.append(FileSymbol(
                        name=f"FROM {image}",
                        kind="docker_stage",
                        line=i,
                        signature=f"FROM {image}{f' AS {alias}' if alias else ''}",
                        description=f"Initializes build stage using base image '{image}'."
                    ))
                    # Stack detection
                    if "node" in image:
                        tech_stack.append("Node.js Container Runtime")
                    elif "python" in image:
                        tech_stack.append("Python Container Runtime")
                    elif "golang" in image:
                        tech_stack.append("Go Container Runtime")
                    elif "rust" in image:
                        tech_stack.append("Rust Container Runtime")
                    elif "alpine" in image:
                        tech_stack.append("Alpine Linux Base")
                    elif "nginx" in image:
                        tech_stack.append("Nginx Web Server")

            elif inst in ("COPY", "ADD"):
                # Track file copies to detect interconnections
                copy_parts = args.split()
                # e.g. COPY --from=builder /app/dist ./dist OR COPY package.json ./
                clean_sources = [p for p in copy_parts[:-1] if not p.startswith("--")]
                dest = copy_parts[-1] if copy_parts else "."
                for src in clean_sources:
                    connections.append(FileConnection(
                        source_file=filepath,
                        target_file=src,
                        relation_type="copies_to_container",
                        mechanism=f"{inst} {src} -> {dest}",
                        rationale="Copies host source code, build artifacts, or configuration files into container filesystem."
                    ))

            elif inst == "EXPOSE":
                ports = args.split()
                exposed_ports.extend(ports)
                for p in ports:
                    exports.append(FileExport(name=f"Port {p}", kind="exposed_port", line=i))

            elif inst in ("ENV", "ARG"):
                env_match = re.match(r"([a-zA-Z0-9_]+)", args)
                if env_match:
                    env_vars.append(env_match.group(1))

            elif inst == "USER":
                if args != "root" and args != "0":
                    has_non_root_user = True

            elif inst in ("ENTRYPOINT", "CMD"):
                symbols.append(FileSymbol(
                    name=inst,
                    kind="container_entrypoint",
                    line=i,
                    signature=f"{inst} {args}",
                    description=f"Defines container execution start command: `{args}`."
                ))
                # Check if script is executed
                script_match = re.search(r"['\"]?([a-zA-Z0-9_./-]+\.sh)['\"]?", args)
                if script_match:
                    connections.append(FileConnection(
                        source_file=filepath,
                        target_file=script_match.group(1),
                        relation_type="triggers_script",
                        mechanism=f"{inst} executes {script_match.group(1)}",
                        rationale="Delegates container initialization or bootstrap sequence to shell entrypoint script."
                    ))

        # Architecture and concepts
        if len(stages) > 1:
            concepts.append(f"Multi-Stage Build Pipeline ({len(stages)} stages: {', '.join(s['alias'] or s['image'] for s in stages)})")
        else:
            concepts.append("Single Stage Container Build")

        if exposed_ports:
            concepts.append(f"Network Port Ingress: {', '.join(exposed_ports)}")
        if env_vars:
            concepts.append(f"Environment Configuration ({len(env_vars)} variable(s) declared)")

        # Security evaluation
        if not has_non_root_user:
            security_and_practices.append("Security Risk: Container runs as default root user. Add a non-root `USER appuser` directive.")
        if any(":latest" in s["image"] or (":" not in s["image"]) for s in stages):
            security_and_practices.append("Best Practice: Base images use `:latest` or unpinned tags. Pin SHA digest or explicit version for reproducibility.")
        if any(c["instruction"] == "ADD" and not c["args"].endswith((".tar.gz", ".tar", ".tgz")) for c in commands):
            security_and_practices.append("Use `COPY` instead of `ADD` unless automatic tar extraction is required.")

        # Breakdown
        stage_summaries = []
        for idx, s in enumerate(stages):
            alias_str = f" AS {s['alias']}" if s.get("alias") else ""
            stage_summaries.append(f"Stage {idx+1}: FROM {s['image']}{alias_str}")

        components_breakdown.append({
            "section": "Build Stages & Base Images",
            "details": "; ".join(stage_summaries)
        })
        components_breakdown.append({
            "section": "Container Runtime Environment",
            "details": f"Exposed Ports: {', '.join(exposed_ports) if exposed_ports else 'None'}. Environment variables: {', '.join(env_vars) if env_vars else 'None'}."
        })
        components_breakdown.append({
            "section": "Instruction Summary",
            "details": f"Executes {len(commands)} directives across container build phases."
        })

        summary = f"Dockerfile defining {len(stages)}-stage container build image with {len(commands)} instructions and {len(exposed_ports)} exposed ports."
        arch_role = "Deployment & Infrastructure / Container Image Specification"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".dockerfile",
            language="Dockerfile",
            lines_of_code=loc,
            size_bytes=size_bytes,
            summary=summary,
            architecture_role=arch_role,
            tech_stack=list(set(tech_stack)),
            symbols=symbols,
            imports=imports,
            exports=exports,
            concepts=concepts,
            components_breakdown=components_breakdown,
            outgoing_connections=connections,
            security_and_best_practices=security_and_practices,
            tags=["docker", "devops", "container", "infrastructure"]
        )
