import re
import json
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class GenericParser(BaseParser):
    """
    Parses configuration manifests (package.json, requirements.txt, .env,
    JSON, YAML, TOML, Markdown) line-by-line with word-by-word breakdowns,
    4-year-old beginner analogies, what happens on screen/in computer,
    and dependency interconnections.
    """

    def __init__(self, language: str = "Configuration / Text"):
        super().__init__(language=language)

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()
        filename = relative_path.lower().split("/")[-1].split("\\")[-1]

        # 1. Specialized: package.json
        if filename == "package.json":
            return self._parse_package_json(analysis, content, lines)

        # 2. Specialized: requirements.txt
        if filename == "requirements.txt" or filename.endswith(".requirements.txt"):
            return self._parse_requirements_txt(analysis, content, lines)

        # 3. Specialized: .env or .env.*
        if filename == ".env" or filename.startswith(".env."):
            return self._parse_env_file(analysis, content, lines)

        # 4. General JSON
        if filename.endswith(".json"):
            return self._parse_general_json(analysis, content, lines)

        # 5. General YAML / TOML
        if filename.endswith(".yaml") or filename.endswith(".yml") or filename.endswith(".toml"):
            return self._parse_yaml_toml(analysis, content, lines)

        # 6. Markdown documentation
        if filename.endswith(".md"):
            return self._parse_markdown(analysis, content, lines)

        # Default fallback
        analysis.beginner_story = (
            f"Think of this {self.language} file like a set of written instructions or notes "
            "kept in a folder so the computer and programmers always remember how everything is configured!"
        )
        analysis.concepts_detected = ["Declarative Data / Configuration Schema"]
        analysis.role_in_codebase = "Application Configuration / Metadata / Documentation"
        analysis.summary = f"{self.language} file specifying parameters, structured data, or documentation ({len(lines)} lines)."
        return analysis

    def _parse_package_json(self, analysis: FileAnalysis, content: str, lines: List[str]) -> FileAnalysis:
        analysis.language = "Node.js Manifest (package.json)"
        analysis.beginner_story = (
            "Think of package.json like the birth certificate and shopping list for a JavaScript or React project! "
            "It gives the project its official name, lists all the ready-made toy boxes (npm packages) it needs to download "
            "from the internet, and writes down shortcut buttons (scripts) so you can type 'npm run dev' to start the app!"
        )
        analysis.role_in_codebase = "JavaScript / Node.js Package Manifest & Script Orchestrator"
        analysis.frameworks_detected = ["Node.js / npm Ecosystem"]

        try:
            data = json.loads(content)
        except Exception:
            data = {}

        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        scripts = data.get("scripts", {})

        analysis.concepts_detected = [
            f"npm Package Manifest ({len(deps)} production deps, {len(dev_deps)} dev deps)",
            f"Lifecycle Automation Scripts ({len(scripts)} scripts)"
        ]

        for pkg, ver in deps.items():
            analysis.raw_imports.append(pkg)

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            # Scripts
            if any(f'"{s}"' in clean for s in scripts):
                for s, cmd in scripts.items():
                    if f'"{s}"' in clean:
                        analysis.elements.append(ElementExplanation(
                            name=f"npm script: '{s}'",
                            kind="script",
                            line_number=idx,
                            snippet=clean,
                            what_it_is=f"Automation command shortcut `{s}`.",
                            how_it_is_used=f"Executed via `npm run {s}` to run: `{cmd}`.",
                            where_it_is_used=f"Scripts block at line {idx}.",
                            why_it_works="npm reads the scripts object and executes the command in a subshell with node_modules/.bin on PATH.",
                            best_practices_and_pitfalls="Keep scripts cross-platform (use tools like cross-env or rimraf).",
                            simple_analogy=f"Think of '{s}' like a custom shortcut button on a microwave that cooks your popcorn in one press!",
                            what_happens_on_screen=f"Typing `npm run {s}` launches the `{cmd}` task in your terminal.",
                            what_if_removed=f"Developers won't have the `npm run {s}` shortcut command.",
                            words_breakdown={s: "The script shortcut name.", cmd: "The actual command line instruction executed."},
                            interconnection_note=f"Orchestrates build, start, or test tasks across project files."
                        ))

            # Dependencies
            if any(f'"{d}"' in clean for d in deps):
                for d, ver in deps.items():
                    if f'"{d}"' in clean:
                        analysis.elements.append(ElementExplanation(
                            name=f"dependency: {d}",
                            kind="dependency",
                            line_number=idx,
                            snippet=clean,
                            what_it_is=f"Production npm dependency library `{d}` (version `{ver}`).",
                            how_it_is_used=f"Installed into `node_modules` and imported in `.js` / `.ts` files.",
                            where_it_is_used=f"Dependencies at line {idx}.",
                            why_it_works="The npm package manager downloads this library and resolves its transitive dependencies.",
                            best_practices_and_pitfalls="Regularly run `npm audit` to check for security vulnerabilities.",
                            simple_analogy=f"Think of package '{d}' like buying a pre-made Lego wheel set instead of carving wheels from scratch!",
                            what_happens_on_screen=f"Installs `{d}` so files can do `import ... from '{d}'`.",
                            what_if_removed=f"Any code file importing `{d}` will throw `Cannot find module '{d}'` error.",
                            words_breakdown={d: "The npm package name.", ver: "Semantic version range requirement."},
                            interconnection_note=f"Imported by JavaScript/TypeScript source files in this project."
                        ))

        analysis.summary = (
            f"Node.js package manifest defining project `{data.get('name', 'unnamed')}` v{data.get('version', '0.0.0')}. "
            f"Declares {len(deps)} production dependency package(s), {len(dev_deps)} development tool(s), "
            f"and {len(scripts)} automated task script(s)."
        )
        return analysis

    def _parse_requirements_txt(self, analysis: FileAnalysis, content: str, lines: List[str]) -> FileAnalysis:
        analysis.language = "Python Manifest (requirements.txt)"
        analysis.beginner_story = (
            "Think of requirements.txt like a grocery list for a Python program! "
            "Before Python can cook your yummy software cake, it looks at this list to see what ingredients "
            "(like FastAPI, PyTest, or Requests) it needs to buy from the internet using `pip install`!"
        )
        analysis.role_in_codebase = "Python Dependency Manifest"
        analysis.frameworks_detected = ["Python / pip Ecosystem"]

        pkgs = []
        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue

            # e.g. fastapi==0.100.0 or requests>=2.28
            m = re.match(r'^([a-zA-Z0-9_\-\.]+)(?:([=><~^!]+)(.*))?$', clean)
            if m:
                pkg = m.group(1)
                op = m.group(2) or "any"
                ver = m.group(3) or "latest"
                pkgs.append(pkg)
                analysis.raw_imports.append(pkg)

                analysis.elements.append(ElementExplanation(
                    name=f"package: {pkg}",
                    kind="dependency",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Python dependency package `{pkg}` ({op} {ver}).",
                    how_it_is_used=f"Installed via `pip install -r requirements.txt` and imported in `.py` files.",
                    where_it_is_used=f"Line {idx} manifest entry.",
                    why_it_works="pip downloads wheel binaries from PyPI and installs them into your Python virtual environment.",
                    best_practices_and_pitfalls="Pin exact versions (`==`) in production to prevent unexpected breaking changes.",
                    simple_analogy=f"Think of '{pkg}' like an ingredient on your recipe card (like '2 cups of chocolate chips')!",
                    what_happens_on_screen=f"Downloads `{pkg}` so your Python files can run `import {pkg}` without errors.",
                    what_if_removed=f"Python files importing `{pkg}` will crash with `ModuleNotFoundError: No module named '{pkg}'`.",
                    words_breakdown={pkg: "Python package name on PyPI.", f"{op}{ver}": "Version constraint pinning."},
                    interconnection_note=f"Imported by Python files (like `server.py` or `models.py`) in this project."
                ))

        analysis.concepts_detected = [f"Python Package List ({len(pkgs)} packages pinned)"]
        analysis.summary = f"Python requirements manifest specifying {len(pkgs)} library dependency requirement(s) for pip."
        return analysis

    def _parse_env_file(self, analysis: FileAnalysis, content: str, lines: List[str]) -> FileAnalysis:
        analysis.language = "Environment Configuration (.env)"
        analysis.beginner_story = (
            "Think of a .env file like a secret diary of settings for your application! "
            "It holds things like secret passwords, database keys, and port numbers so they aren't "
            "written directly inside the code. This way, you can keep your secrets safe and change settings easily!"
        )
        analysis.role_in_codebase = "Environment Variables & Configuration Secrets"

        env_keys = []
        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue

            if "=" in clean:
                k, v = clean.split("=", 1)
                k = k.strip()
                v = v.strip()
                env_keys.append(k)

                analysis.elements.append(ElementExplanation(
                    name=f"ENV: {k}",
                    kind="environment_variable",
                    line_number=idx,
                    snippet=f"{k}=...",
                    what_it_is=f"Environment variable `{k}`.",
                    how_it_is_used=f"Read at runtime via `os.environ.get('{k}')` or `process.env.{k}`.",
                    where_it_is_used=f"Configuration line {idx}.",
                    why_it_works="Injected into the process environment table during application boot.",
                    best_practices_and_pitfalls="NEVER commit real production secrets (.env) to git repositories; add to .gitignore.",
                    simple_analogy=f"Think of {k} like a secret combination code written on a sticky note under your keyboard!",
                    what_happens_on_screen="Configures database URLs, port numbers, or API keys without code changes.",
                    what_if_removed="The application may crash on startup due to missing configuration settings.",
                    words_breakdown={k: "Variable name identifier.", "=": "Assignment operator."},
                    interconnection_note="Injected into backend server scripts and container runtimes."
                ))

        analysis.concepts_detected = [f"Environment Configuration ({len(env_keys)} variables)"]
        analysis.summary = f"Environment variable configuration declaring {len(env_keys)} runtime parameter(s)."
        return analysis

    def _parse_general_json(self, analysis: FileAnalysis, content: str, lines: List[str]) -> FileAnalysis:
        analysis.beginner_story = (
            "Think of a JSON file like a neat collection of labeled cubbyholes! "
            "Each cubbyhole has a name tag (key) and holds a specific toy or note (value). "
            "Computers all around the world love reading JSON because it is super tidy and organized!"
        )
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                for k, v in list(data.items())[:10]:
                    analysis.elements.append(ElementExplanation(
                        name=f"Key: \"{k}\"",
                        kind="json_key",
                        line_number=None,
                        snippet=f'"{k}": {json.dumps(v)[:40]}...',
                        what_it_is=f"JSON top-level key `{k}` holding type `{type(v).__name__}`.",
                        how_it_is_used=f"Parsed and queried by application components.",
                        where_it_is_used="Top-level JSON property.",
                        why_it_works="Parsed into native dictionary/hash map by JSON parser.",
                        best_practices_and_pitfalls="Validate against a JSON Schema to prevent unexpected null values.",
                        simple_analogy=f"Like a labeled sticker on a drawer: open '{k}' to find its contents!",
                        what_happens_on_screen="Supplies structured data to UI views or backend services.",
                        what_if_removed="Code attempting to access this key will get null or an undefined error.",
                        words_breakdown={f'"{k}"': "The property name key.", f"{type(v).__name__}": "Value data type."}
                    ))
        except Exception:
            pass

        analysis.concepts_detected = ["Structured JSON Data"]
        analysis.summary = f"JSON data document with {len(lines)} lines."
        return analysis

    def _parse_yaml_toml(self, analysis: FileAnalysis, content: str, lines: List[str]) -> FileAnalysis:
        analysis.beginner_story = (
            "Think of this configuration file like a rulebook for your software! "
            "It uses clean indentation to group settings into chapters and rules so the software "
            "knows exactly how to behave when you turn it on."
        )
        for idx, line in enumerate(lines[:15], 1):
            clean = line.strip()
            if clean and not clean.startswith("#") and ":" in clean:
                k = clean.split(":", 1)[0].strip()
                analysis.elements.append(ElementExplanation(
                    name=f"Config: {k}",
                    kind="setting",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Configuration parameter `{k}`.",
                    how_it_is_used=f"Configured at line {idx}.",
                    where_it_is_used=f"Configuration line {idx}.",
                    why_it_works="Parsed into runtime configuration object.",
                    best_practices_and_pitfalls="Use consistent spacing; YAML is sensitive to tabs vs spaces.",
                    simple_analogy=f"Like setting the temperature dial on an air conditioner to keep the room comfortable!",
                    what_happens_on_screen="Adjusts runtime behavior or features.",
                    what_if_removed="The software falls back to default settings or fails validation.",
                    words_breakdown={k: "Configuration setting key."}
                ))

        analysis.concepts_detected = ["Declarative Configuration Schema"]
        analysis.summary = f"Configuration file with {len(lines)} lines."
        return analysis

    def _parse_markdown(self, analysis: FileAnalysis, content: str, lines: List[str]) -> FileAnalysis:
        analysis.beginner_story = (
            "Think of a Markdown file like a friendly guidebook or storybook for human programmers! "
            "It explains what the project does, how to install it, and teaches people how to use it "
            "with nice headings, bullet points, and code examples!"
        )
        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if clean.startswith("#"):
                analysis.elements.append(ElementExplanation(
                    name=f"Heading: {clean[:40]}",
                    kind="documentation_heading",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Documentation heading: `{clean}`.",
                    how_it_is_used=f"Organizes markdown documentation into structured sections.",
                    where_it_is_used=f"Section header at line {idx}.",
                    why_it_works="Rendered into semantic HTML `<h1-h6>` elements by markdown processors.",
                    best_practices_and_pitfalls="Use single H1 for the page title, followed by hierarchical H2 and H3 headings.",
                    simple_analogy="Like the chapter title in a storybook so you know what the chapter is about!",
                    what_happens_on_screen="Renders as a bold, prominent section title on GitHub or documentation websites.",
                    what_if_removed="The documentation loses its clear visual structure and becomes hard to skim.",
                    words_breakdown={"#": "Markdown heading marker signaling text size and importance."}
                ))

        analysis.concepts_detected = ["Technical Documentation & Specifications"]
        analysis.summary = f"Markdown documentation file containing {len(lines)} lines of specifications and instructions."
        return analysis
