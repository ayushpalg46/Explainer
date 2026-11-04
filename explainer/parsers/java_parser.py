import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class JavaParser(BaseParser):
    """
    Parses Java source files line-by-line, extracting package declarations,
    imports, annotations, classes, interfaces, and methods with word-by-word
    breakdowns, 4-year-old beginner analogies, and cross-file connections.
    """

    def __init__(self):
        super().__init__(language="Java")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        analysis.beginner_story = (
            "Think of a Java file like a sturdy building blueprint in a bustling city! "
            "Java is very organized and neat: every file has its official address (package), "
            "lists all the tools it borrows from the hardware store (imports), and creates "
            "a sturdy building (class) with special stickers (annotations) telling the JVM "
            "exactly how to construct and wire everything together safely!"
        )

        # Package
        pkg_match = re.search(r'package\s+([a-zA-Z0-9_.]+);', content)
        package_name = pkg_match.group(1) if pkg_match else "default"

        # Imports
        imports = re.findall(r'import\s+(?:static\s+)?([a-zA-Z0-9_.*]+);', content)
        for imp in imports:
            analysis.raw_imports.append(imp)

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("//"):
                continue

            # Package
            if clean.startswith("package ") and clean.endswith(";"):
                words_breakdown = {
                    "package": "Java keyword declaring the namespace package folder path.",
                    package_name: f"The package namespace path `{package_name}`."
                }
                analysis.elements.append(ElementExplanation(
                    name=f"package {package_name}",
                    kind="package",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Java package namespace `{package_name}`.",
                    how_it_is_used=f"Maps to folder structure `{package_name.replace('.', '/')}` in the classpath.",
                    where_it_is_used=f"Header at line {idx}.",
                    why_it_works="The JVM classloader relies on package definitions to resolve class paths.",
                    best_practices_and_pitfalls="Use reverse domain name convention (e.g. `com.company.project`).",
                    simple_analogy="Like writing your postal code and city address on top of an official document!",
                    what_happens_on_screen="Allows other classes in the package to access package-private members.",
                    what_if_removed="Class gets placed into default package, which breaks imports in other packages.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Namespace shared across files in `{package_name}`."
                ))

            # Import
            elif clean.startswith("import ") and clean.endswith(";"):
                imp_target = clean[7:-1].strip()
                words_breakdown = {
                    "import": "Java keyword bringing an external class or package into scope.",
                    imp_target: f"Fully-qualified class or package path."
                }
                analysis.elements.append(ElementExplanation(
                    name=f"import {imp_target}",
                    kind="import",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Java import bringing `{imp_target}` into scope.",
                    how_it_is_used=f"Allows referencing `{imp_target.split('.')[-1]}` without typing the full package prefix.",
                    where_it_is_used=f"Import section at line {idx}.",
                    why_it_works="The Java compiler resolves class tokens against imported packages.",
                    best_practices_and_pitfalls="Avoid wildcard imports (`import foo.*`); use explicit class imports.",
                    simple_analogy="Like bookmarking a page in an encyclopedia so you can flip right to it!",
                    what_happens_on_screen=f"Provides classes from `{imp_target}` to this file.",
                    what_if_removed=f"References to `{imp_target.split('.')[-1]}` will cause compiler 'cannot find symbol' errors.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Dependency link to `{imp_target}`."
                ))

            # Annotation
            elif clean.startswith("@"):
                annot_name = clean[1:].split("(")[0].strip()
                words_breakdown = {
                    f"@{annot_name}": "Declarative metadata annotation processed by compiler or framework."
                }
                analysis.elements.append(ElementExplanation(
                    name=f"@{annot_name}",
                    kind="annotation",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Java annotation `@{annot_name}` providing declarative metadata.",
                    how_it_is_used=f"Decorates the subsequent class or method at line {idx}.",
                    where_it_is_used=f"Annotation decorator at line {idx}.",
                    why_it_works="Processed either at compile time or at runtime via JVM reflection / Spring container.",
                    best_practices_and_pitfalls="Keep configuration clear and avoid hidden side-effects.",
                    simple_analogy=f"Think of @{annot_name} like a special VIP sticker placed on a door giving it special powers!",
                    what_happens_on_screen=f"Triggers framework magic (like dependency injection or HTTP route mapping).",
                    what_if_removed="The framework won't know to wire or manage this component.",
                    words_breakdown=words_breakdown,
                    interconnection_note="Integrates with Spring / Jakarta / JUnit lifecycle."
                ))

            # Class definition
            class_m = re.match(r'(?:public\s+|protected\s+|private\s+)?(?:abstract\s+|final\s+)?class\s+([a-zA-Z0-9_]+)', clean)
            if class_m:
                c_name = class_m.group(1)
                words_breakdown = {
                    "class": "Java keyword defining an object-oriented class blueprint.",
                    c_name: f"Name of the class."
                }
                if "public" in clean:
                    words_breakdown["public"] = "Access modifier allowing access from any package."

                analysis.elements.append(ElementExplanation(
                    name=f"class {c_name}",
                    kind="class",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Java class `{c_name}` defined in package `{package_name}`.",
                    how_it_is_used=f"Forms the primary object-oriented template for `{c_name}` objects.",
                    where_it_is_used=f"Class declaration at line {idx}.",
                    why_it_works="Compiled into a `.class` bytecode file executed by the JVM with GC.",
                    best_practices_and_pitfalls="Maintain strong encapsulation with private fields and getter/setter accessors.",
                    simple_analogy=f"Think of class '{c_name}' like a factory mold that punches out identical toy robots!",
                    what_happens_on_screen=f"Instantiated at runtime to handle business logic or data.",
                    what_if_removed=f"The entire `{c_name}` component disappears from the program.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Instantiated or injected into other service classes across the project."
                ))

        classes = re.findall(r'(?:public\s+|protected\s+|private\s+)?(?:abstract\s+|final\s+)?class\s+([a-zA-Z0-9_]+)', content)
        interfaces = re.findall(r'(?:public\s+)?interface\s+([a-zA-Z0-9_]+)', content)
        annotations = re.findall(r'@([a-zA-Z0-9_]+)', content)

        detected_frameworks = []
        detected_concepts = []

        if any("org.springframework" in imp for imp in imports) or any(a in annotations for a in ["SpringBootApplication", "RestController", "Service", "Component", "Autowired"]):
            detected_frameworks.append("Spring Boot Enterprise Framework")
        if any("jakarta." in imp or "javax." in imp for imp in imports):
            detected_frameworks.append("Jakarta / Java EE")

        if classes:
            detected_concepts.append(f"Java Class OOP Structure ({', '.join(classes[:3])})")
        if interfaces:
            detected_concepts.append(f"Polymorphic Interfaces ({', '.join(interfaces[:3])})")
        if annotations:
            detected_concepts.append(f"Declarative Metadata Annotations (@{', '.join(list(set(annotations))[:4])})")

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks
        analysis.role_in_codebase = "Java Enterprise Backend Service / JVM Component"
        analysis.summary = (
            f"Java source file in package `{package_name}` declaring {len(classes)} class(es), {len(interfaces)} interface(s), "
            f"and using {len(imports)} imports. "
            f"{'Built with ' + ', '.join(detected_frameworks) + '. ' if detected_frameworks else ''}"
        )
        return analysis
