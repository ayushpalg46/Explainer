"""
Shell Script (Bash, Sh, Zsh) Parser for Explainer.
Analyzes shebangs, safety flags (set -e), environment variables, functions, invoked commands, pipelines, and script chaining.
"""
import re
from typing import List, Dict, Any
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class ShellFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".sh", ".bash", ".zsh"]

    @property
    def language_name(self) -> str:
        return "Shell Script"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["Shell Script"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        # 1. Shebang
        shebang = lines[0] if lines and lines[0].startswith("#!") else ""
        if shebang:
            concepts.append(f"Shebang Interpreter: `{shebang}`")
            if "bash" in shebang:
                tech_stack.append("Bash")
            elif "zsh" in shebang:
                tech_stack.append("Zsh")
            elif "sh" in shebang:
                tech_stack.append("POSIX Sh")
        else:
            security_and_practices.append("Missing shebang line (e.g. `#!/usr/bin/env bash`). Script depends on calling environment shell.")

        # 2. Strict Safety Flags (set -euo pipefail)
        has_set_e = bool(re.search(r"set\s+-[a-zA-Z]*e", content))
        has_set_u = bool(re.search(r"set\s+-[a-zA-Z]*u", content))
        has_set_pipefail = "pipefail" in content
        if has_set_e and has_set_pipefail:
            concepts.append("Strict Error Trapping (`set -euo pipefail`) Enabled")
        elif not has_set_e:
            security_and_practices.append("Consider adding `set -euo pipefail` to automatically abort on errors or unset variables.")

        # 3. Source / Sourced files (. or source)
        source_matches = re.finditer(r"(?:source|\.)\s+([a-zA-Z0-9_./-]+\.(?:sh|env))", content)
        for m in source_matches:
            target = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            imports.append(FileImport(source="source", target=target, line=line_num, import_type="shell_source"))
            connections.append(FileConnection(
                source_file=filepath,
                target_file=target,
                relation_type="sources_environment",
                mechanism=f"source {target}",
                rationale="Loads environment variables, helper routines, or credentials from external script/config."
            ))

        # 4. Functions
        func_matches = re.finditer(r"(?:function\s+)?([a-zA-Z0-9_-]+)\s*\(\)\s*\{", content)
        func_names = []
        for m in func_matches:
            f_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            func_names.append(f_name)
            symbols.append(FileSymbol(
                name=f_name,
                kind="shell_function",
                line=line_num,
                signature=f"{f_name}()",
                description=f"Modular shell routine executing {f_name}."
            ))
            exports.append(FileExport(name=f_name, kind="function", line=line_num))

        if func_names:
            concepts.append(f"Structured Shell Functions ({len(func_names)} declared: {', '.join(func_names)})")

        # 5. Environment Variables Exported
        export_matches = re.finditer(r"export\s+([a-zA-Z0-9_]+)=(?:['\"`]?([^'\"`\n]+)['\"`]?)?", content)
        exported_vars = []
        for m in export_matches:
            var_name = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            exported_vars.append(var_name)
            exports.append(FileExport(name=f"ENV: {var_name}", kind="env_var", line=line_num))

        if exported_vars:
            concepts.append(f"Exported Process Environment Variables ({len(exported_vars)}: {', '.join(exported_vars[:6])})")

        # 6. Commands and Tool Ecosystem Detected
        tools_found = set()
        common_tools = [
            ("docker", "Docker CLI Engine"),
            ("kubectl", "Kubernetes CLI Engine"),
            ("git", "Git Version Control"),
            ("npm", "Node Package Manager"),
            ("cargo", "Rust Cargo Build System"),
            ("python", "Python Interpreter"),
            ("curl", "cURL HTTP Transfer Tool"),
            ("terraform", "Terraform Infrastructure as Code"),
            ("systemctl", "Systemd Service Manager"),
            ("aws", "AWS CLI SDK"),
            ("gcloud", "Google Cloud SDK")
        ]
        for cmd, label in common_tools:
            if re.search(rf"\b{cmd}\b", content):
                tools_found.add(label)
                tech_stack.append(label)

        # Chained script invocations (e.g. `./run.sh`, `bash setup.sh`)
        chained_scripts = re.findall(r"(?:\./|bash\s+|sh\s+)([a-zA-Z0-9_/-]+\.sh)", content)
        for cs in chained_scripts:
            if cs != filename:
                connections.append(FileConnection(
                    source_file=filepath,
                    target_file=cs,
                    relation_type="triggers_script",
                    mechanism=f"Invokes {cs}",
                    rationale="Chains execution workflow by invoking secondary shell automation script."
                ))

        # Components breakdown
        components_breakdown.append({
            "section": "Interpreter & Execution Context",
            "details": f"Interpreter: {shebang or 'Unspecified sh'}. Strict mode: {'Enabled' if has_set_e else 'Disabled'}."
        })
        components_breakdown.append({
            "section": "Automation Routines & Functions",
            "details": f"Defines {len(func_names)} function(s): {', '.join(func_names) if func_names else 'Linear script flow'}."
        })
        components_breakdown.append({
            "section": "Invoked Command-Line Ecosystem",
            "details": f"Leverages CLI tools: {', '.join(tools_found) if tools_found else 'Standard POSIX utilities'}."
        })

        summary = f"Shell automation script ({filename}) containing {loc} lines, invoking {len(tools_found)} CLI tools and {len(func_names)} custom functions."
        arch_role = "CI/CD & DevOps Automation / Build Script"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".sh",
            language="Shell Script",
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
            tags=["shell", "bash", "devops", "automation", "script"]
        )
