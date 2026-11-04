"""
Java Class, Annotation, and Spring/Enterprise Framework Parser for Explainer.
Analyzes package structures, imports, classes, interfaces, annotations, methods, and Spring dependency injections.
"""
import re
from typing import List, Dict, Any
from explainer.core.parsers.base import BaseParser, FileAnalysis, FileSymbol, FileImport, FileExport, FileConnection


class JavaFileParser(BaseParser):
    @property
    def supported_extensions(self) -> List[str]:
        return [".java"]

    @property
    def language_name(self) -> str:
        return "Java"

    def parse(self, filepath: str, content: str) -> FileAnalysis:
        lines = content.splitlines()
        loc = len(lines)
        size_bytes = len(content.encode("utf-8"))
        filename = filepath.replace("\\", "/").split("/")[-1]

        symbols: List[FileSymbol] = []
        imports: List[FileImport] = []
        exports: List[FileExport] = []
        connections: List[FileConnection] = []
        tech_stack: List[str] = ["Java"]
        concepts: List[str] = []
        components_breakdown: List[Dict[str, Any]] = []
        security_and_practices: List[str] = []

        # 1. Package Declaration
        pkg_match = re.search(r"package\s+([a-zA-Z0-9_.]+);", content)
        package_name = pkg_match.group(1) if pkg_match else ""
        if package_name:
            concepts.append(f"Java Namespace Package: `{package_name}`")

        # 2. Imports
        import_matches = re.finditer(r"import\s+(?:static\s+)?([a-zA-Z0-9_.*]+);", content)
        for m in import_matches:
            target = m.group(1)
            line_num = content[:m.start()].count("\n") + 1
            imports.append(FileImport(
                source=target.split(".")[-1],
                target=target,
                line=line_num,
                import_type="java_import"
            ))
            self._classify_import(target, tech_stack)

        # 3. Annotations
        annotations = re.findall(r"@([A-Z][a-zA-Z0-9_]*(?:\([^)]*\))?)", content)
        clean_annotations = [a.split("(")[0] for a in annotations]
        unique_annotations = sorted(list(set(clean_annotations)))
        if unique_annotations:
            concepts.append(f"Enterprise Annotations ({', '.join(f'@{a}' for a in unique_annotations[:8])})")
            if any("Spring" in s for s in tech_stack) or any(a in ("RestController", "Service", "Repository", "Autowired", "SpringBootApplication") for a in unique_annotations):
                tech_stack.append("Spring Boot Framework")

        # 4. Classes and Interfaces
        type_pattern = re.finditer(
            r"(?:public|protected|private)?\s*(?:static)?\s*(?:final)?\s*(?:abstract)?\s*(class|interface|enum|record)\s+([A-Z][a-zA-Z0-9_]*)"
            r"(?:\s+extends\s+([A-Z][a-zA-Z0-9_<>.]+))?(?:\s+implements\s+([A-Z][a-zA-Z0-9_<>.,\s]+))?",
            content
        )
        type_names = []
        for m in type_pattern:
            kind = m.group(1)
            name = m.group(2)
            extends_type = m.group(3) or ""
            implements_type = m.group(4) or ""
            line_num = content[:m.start()].count("\n") + 1
            type_names.append(name)

            sig = f"{kind} {name}"
            if extends_type:
                sig += f" extends {extends_type}"
            if implements_type:
                sig += f" implements {implements_type}"

            symbols.append(FileSymbol(
                name=name,
                kind=f"java_{kind}",
                line=line_num,
                signature=sig,
                description=f"Java {kind} declaring {name} type contract and implementation."
            ))
            exports.append(FileExport(name=name, kind=kind, line=line_num))

        if type_names:
            concepts.append(f"Object-Oriented Architecture ({', '.join(type_names)})")

        # 5. Methods
        method_pattern = re.finditer(
            r"(?:public|protected|private)\s+(?:static\s+)?(?:final\s+)?(?:[a-zA-Z0-9_<>[\]]+)\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)\s*(?:throws\s+[^{]+)?\{",
            content
        )
        methods = []
        for m in method_pattern:
            m_name = m.group(1)
            m_args = m.group(2)
            if m_name in type_names:
                continue  # skip constructor for now
            line_num = content[:m.start()].count("\n") + 1
            methods.append(m_name)
            symbols.append(FileSymbol(
                name=m_name,
                kind="java_method",
                line=line_num,
                signature=f"{m_name}({m_args})",
                description=f"Method implementing {m_name} operation."
            ))

        # 6. REST Routes / Endpoints
        routes = re.findall(r"@(Get|Post|Put|Delete|Patch)Mapping\s*\(\s*(?:value\s*=\s*)?['\"]([^'\"]+)['\"]", content)
        if routes:
            concepts.append(f"Spring Web REST Endpoints ({len(routes)} mapped routes)")
            for verb, path in routes:
                connections.append(FileConnection(
                    source_file=filepath,
                    target_file=path,
                    relation_type="exposes_api",
                    mechanism=f"@{verb}Mapping('{path}')",
                    rationale="Exposes HTTP REST endpoint for web clients or microservice communication."
                ))

        # Components breakdown
        components_breakdown.append({
            "section": "Package & External Libraries",
            "details": f"Package: '{package_name or 'default'}'. Imports {len(imports)} classes. Detected stacks: {', '.join(set(tech_stack))}."
        })
        components_breakdown.append({
            "section": "Declared Types & Classes",
            "details": f"Defines {len(type_names)} types: {', '.join(type_names)} with {len(methods)} member methods."
        })
        if routes:
            components_breakdown.append({
                "section": "Spring REST Route Mappings",
                "details": "; ".join(f"[{verb.upper()}] {path}" for verb, path in routes)
            })

        summary = f"Java source file ({filename}) belonging to package '{package_name or 'default'}', defining {len(type_names)} type(s) and {len(methods)} method(s)."
        if any(a in unique_annotations for a in ("RestController", "Controller")):
            arch_role = "Spring REST Controller / API Layer"
        elif "Service" in unique_annotations:
            arch_role = "Service Layer / Business Logic"
        elif "Repository" in unique_annotations:
            arch_role = "Data Access Object / Repository Layer"
        elif "Entity" in unique_annotations or "Table" in unique_annotations:
            arch_role = "JPA / Hibernate Database Entity Model"
        else:
            arch_role = "Core Java Domain Component"

        return FileAnalysis(
            path=filepath,
            filename=filename,
            extension=".java",
            language="Java",
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
            tags=["java", "enterprise", "backend", "spring" if "Spring Boot Framework" in tech_stack else "oop"]
        )

    def _classify_import(self, target: str, stack: List[str]):
        if "org.springframework" in target:
            stack.append("Spring Framework")
        elif "javax.persistence" in target or "jakarta.persistence" in target:
            stack.append("JPA / Hibernate Persistence")
        elif "org.junit" in target:
            stack.append("JUnit Testing Framework")
        elif "lombok" in target:
            stack.append("Project Lombok Annotations")
