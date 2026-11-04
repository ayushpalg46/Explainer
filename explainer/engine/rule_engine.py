from pathlib import Path
from typing import Dict, List, Tuple
from ..models import CodebaseAnalysis, FileAnalysis, TechStackInfo, FileInterconnection


class RuleExplainerEngine:
    """
    Deterministic, high-accuracy AST & Semantic Knowledge Engine.
    Provides exhaustive, pedagogical explanations of codebase architecture,
    technology compatibility, file purposes, and cross-file interconnections
    without needing any external AI model.
    """

    def analyze_codebase(
        self,
        root_path: str,
        files: Dict[str, FileAnalysis],
        tech_stack: TechStackInfo,
        interconnections: List[FileInterconnection]
    ) -> CodebaseAnalysis:
        root_p = Path(root_path).resolve()
        project_name = root_p.name or "Codebase"

        total_lines = sum(f.line_count for f in files.values())
        folder_roles = self._compute_folder_roles(files)
        arch_style, arch_summary = self._synthesize_architecture(files, tech_stack, interconnections)

        return CodebaseAnalysis(
            root_path=str(root_p),
            project_name=project_name,
            total_files=len(files),
            total_lines=total_lines,
            tech_stack=tech_stack,
            architecture_style=arch_style,
            architecture_summary=arch_summary,
            folder_roles=folder_roles,
            files=files,
            interconnections=interconnections,
            engine_used="Rule/AST Deep Knowledge Engine (Deterministic Zero-AI Mode)"
        )

    def _compute_folder_roles(self, files: Dict[str, FileAnalysis]) -> Dict[str, str]:
        folders: Dict[str, List[FileAnalysis]] = {}
        for rel_path, file_analysis in files.items():
            parent = str(Path(rel_path).parent.as_posix())
            if parent == ".":
                parent = "root"
            folders.setdefault(parent, []).append(file_analysis)

        roles: Dict[str, str] = {}
        for folder, file_list in folders.items():
            f_lower = folder.lower()
            if f_lower in ("src", "app"):
                roles[folder] = "Primary Application Source Code & Logic Modules"
            elif "component" in f_lower:
                roles[folder] = "Reusable UI Views & Visual Component Library"
            elif "style" in f_lower or "css" in f_lower:
                roles[folder] = "Global Styling, Theming Tokens, and CSS Architecture"
            elif "util" in f_lower or "lib" in f_lower or "helper" in f_lower:
                roles[folder] = "Shared Helper Utilities, Pure Functions, and Common Libraries"
            elif "route" in f_lower or "api" in f_lower or "controller" in f_lower:
                roles[folder] = "Network Endpoints, Request Routers & API Controllers"
            elif "model" in f_lower or "schema" in f_lower:
                roles[folder] = "Domain Entities, Database ORM Models & Type Contracts"
            elif "test" in f_lower or "spec" in f_lower:
                roles[folder] = "Automated Test Specs, Unit Suites & Integration Fixtures"
            elif "doc" in f_lower:
                roles[folder] = "Technical Documentation, Guides & API References"
            elif folder == "root":
                roles[folder] = "Repository Scaffolding, Package Manifests & Environment Configs"
            else:
                roles[folder] = f"Modular Subsystem with {len(file_list)} source file(s)"

        return roles

    def _synthesize_architecture(
        self,
        files: Dict[str, FileAnalysis],
        tech_stack: TechStackInfo,
        interconnections: List[FileInterconnection]
    ) -> Tuple[str, str]:
        frameworks = tech_stack.frameworks
        has_react = any("React" in f for f in frameworks)
        has_python_backend = any(f in frameworks for f in ["FastAPI", "Flask", "Django"])
        has_docker = any("Docker" in b for b in tech_stack.build_tools)
        has_rust = "Rust" in tech_stack.languages
        has_go = "Go" in tech_stack.languages

        if has_react and has_python_backend:
            style = "Decoupled Full-Stack Web Application (SPA Client + Python API)"
            summary = (
                f"The repository is structured as a decoupled full-stack architecture. "
                f"The client layer is managed via modern React components with declarative state handling. "
                f"The backend is powered by Python web services handling routing and business domain logic. "
                f"{'Containerized with Docker for seamless environment parity across development and deployment.' if has_docker else ''}"
            )
        elif has_react:
            style = "Single Page Application (SPA) / Frontend Component Architecture"
            summary = (
                f"The project implements a modern client-side Single Page Application architecture. "
                f"Components are organized hierarchically, allowing rapid declarative DOM updates via the Virtual DOM "
                f"and encapsulated CSS styling."
            )
        elif has_python_backend:
            style = "Modular Python Backend Service & API Architecture"
            summary = (
                f"The application is architected around structured Python modules and services, "
                f"organizing business models, route controllers, and utility pipelines into cleanly separated packages."
            )
        elif has_rust:
            style = "High-Performance Systems Architecture (Rust)"
            summary = (
                f"Engineered with Rust's memory-safe, zero-cost abstraction paradigm. "
                f"Utilizes strict ownership semantics, algebraic types, and compile-time correctness guarantees."
            )
        elif has_go:
            style = "Concurrent Cloud Microservice Architecture (Go)"
            summary = (
                f"Structured around Go's lightweight CSP concurrency model, utilizing goroutines, "
                f"strongly-typed structs, and standard HTTP handlers for scalable throughput."
            )
        else:
            style = "Modular Multi-File Codebase"
            summary = (
                f"A structured project spanning {len(files)} files and {len(tech_stack.languages)} programming languages, "
                f"organized into {len(interconnections)} cross-file dependencies."
            )

        return style, summary
