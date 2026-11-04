import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class GoParser(BaseParser):
    """
    Parses Go source files line-by-line, extracting package declarations,
    imports, structs, interfaces, functions, and concurrency primitives with
    word-by-word breakdowns, 4-year-old beginner analogies, and cross-file links.
    """

    def __init__(self):
        super().__init__(language="Go")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        analysis.beginner_story = (
            "Think of a Go file like a super fast sports car engine assembled with snap-together Lego blocks! "
            "Go keeps things very simple: each file belongs to a team (package), lists its tools (imports), "
            "draws blueprints for objects (structs), and has workers (functions) that run super fast. If you need "
            "multiple workers doing jobs at the same time, Go gives them magical walkie-talkies called channels!"
        )

        # Package
        pkg_match = re.search(r'package\s+([a-zA-Z0-9_]+)', content)
        package_name = pkg_match.group(1) if pkg_match else "main"

        # Imports
        import_block = re.search(r'import\s*\((.*?)\)', content, re.DOTALL)
        if import_block:
            for imp in re.findall(r'["\']([^"\']+)["\']', import_block.group(1)):
                analysis.raw_imports.append(imp)
        for single in re.findall(r'import\s+["\']([^"\']+)["\']', content):
            if single not in analysis.raw_imports:
                analysis.raw_imports.append(single)

        # Structs, Interfaces, Functions with line numbers
        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("//"):
                continue

            # Package declaration
            if clean.startswith("package "):
                words_breakdown = {
                    "package": "Go keyword that declares the package namespace for all declarations in this file.",
                    package_name: f"The package name '{package_name}'. If named 'main', it compiles into an executable program."
                }
                analysis.elements.append(ElementExplanation(
                    name=f"package {package_name}",
                    kind="package",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Go package declaration organizing code into the `{package_name}` namespace.",
                    how_it_is_used=f"Groups all declarations in this file under the `{package_name}` package boundary.",
                    where_it_is_used=f"Header of file at line {idx}.",
                    why_it_works="The Go compiler links all files sharing the same package declaration into a single compiled unit.",
                    best_practices_and_pitfalls="Package names should be short, lowercase, and concise (e.g. `http`, `models`).",
                    simple_analogy=f"Think of package '{package_name}' like a name badge on a sports jersey so teammates recognize each other!",
                    what_happens_on_screen="Allows other files in this package to share functions without extra imports.",
                    what_if_removed="Go compilation fails because every Go file must begin with a package clause.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Shared across all files in the `{package_name}` package."
                ))

            # Import single
            elif clean.startswith("import ") and "(" not in clean:
                imp_match = re.search(r'import\s+["\']([^"\']+)["\']', clean)
                if imp_match:
                    pkg = imp_match.group(1)
                    analysis.elements.append(ElementExplanation(
                        name=f"import \"{pkg}\"",
                        kind="import",
                        line_number=idx,
                        snippet=clean,
                        what_it_is=f"Go package import bringing in external package `{pkg}`.",
                        how_it_is_used=f"Allows this file to call functions and types exposed by `{pkg}`.",
                        where_it_is_used=f"Line {idx} import section.",
                        why_it_works="The Go module resolver links the symbol table of `{pkg}` during compilation.",
                        best_practices_and_pitfalls="Go strictly forbids unused imports; remove any import not called.",
                        simple_analogy=f"Think of import like opening your toolbox and taking out a specialized wrench from the '{pkg}' workshop!",
                        what_happens_on_screen="Provides external capabilities (like HTTP servers or JSON parsing) to this file.",
                        what_if_removed=f"Any code using `{pkg}` will fail to compile.",
                        words_breakdown={"import": "Keyword declaring external dependency.", f"\"{pkg}\"": f"Path/module name of imported package."},
                        interconnection_note=f"External or internal dependency link to `{pkg}`."
                    ))

            # Struct definition
            struct_m = re.match(r'type\s+([a-zA-Z0-9_]+)\s+struct', clean)
            if struct_m:
                s_name = struct_m.group(1)
                analysis.elements.append(ElementExplanation(
                    name=f"type {s_name} struct",
                    kind="struct",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Go composite data structure `{s_name}`.",
                    how_it_is_used=f"Defines typed memory layout and fields for representing `{s_name}` entities.",
                    where_it_is_used=f"Type definition at line {idx}.",
                    why_it_works="Allocated contiguously in memory for minimal CPU cache misses and fast GC scanning.",
                    best_practices_and_pitfalls="Add struct tags (e.g. `json:\"name\"`) to govern serialization.",
                    simple_analogy=f"Think of struct '{s_name}' like a custom identity card with labeled slots for name, photo, and age!",
                    what_happens_on_screen=f"Models structured `{s_name}` data in memory.",
                    what_if_removed=f"Any function expecting a `{s_name}` object will report a type error.",
                    words_breakdown={"type": "Declares a new named type.", s_name: f"Name of the custom type.", "struct": "Go keyword for composite data structure."},
                    interconnection_note=f"Data model passed between functions and API endpoints across this project."
                ))

            # Function definition
            func_m = re.match(r'func\s+(?:\(([^)]+)\)\s+)?([a-zA-Z0-9_]+)\s*\((.*?)\)', clean)
            if func_m:
                receiver = func_m.group(1)
                f_name = func_m.group(2)
                params = func_m.group(3)
                words_breakdown = {
                    "func": "Go keyword declaring a function or method.",
                    f_name: f"The identifier name of this routine.",
                    "()": "Parameter parentheses defining input arguments."
                }
                if receiver:
                    words_breakdown[f"({receiver})"] = "Method receiver binding this function to a struct instance."

                analysis.elements.append(ElementExplanation(
                    name=f"func {f_name}()",
                    kind="function",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Go {'method' if receiver else 'function'} `{f_name}`.",
                    how_it_is_used=f"Executes procedural logic with explicit parameters `({params[:40]})`.",
                    where_it_is_used=f"Line {idx} routine declaration.",
                    why_it_works="Compiled directly into native machine instructions with Go runtime stack management.",
                    best_practices_and_pitfalls="Always check returned error values immediately (`if err != nil`).",
                    simple_analogy=f"Think of function '{f_name}' like a magical recipe card: you give it ingredients and it does the job!",
                    what_happens_on_screen=f"Executes `{f_name}` logic when invoked.",
                    what_if_removed=f"Callers invoking `{f_name}` will fail to compile.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Callable across the `{package_name}` package or exported if capitalized."
                ))

        has_goroutine = bool(re.search(r'\bgo\s+[a-zA-Z0-9_]+|\bgo\s+func\(', content))
        has_channel = bool(re.search(r'\bchan\s+|<-', content))

        detected_frameworks = []
        detected_concepts = []

        all_imports = " ".join(analysis.raw_imports)
        if "gin-gonic" in all_imports:
            detected_frameworks.append("Gin Web Framework")
        if "gorm.io" in all_imports:
            detected_frameworks.append("GORM ORM")
        if "net/http" in all_imports:
            detected_frameworks.append("Go Standard net/http")

        structs = re.findall(r'type\s+([a-zA-Z0-9_]+)\s+struct', content)
        interfaces = re.findall(r'type\s+([a-zA-Z0-9_]+)\s+interface', content)
        functions = re.findall(r'func\s+(?:\([^)]+\)\s+)?([a-zA-Z0-9_]+)\s*\(', content)

        if structs:
            detected_concepts.append(f"Go Composite Structs ({', '.join(structs[:3])})")
        if interfaces:
            detected_concepts.append(f"Implicit Go Interfaces ({', '.join(interfaces[:3])})")
        if has_goroutine or has_channel:
            detected_concepts.append("CSP Concurrency (Goroutines & Channels)")

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks
        analysis.role_in_codebase = "Go Cloud Microservice / High-Performance Backend Routine"
        analysis.summary = (
            f"Go source file in package `{package_name}` with {len(structs)} struct(s), {len(interfaces)} interface(s), "
            f"and {len(functions)} function(s). Uses {len(analysis.raw_imports)} package imports. "
            f"{'Features lightweight goroutine concurrency. ' if has_goroutine else ''}"
        )
        return analysis
