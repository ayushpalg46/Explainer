"""
Base data models and abstract parser interface for Explainer.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


@dataclass
class FileSymbol:
    """Represents a code symbol (function, class, component, tag, selector, struct, etc.)"""
    name: str
    kind: str  # e.g., "tag", "component", "function", "class", "hook", "struct", "rule"
    line: int
    signature: str = ""
    description: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)
    sub_elements: List["FileSymbol"] = field(default_factory=list)


@dataclass
class FileImport:
    """Represents an imported module, file, style, or asset."""
    source: str  # imported identifier or module name
    target: str  # path or package name
    line: int
    import_type: str = "static"  # "static", "dynamic", "link", "script", "asset", "macro"


@dataclass
class FileExport:
    """Represents an exported symbol, API route, or component."""
    name: str
    kind: str
    line: int


@dataclass
class FileConnection:
    """
    Represents an explicit or implicit interconnection with another file.
    Explains HOW and WHY the connection works.
    """
    source_file: str
    target_file: str
    relation_type: str  # e.g., "imports", "styles", "mounts", "calls_api", "copies_to_container", "triggers_script"
    mechanism: str      # HOW it works (e.g., "ES6 static import", "<link rel='stylesheet'>", "POST /api/users")
    rationale: str      # WHY it works (e.g., "Applies unified theme rules to DOM", "Separates data models from business logic")
    confidence: float = 1.0  # 1.0 = explicit path, 0.8 = resolved fuzzy/module match


@dataclass
class FileAnalysis:
    """Complete deep analysis artifact for an individual file."""
    path: str
    filename: str
    extension: str
    language: str
    lines_of_code: int
    size_bytes: int
    summary: str
    architecture_role: str
    tech_stack: List[str] = field(default_factory=list)
    symbols: List[FileSymbol] = field(default_factory=list)
    imports: List[FileImport] = field(default_factory=list)
    exports: List[FileExport] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    components_breakdown: List[Dict[str, Any]] = field(default_factory=list)
    outgoing_connections: List[FileConnection] = field(default_factory=list)
    incoming_connections: List[FileConnection] = field(default_factory=list)
    security_and_best_practices: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class BaseParser(ABC):
    """Abstract base class for all language-specific parsers."""

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """List of file extensions supported by this parser (e.g. ['.html', '.htm'])."""
        pass

    @property
    @abstractmethod
    def language_name(self) -> str:
        """Human-readable language name (e.g. 'HTML', 'JavaScript')."""
        pass

    @abstractmethod
    def parse(self, filepath: str, content: str) -> FileAnalysis:
        """
        Parses the given file content and produces a comprehensive FileAnalysis.
        """
        pass
