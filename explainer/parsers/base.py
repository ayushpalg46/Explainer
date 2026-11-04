from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path
from ..models import FileAnalysis, ElementExplanation, FileInterconnection


class BaseParser(ABC):
    """Abstract base class for all file-specific parsers."""

    def __init__(self, language: str):
        self.language = language

    @abstractmethod
    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        """Parse source content and return a deep FileAnalysis object."""
        pass

    def create_base_analysis(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        """Helper to create initial file metadata."""
        lines = content.splitlines()
        size_bytes = len(content.encode("utf-8"))
        return FileAnalysis(
            file_path=file_path,
            relative_path=relative_path,
            language=self.language,
            file_size_bytes=size_bytes,
            line_count=len(lines),
            summary="",
            role_in_codebase="",
            concepts_detected=[],
            frameworks_detected=[],
            elements=[],
            inbound_connections=[],
            outbound_connections=[],
            raw_imports=[],
            raw_exports=[],
        )

