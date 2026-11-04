import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class JavaParser(BaseParser):
    def __init__(self):
        super().__init__(language="Java")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)

        # Package
        pkg_match = re.search(r'package\s+([a-zA-Z0-9_.]+);', content)
        package_name = pkg_match.group(1) if pkg_match else "default"

        # Imports
        imports = re.findall(r'import\s+(?:static\s+)?([a-zA-Z0-9_.*]+);', content)
        for imp in imports:
            analysis.raw_imports.append(imp)

        # Classes, Interfaces, Enums
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

        # Element explanations
        for c in classes[:5]:
            analysis.elements.append(ElementExplanation(
                name=f"class {c}",
                kind="class",
                snippet=f"public class {c} {{ ... }}",
                what_it_is=f"Java class `{c}` defined in package `{package_name}`.",
                how_it_is_used="Forms a core object-oriented building block compiled to JVM bytecode.",
                where_it_is_used=f"Belongs to package `{package_name}`.",
                why_it_works="Executed by the JVM with automatic garbage collection and runtime classloading.",
                best_practices_and_pitfalls="Maintain strong encapsulation with private fields and descriptive method contracts."
            ))

        for a in list(set(annotations))[:4]:
            analysis.elements.append(ElementExplanation(
                name=f"@{a}",
                kind="annotation",
                snippet=f"@{a}",
                what_it_is=f"Java annotation `@{a}` providing declarative metadata.",
                how_it_is_used="Applied to classes or methods to trigger runtime dependency injection or validation.",
                where_it_is_used="Decorates declarations in this file.",
                why_it_works="Processed either at compile time via annotation processors or at runtime via JVM reflection.",
                best_practices_and_pitfalls="Keep configuration centralized and avoid excessive hidden reflection magic."
            ))

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = detected_frameworks
        analysis.role_in_codebase = "Java Enterprise Backend Service / JVM Component"
        analysis.summary = (
            f"Java source file in package `{package_name}` declaring {len(classes)} class(es), {len(interfaces)} interface(s), "
            f"and using {len(imports)} imports. "
            f"{'Built with ' + ', '.join(detected_frameworks) + '. ' if detected_frameworks else ''}"
        )
        return analysis
