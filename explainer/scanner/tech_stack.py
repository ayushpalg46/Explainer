from pathlib import Path
from typing import List, Dict, Set
from ..models import TechStackInfo, FileAnalysis


class TechStackAnalyzer:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).resolve()

    def analyze(self, files: Dict[str, FileAnalysis]) -> TechStackInfo:
        languages: Dict[str, int] = {}
        frameworks: Set[str] = set()
        libraries: Set[str] = set()
        build_tools: Set[str] = set()
        package_managers: Set[str] = set()
        runtimes: Set[str] = set()
        potential_risks: List[str] = []

        # Count languages from analyzed files
        for f in files.values():
            languages[f.language] = languages.get(f.language, 0) + 1
            for fw in f.frameworks_detected:
                frameworks.add(fw)

        # Inspect manifests in root or repo
        package_json = self.root / "package.json"
        if package_json.exists():
            package_managers.add("npm / yarn / pnpm")
            runtimes.add("Node.js")
            content = package_json.read_text(encoding="utf-8", errors="ignore")
            if "vite" in content:
                build_tools.add("Vite Lightning Bundler")
            if "webpack" in content:
                build_tools.add("Webpack")
            if "tailwind" in content:
                frameworks.add("Tailwind CSS")
            if "react" in content:
                frameworks.add("React.js")
            if "typescript" in content:
                languages["TypeScript"] = languages.get("TypeScript", 0) + 1

        requirements_txt = self.root / "requirements.txt"
        pyproject = self.root / "pyproject.toml"
        if requirements_txt.exists() or pyproject.exists():
            package_managers.add("pip / setuptools")
            runtimes.add("Python 3")
            content = ""
            if requirements_txt.exists():
                content += requirements_txt.read_text(encoding="utf-8", errors="ignore")
            if pyproject.exists():
                content += pyproject.read_text(encoding="utf-8", errors="ignore")
            if "fastapi" in content.lower():
                frameworks.add("FastAPI")
            if "flask" in content.lower():
                frameworks.add("Flask")
            if "django" in content.lower():
                frameworks.add("Django")
            if "rich" in content.lower():
                libraries.add("Rich Terminal UI")

        cargo_toml = self.root / "Cargo.toml"
        if cargo_toml.exists():
            package_managers.add("Cargo")
            runtimes.add("Rust Native Binary (LLVM)")
            build_tools.add("rustc")

        go_mod = self.root / "go.mod"
        if go_mod.exists():
            package_managers.add("go modules")
            runtimes.add("Go Runtime")

        dockerfile = self.root / "Dockerfile"
        if dockerfile.exists() or any("Dockerfile" in p for p in files.keys()):
            build_tools.add("Docker Container Engine")
            runtimes.add("OCI Containerized Sandbox")

        # Compatibility synthesis
        compat_narrative = self._generate_compatibility_narrative(
            languages, list(frameworks), list(package_managers), list(runtimes), list(build_tools)
        )

        return TechStackInfo(
            languages=languages,
            frameworks=sorted(list(frameworks)),
            libraries=sorted(list(libraries)),
            build_tools=sorted(list(build_tools)),
            package_managers=sorted(list(package_managers)),
            runtimes=sorted(list(runtimes)),
            compatibility_analysis=compat_narrative,
            potential_risks_or_upgrades=potential_risks
        )

    def _generate_compatibility_narrative(
        self,
        languages: Dict[str, int],
        frameworks: List[str],
        package_managers: List[str],
        runtimes: List[str],
        build_tools: List[str]
    ) -> str:
        parts = []
        langs_str = ", ".join([f"{k} ({v} files)" for k, v in languages.items()])
        parts.append(f"**Multi-Language Ecosystem**: The codebase is composed of {langs_str}.")

        if "React.js" in frameworks or any("React" in f for f in frameworks):
            parts.append("The frontend leverages modern React declarative components for high-fidelity interactive state management.")

        if "Tailwind CSS" in frameworks or any("Tailwind" in f for f in frameworks):
            parts.append("Styling is streamlined using atomic utility classes compiled ahead of time for minimal production bundle footprint.")

        if any("FastAPI" in f or "Flask" in f or "Django" in f for f in frameworks):
            parts.append("Backend services are driven by high-throughput Python REST/ASGI web frameworks providing asynchronous endpoint routing.")

        if "Docker Container Engine" in build_tools:
            parts.append("Environment parity is guaranteed through Docker containerization, ensuring deterministic deployment across local and cloud targets.")

        if not parts:
            parts.append("Standard modular software architecture with standard compiler/interpreter toolchains.")

        return " ".join(parts)
