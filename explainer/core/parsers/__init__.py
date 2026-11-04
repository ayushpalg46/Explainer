"""
Parser Registry for Explainer.
Routes files to their optimal language parser based on extension and content.
"""
from typing import Dict, List, Optional
from explainer.core.parsers.base import BaseParser, FileAnalysis
from explainer.core.parsers.html_parser import HTMLFileParser
from explainer.core.parsers.css_parser import CSSFileParser
from explainer.core.parsers.js_ts_jsx_parser import JSTSJSXFileParser
from explainer.core.parsers.python_parser import PythonFileParser
from explainer.core.parsers.rust_parser import RustFileParser
from explainer.core.parsers.java_parser import JavaFileParser
from explainer.core.parsers.go_parser import GoFileParser
from explainer.core.parsers.docker_parser import DockerFileParser
from explainer.core.parsers.shell_parser import ShellFileParser
from explainer.core.parsers.generic_parser import GenericFileParser


class ParserRegistry:
    def __init__(self):
        self._parsers: List[BaseParser] = [
            HTMLFileParser(),
            CSSFileParser(),
            JSTSJSXFileParser(),
            PythonFileParser(),
            RustFileParser(),
            JavaFileParser(),
            GoFileParser(),
            DockerFileParser(),
            ShellFileParser(),
            GenericFileParser(),
        ]
        self._extension_map: Dict[str, BaseParser] = {}
        for p in self._parsers:
            for ext in p.supported_extensions:
                self._extension_map[ext.lower()] = p

    def get_parser(self, filepath: str) -> BaseParser:
        filename = filepath.replace("\\", "/").split("/")[-1].lower()
        if filename.startswith("dockerfile"):
            return self._extension_map.get("dockerfile", GenericFileParser())

        ext = "." + filename.split(".")[-1] if "." in filename else ""
        return self._extension_map.get(ext, GenericFileParser())

    def parse_file(self, filepath: str, content: str) -> FileAnalysis:
        parser = self.get_parser(filepath)
        return parser.parse(filepath, content)


default_registry = ParserRegistry()
