"""
Generic Config, Data, and Documentation Parser for Explainer.
Handles JSON, YAML, TOML, Markdown, SQL, and other project configuration files.
"""
import re
from typing import List, Dict, Any
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class GenericFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".json", ".yaml", ".yml", ".toml", ".sql", ".md", ".txt", ".env"]

    @property
    def language_name(self) -> str:
        return "Configuration / Data / Documentation"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]
        ext = "." + filename.split(".")[-1] if "." in filename else ""

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = []
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        if ext == ".json":
            tech_stack.append("JSON Data Format")
            if filename == "package.json":
                tech_stack.append("Node.js / npm Project Manifest")
                concepts.append("Node.js Package Manifest & Script Orchestration")
                arch_role = "Project Manifest & Dependency Configuration"
                # Extract script entries and dependencies
                scripts = re.findall(r'"([a-zA-Z0-9_:-]+)"\s*:\s*"([^"]+)"', content)
                for s_name, s_cmd in scripts[:10]:
                    symbols.append(FileSymbol(
                        name=f"npm run {s_name}",
                        kind="npm_script",
                        line=1,
                        signature=s_cmd,
                        description=f"Automated npm script: `{s_cmd}`."
                    ))
            elif filename == "tsconfig.json":
                tech_stack.append("TypeScript Compiler Config")
                concepts.append("TypeScript Compiler Strictness & Path Aliases")
                arch_role = "TypeScript Compiler Configuration"
            else:
                arch_role = "Structured Data / JSON Configuration"

        elif ext in (".yaml", ".yml"):
            tech_stack.append("YAML Structured Config")
            if "apiVersion" in content and "kind" in content:
                tech_stack.append("Kubernetes Manifest")
                concepts.append("Kubernetes Cloud Native Declarative Spec")
                arch_role = "Kubernetes Infrastructure Manifest"
            elif "github/workflows" in filepath or "jobs:" in content:
                tech_stack.append("GitHub Actions CI/CD")
                concepts.append("Automated CI/CD Workflow Pipeline")
                arch_role = "CI/CD Automation Workflow"
            elif "services:" in content and "version:" in content:
                tech_stack.append("Docker Compose Multi-Container")
                concepts.append("Multi-Container Service Orchestration")
                arch_role = "Container Orchestration Specification"
            else:
                arch_role = "YAML Configuration"

        elif ext == ".sql":
            tech_stack.append("SQL Relational Database")
            concepts.append("Relational Schema & Query DDL/DML")
            tables = re.findall(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)", content, re.IGNORECASE)
            for t in tables:
                symbols.append(FileSymbol(
                    name=t,
                    kind="sql_table",
                    line=1,
                    signature=f"TABLE {t}",
                    description=f"Relational database entity table schema for `{t}`."
                ))
            arch_role = "Database Schema / Migration Script"

        elif ext == ".md":
            tech_stack.append("Markdown Documentation")
            concepts.append("Developer Documentation & Knowledge Repository")
            arch_role = "Documentation / Technical Specification"

        elif ext == ".env":
            tech_stack.append("Environment Variables Configuration")
            concepts.append("Application Configuration & Secret Parameters")
            arch_role = "Runtime Environment Secret Definition"
            security_and_practices.append("Ensure `.env` files are included in `.gitignore` to prevent leaking secrets.")

        else:
            tech_stack.append("Plain Text Configuration")
            arch_role = "Configuration File"

        components_breakdown.append({
            "section": "Configuration Scope",
            "details": f"Defines {loc} lines of configuration or structured declarations."
        })

        summary = f"{arch_role} ({filename}) declaring configuration or structured data."

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=ext,
            language=tech_stack[0] if tech_stack else "Config",
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
            tags=["config", "meta", ext.replace(".", "")]
        )
