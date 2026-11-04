from __future__ import annotations
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ElementExplanation(BaseModel):
    """Deep pedagogical explanation of a specific tag, component, function, hook, or directive."""
    name: str
    kind: str  # 'tag', 'component', 'hook', 'function', 'class', 'directive', 'property', 'concept', 'animation', 'import'
    line_number: Optional[int] = None
    snippet: Optional[str] = None
    what_it_is: str
    how_it_is_used: str
    where_it_is_used: str
    why_it_works: str
    best_practices_and_pitfalls: Optional[str] = None


class FileInterconnection(BaseModel):
    """Detailed relationship between two files in the codebase."""
    source_file: str
    target_file: str
    relation_type: str  # 'imports', 'styles', 'scripts', 'renders', 'routes_to', 'docker_builds', 'executes'
    how_it_works: str
    why_it_works: str
    code_reference: Optional[str] = None


class FileAnalysis(BaseModel):
    """Super-detailed file-level analysis and breakdown."""
    file_path: str
    relative_path: str
    language: str
    file_size_bytes: int
    line_count: int
    summary: str
    role_in_codebase: str
    concepts_detected: List[str] = Field(default_factory=list)
    frameworks_detected: List[str] = Field(default_factory=list)
    elements: List[ElementExplanation] = Field(default_factory=list)
    inbound_connections: List[FileInterconnection] = Field(default_factory=list)
    outbound_connections: List[FileInterconnection] = Field(default_factory=list)
    design_and_style_notes: Optional[str] = None
    animations_and_interactions: Optional[str] = None
    raw_imports: List[str] = Field(default_factory=list)
    raw_exports: List[str] = Field(default_factory=list)
    ai_insights: Optional[str] = None
    ai_model_used: Optional[str] = None


class TechStackInfo(BaseModel):
    """High-level tech stack and compatibility evaluation."""
    languages: Dict[str, int] = Field(default_factory=dict)
    frameworks: List[str] = Field(default_factory=list)
    libraries: List[str] = Field(default_factory=list)
    build_tools: List[str] = Field(default_factory=list)
    package_managers: List[str] = Field(default_factory=list)
    runtimes: List[str] = Field(default_factory=list)
    compatibility_analysis: str = ""
    potential_risks_or_upgrades: List[str] = Field(default_factory=list)


class CodebaseAnalysis(BaseModel):
    """Complete comprehensive dossier of the analyzed codebase."""
    root_path: str
    project_name: str
    total_files: int
    total_lines: int
    tech_stack: TechStackInfo
    architecture_style: str
    architecture_summary: str
    folder_roles: Dict[str, str] = Field(default_factory=dict)
    files: Dict[str, FileAnalysis] = Field(default_factory=dict)
    interconnections: List[FileInterconnection] = Field(default_factory=list)
    engine_used: str = "Rule/AST Deep Knowledge Engine"
    ai_model_name: Optional[str] = None
    ai_architecture_critique: Optional[str] = None

