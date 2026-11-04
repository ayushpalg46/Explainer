"""
Tech Stack, Architecture, and Compatibility Matrix Detector for Explainer.
Scans codebases, classifies high-level architectures, and validates cross-stack compatibility.
"""
import os
from typing import Dict, List, Set, Any
from explainer.core.parsers.base import FileAnalysis


class ProjectDetector:
    IGNORE_DIRS = {
        ".git", "node_modules", "venv", ".venv", "env", "target", "dist", "build",
        "__pycache__", ".pytest_cache", ".idea", ".vscode", ".next", ".turbo"
    }

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def scan_files(self) -> List[str]:
        """Collects all scan-worthy project source files."""
        matched_files = []
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            # Prune ignored directories
            dirnames[:] = [d for d in dirnames if d not in self.IGNORE_DIRS and not d.startswith(".")]

            for f in filenames:
                if f.startswith(".") and not f.startswith(".env"):
                    continue
                full_path = os.path.join(dirpath, f)
                rel_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                matched_files.append(rel_path)
        return sorted(matched_files)

    def detect_architecture(self, analyses: List[FileAnalysis]) -> Dict[str, Any]:
        """Classifies the project architecture style and layer distribution."""
        languages = {}
        total_loc = 0
        all_tech = set()

        for a in analyses:
            languages[a.language] = languages.get(a.language, 0) + a.lines_of_code
            total_loc += a.lines_of_code
            all_tech.update(a.tech_stack)

        has_frontend = any(lang in languages for lang in ("HTML", "CSS", "JavaScript", "TypeScript"))
        has_backend = any(lang in languages for lang in ("Python", "Rust", "Java", "Go"))
        has_docker = any("Docker" in t for t in all_tech)

        if has_frontend and has_backend:
            arch_type = "Full-Stack Application Architecture"
            arch_desc = "Combines interactive client-side presentation layers with server-side API/business logic engines."
        elif has_frontend and not has_backend:
            arch_type = "Client-Side Frontend Application / SPA"
            arch_desc = "Executes within client browser runtimes, delegating data persistence to external headless APIs."
        elif has_backend and not has_frontend:
            arch_type = "Backend Microservice / Systems Application"
            arch_desc = "Server-side headless computing service providing APIs, data models, or background processing."
        elif has_docker and not has_frontend and not has_backend:
            arch_type = "Infrastructure & Containerization Pipeline"
            arch_desc = "Configures automated deployment environments and container topologies."
        else:
            arch_type = "Modular Codebase"
            arch_desc = "Multi-language utility and script automation project."

        return {
            "architecture_type": arch_type,
            "architecture_description": arch_desc,
            "total_files": len(analyses),
            "total_loc": total_loc,
            "languages": languages,
            "detected_technologies": sorted(list(all_tech))
        }

    def evaluate_compatibility(self, analyses: List[FileAnalysis]) -> List[Dict[str, str]]:
        """
        Validates technology versions, toolchain alignments, and configuration hygiene.
        """
        checks: List[Dict[str, str]] = []
        file_names = {a.filename.lower() for a in analyses}
        all_tech = {t for a in analyses for t in a.tech_stack}

        # Check Node.js / Frontend configs
        has_js = any(a.language in ("JavaScript", "TypeScript") for a in analyses)
        if has_js:
            if "package.json" in file_names:
                checks.append({
                    "status": "PASS",
                    "category": "Frontend Runtime",
                    "title": "Node.js Package Manifest",
                    "details": "Found `package.json` specifying project scripts and package dependencies."
                })
            else:
                checks.append({
                    "status": "WARN",
                    "category": "Frontend Runtime",
                    "title": "Missing package.json",
                    "details": "JavaScript/TypeScript code present without a root `package.json` manifest."
                })

        # Check Python configs
        has_py = any(a.language == "Python" for a in analyses)
        if has_py:
            has_py_manifest = any(fn in file_names for fn in ("requirements.txt", "pyproject.toml", "setup.py", "pipfile"))
            if has_py_manifest:
                checks.append({
                    "status": "PASS",
                    "category": "Python Ecosystem",
                    "title": "Python Dependency Management",
                    "details": "Standard dependency declaration file identified."
                })
            else:
                checks.append({
                    "status": "WARN",
                    "category": "Python Ecosystem",
                    "title": "Missing Python Manifest",
                    "details": "Python source files detected without `pyproject.toml` or `requirements.txt`."
                })

        # Check Rust configs
        has_rs = any(a.language == "Rust" for a in analyses)
        if has_rs:
            if "cargo.toml" in file_names:
                checks.append({
                    "status": "PASS",
                    "category": "Rust Toolchain",
                    "title": "Cargo Manifest Present",
                    "details": "`Cargo.toml` found configuring Rust editions and dependencies."
                })
            else:
                checks.append({
                    "status": "WARN",
                    "category": "Rust Toolchain",
                    "title": "Missing Cargo.toml",
                    "details": "Rust `.rs` files found without a package `Cargo.toml` manifest."
                })

        # Check Docker & .dockerignore
        has_dockerfile = any("dockerfile" in a.filename.lower() for a in analyses)
        if has_dockerfile:
            if ".dockerignore" in file_names:
                checks.append({
                    "status": "PASS",
                    "category": "Containerization",
                    "title": "Dockerignore Protection",
                    "details": "`.dockerignore` present to avoid sending local cache and node_modules to Docker daemon."
                })
            else:
                checks.append({
                    "status": "WARN",
                    "category": "Containerization",
                    "title": "Missing .dockerignore",
                    "details": "Dockerfile detected without `.dockerignore`. Local build caches or secrets may bloat image layers."
                })

        # Check Git configuration
        if ".gitignore" in file_names:
            checks.append({
                "status": "PASS",
                "category": "Version Control",
                "title": "Git Ignore Hygiene",
                "details": "`.gitignore` found guarding against checking in secrets or build artifacts."
            })
        else:
            checks.append({
                "status": "WARN",
                "category": "Version Control",
                "title": "Missing .gitignore",
                "details": "No `.gitignore` found. Virtual environments or build outputs may be inadvertently committed."
            })

        return checks
