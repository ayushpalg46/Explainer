from pathlib import Path
from typing import Optional
from .base import BaseParser
from .html_parser import HtmlParser
from .css_parser import CssParser
from .js_ts_parser import JsTsParser
from .python_parser import PythonParser
from .rust_parser import RustParser
from .java_parser import JavaParser
from .go_parser import GoParser
from .docker_parser import DockerParser
from .shell_parser import ShellParser
from .generic_parser import GenericParser


class ParserRegistry:
    def __init__(self):
        self._parsers = {
            ".html": HtmlParser(),
            ".htm": HtmlParser(),
            ".css": CssParser(),
            ".scss": CssParser(),
            ".sass": CssParser(),
            ".js": JsTsParser(is_typescript=False, is_jsx=False),
            ".mjs": JsTsParser(is_typescript=False, is_jsx=False),
            ".cjs": JsTsParser(is_typescript=False, is_jsx=False),
            ".jsx": JsTsParser(is_typescript=False, is_jsx=True),
            ".ts": JsTsParser(is_typescript=True, is_jsx=False),
            ".tsx": JsTsParser(is_typescript=True, is_jsx=True),
            ".py": PythonParser(),
            ".rs": RustParser(),
            ".java": JavaParser(),
            ".go": GoParser(),
            ".sh": ShellParser(),
            ".bash": ShellParser(),
            ".zsh": ShellParser(),
            ".json": GenericParser("JSON Data"),
            ".yaml": GenericParser("YAML Configuration"),
            ".yml": GenericParser("YAML Configuration"),
            ".toml": GenericParser("TOML Configuration"),
            ".md": GenericParser("Markdown Documentation"),
        }

    def get_parser_for_path(self, path: Path) -> BaseParser:
        filename = path.name.lower()
        if filename == "dockerfile" or filename.startswith("dockerfile."):
            return DockerParser(is_compose=False)
        if filename in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
            return DockerParser(is_compose=True)

        suffix = path.suffix.lower()
        if suffix in self._parsers:
            return self._parsers[suffix]

        return GenericParser(f"{suffix.upper()[1:] if suffix else 'Plain Text'} File")

