from typing import List
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class GenericParser(BaseParser):
    def __init__(self, language: str = "Configuration / Text"):
        super().__init__(language=language)

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        analysis.concepts_detected = ["Declarative Data / Configuration Schema"]
        analysis.role_in_codebase = "Application Configuration / Metadata / Documentation"
        analysis.summary = f"{self.language} file specifying parameters, structured data, or documentation ({len(lines)} lines)."

        return analysis

