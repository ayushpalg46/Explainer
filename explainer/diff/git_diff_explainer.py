import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Callable, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from ..parsers.registry import ParserRegistry
from ..models import ElementExplanation
from ..engine.ai_engine import AIExplainerEngine


@dataclass
class DiffLine:
    line_number: Optional[int]
    line_type: str  # '+', '-', ' '
    content: str


@dataclass
class DiffHunk:
    header: str
    old_start: int
    new_start: int
    lines: List[DiffLine] = field(default_factory=list)


@dataclass
class DiffFile:
    old_path: str
    new_path: str
    language: str
    status: str  # 'modified', 'added', 'deleted'
    hunks: List[DiffHunk] = field(default_factory=list)
    added_lines: List[DiffLine] = field(default_factory=list)


@dataclass
class DiffLineExplanation:
    file_path: str
    line_number: Optional[int]
    code_line: str
    what_is_written: str
    words_breakdown: Dict[str, str] = field(default_factory=dict)
    simple_analogy: str = ""
    what_happens_on_screen: str = ""
    interconnection_note: str = ""
    what_breaks_if_deleted: str = ""


@dataclass
class DiffAnalysis:
    ref: Optional[str]
    total_files_changed: int
    total_lines_added: int
    total_lines_deleted: int
    files: List[DiffFile] = field(default_factory=list)
    big_picture_story: str = ""
    line_explanations: List[DiffLineExplanation] = field(default_factory=list)
    ai_insights: Optional[str] = None
    ai_model_used: Optional[str] = None


class GitDiffExplainer:
    """
    Extracts, parses, and provides line-by-line & word-by-word beginner-friendly
    explanations of Git diff changes (Without-AI and AI modes).
    """

    def __init__(self, repo_dir: str = "."):
        self.repo_dir = Path(repo_dir).resolve()
        self.parser_registry = ParserRegistry()

    def get_git_diff(self, ref: Optional[str] = None, staged: bool = False) -> Tuple[str, str]:
        """Runs git diff to retrieve unified diff text."""
        cmd = ["git", "diff", "-U3"]
        if staged:
            cmd.append("--staged")
        if ref:
            cmd.append(ref)

        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                check=False
            )
            output = res.stdout
            if not output.strip() and not ref and not staged:
                # Check if staged has changes
                staged_res = subprocess.run(
                    ["git", "diff", "--staged", "-U3"],
                    cwd=str(self.repo_dir),
                    capture_output=True,
                    text=True,
                    check=False
                )
                if staged_res.stdout.strip():
                    return staged_res.stdout, "staged changes"

                # Check previous commit HEAD~1
                head_res = subprocess.run(
                    ["git", "diff", "HEAD~1", "-U3"],
                    cwd=str(self.repo_dir),
                    capture_output=True,
                    text=True,
                    check=False
                )
                if head_res.stdout.strip():
                    return head_res.stdout, "latest commit (HEAD~1)"

            return output, ref or ("staged" if staged else "working tree")
        except FileNotFoundError:
            return "", "git not found"
        except Exception as e:
            return "", f"error: {str(e)}"

    def parse_diff(self, raw_diff: str) -> List[DiffFile]:
        """Parses unified diff output into structured DiffFile and DiffLine objects."""
        if not raw_diff.strip():
            return []

        files: List[DiffFile] = []
        current_file: Optional[DiffFile] = None
        current_hunk: Optional[DiffHunk] = None
        current_new_line_num = 1

        file_header_re = re.compile(r"^diff --git a/(.*) b/(.*)$")
        hunk_header_re = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$")

        for line in raw_diff.splitlines():
            m_file = file_header_re.match(line)
            if m_file:
                old_p, new_p = m_file.group(1), m_file.group(2)
                ext = Path(new_p).suffix.lower()
                lang = self._detect_language(ext)
                current_file = DiffFile(
                    old_path=old_p,
                    new_path=new_p,
                    language=lang,
                    status="modified"
                )
                files.append(current_file)
                current_hunk = None
                continue

            if current_file is None:
                continue

            if line.startswith("new file mode"):
                current_file.status = "added"
                continue
            elif line.startswith("deleted file mode"):
                current_file.status = "deleted"
                continue

            m_hunk = hunk_header_re.match(line)
            if m_hunk:
                old_start = int(m_hunk.group(1))
                new_start = int(m_hunk.group(2))
                current_new_line_num = new_start
                current_hunk = DiffHunk(
                    header=line,
                    old_start=old_start,
                    new_start=new_start
                )
                current_file.hunks.append(current_hunk)
                continue

            if current_hunk is None:
                continue

            if line.startswith("+") and not line.startswith("+++"):
                content = line[1:]
                dl = DiffLine(
                    line_number=current_new_line_num,
                    line_type="+",
                    content=content
                )
                current_hunk.lines.append(dl)
                current_file.added_lines.append(dl)
                current_new_line_num += 1
            elif line.startswith("-") and not line.startswith("---"):
                content = line[1:]
                dl = DiffLine(
                    line_number=None,
                    line_type="-",
                    content=content
                )
                current_hunk.lines.append(dl)
            elif line.startswith(" "):
                content = line[1:]
                dl = DiffLine(
                    line_number=current_new_line_num,
                    line_type=" ",
                    content=content
                )
                current_hunk.lines.append(dl)
                current_new_line_num += 1

        return files

    def analyze_diff(
        self,
        files: List[DiffFile],
        ref_label: str,
        mode: str = "static",
        ai_engine: Optional[AIExplainerEngine] = None,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> DiffAnalysis:
        total_added = sum(len(f.added_lines) for f in files)
        total_deleted = sum(
            sum(1 for l in h.lines if l.line_type == "-")
            for f in files for h in f.hunks
        )

        file_names = [f.new_path for f in files]
        file_summary = ", ".join(file_names[:3]) + (f" and {len(file_names)-3} more" if len(file_names) > 3 else "")

        story = (
            f"Imagine you and your friend are working on a giant Lego project. "
            f"In this update ({ref_label}), someone adjusted {len(files)} file(s) ({file_summary}), "
            f"adding {total_added} shiny new Lego bricks and taking away {total_deleted} old bricks. "
            f"Every new line is a new instruction telling the computer to draw something new, remember new information, "
            f"or connect two parts together!"
        )

        analysis = DiffAnalysis(
            ref=ref_label,
            total_files_changed=len(files),
            total_lines_added=total_added,
            total_lines_deleted=total_deleted,
            files=files,
            big_picture_story=story
        )

        # 1. Deterministic Rule / AST Explanations for added lines
        for f in files:
            parser = self.parser_registry.get_parser_for_path(Path(f.new_path))
            for line_obj in f.added_lines:
                raw_code = line_obj.content.strip()
                if not raw_code:
                    continue

                line_exp = self._explain_single_line_rule(
                    file_path=f.new_path,
                    language=f.language,
                    line_num=line_obj.line_number,
                    raw_code=raw_code,
                    parser=parser
                )
                analysis.line_explanations.append(line_exp)

        # 2. AI Mode Deep Neural Walkthrough (if enabled)
        if mode == "ai" and ai_engine:
            diff_text = self._build_diff_prompt_text(files)
            prompt = (
                f"{ai_engine.SYSTEM_PROMPT}\n\n"
                f"You are explaining a Git Diff code modification to an absolute beginner / 4-year-old child.\n"
                f"Reference: {ref_label}\n"
                f"Changed Files: {', '.join(file_names)}\n\n"
                f"DIFF CONTENT:\n```\n{diff_text}\n```\n\n"
                f"You MUST format your output in this EXACT standard format:\n\n"
                f"#### 🧸 1. The Big Picture Story (What is this code change?)\n\n"
                f"│ \"[A vivid 4-year-old real-world toy/repair story explaining what changed and why in 2-3 sentences]\"\n"
                f"──────\n"
                f"#### 🔍 2. Line-by-Line & Word-by-Word Breakdown\n\n"
                f"For every changed/added line:\n\n"
                f"#### Line X: <span style=\"color: #3b82f6;\"><font color=\"#3b82f6\">`[exact changed code line]`</font></span>\n\n"
                f"• What is written?: [Plain English description of what was added or modified]\n"
                f"• What does every word mean?:\n"
                f"    • [word/keyword]: [Simple definition]\n"
                f"• 🧸 4-Year-Old Analogy: [Vivid everyday toy/kitchen analogy]\n"
                f"• 🖥️ What happens on screen / in system?: [What the user sees or what changes in computer memory]\n"
                f"• 🔗 Interconnection with other files:\n"
                f"    • [How this change impacts other parts of the codebase]\n"
                f"• 💥 What breaks if deleted?: [What breaks, crashes, or fails if this change is reverted]\n"
                f"──────\n"
            )
            ai_out = ai_engine._send_prompt(
                prompt,
                max_tokens=900,
                temperature=0.3,
                stream_callback=stream_callback
            )
            if ai_out:
                analysis.ai_insights = ai_out
                analysis.ai_model_used = ai_engine.model_name

        return analysis

    def _explain_single_line_rule(
        self,
        file_path: str,
        language: str,
        line_num: Optional[int],
        raw_code: str,
        parser
    ) -> DiffLineExplanation:
        """Generates standard 6-bullet line explanation using deterministic parser knowledge."""
        # Try parsing small snippet via parser
        words_breakdown = {}
        simple_analogy = ""
        screen_effect = "Executes new instructions inside computer memory."
        interconn = f"Affects runtime behavior in `{file_path}`."
        what_breaks = "The new feature or bugfix will be lost, reverting to older behavior."
        what_written = f"Added statement: `{raw_code}`"

        # Check for imports
        if any(raw_code.startswith(k) for k in ("import ", "from ", "#include", "require(", "using ")):
            what_written = f"Import directive loading outside helper code: `{raw_code}`"
            simple_analogy = "Like ordering a special wrench from the hardware store before starting to build."
            screen_effect = "Nothing visible yet; equips the program with new tools."
            interconn = "Establishes a direct dependency on an external or internal module."
            what_breaks = "Code calling functions from this import will immediately crash with unresolved symbol errors."
            words_breakdown = {"import": "Keyword telling the computer to fetch outside tools", "module": "The helper package being imported"}

        # Check for function/method definitions
        elif any(k in raw_code for k in ("def ", "function ", "fn ", "func ", "public void ", "const ")):
            what_written = f"New function or constant declaration: `{raw_code}`"
            simple_analogy = "Like writing down a new recipe in a cookbook so anyone in the kitchen can bake it."
            screen_effect = "Prepares a new reusable action or stores a constant value in memory."
            interconn = "Other functions or files can now invoke this new routine."
            what_breaks = "Any other part of the code attempting to call this will crash because the recipe is missing."
            words_breakdown = {"def/function": "Recipe maker command", "identifier": "The custom name given to this new action"}

        # Check for HTML tags
        elif raw_code.startswith("<") and ">" in raw_code:
            tag_match = re.match(r"<([a-zA-Z0-9_-]+)", raw_code)
            tag_name = tag_match.group(1) if tag_match else "element"
            what_written = f"HTML UI element `<{tag_name}>` added to the interface."
            simple_analogy = f"Like placing a new physical `{tag_name}` object onto the display table."
            screen_effect = f"Renders a new `{tag_name}` element on the user's screen."
            interconn = "Can be styled by CSS files and manipulated by JavaScript code."
            what_breaks = f"The user interface will be missing this `{tag_name}` component."
            words_breakdown = {tag_name: f"HTML tag instructing the browser to draw a {tag_name}"}

        # Check for CSS rules
        elif ":" in raw_code and (raw_code.endswith(";") or "{" in raw_code):
            prop = raw_code.split(":")[0].strip()
            val = raw_code.split(":")[1].replace(";", "").strip()
            what_written = f"CSS visual style rule applying `{val}` to `{prop}`."
            simple_analogy = "Like dipping the paintbrush in a new color or adjusting the size of a picture frame."
            screen_effect = f"Immediately adjusts `{prop}` on matching visual elements."
            interconn = "Dictates the visual appearance of HTML elements targeted by this selector."
            what_breaks = "Elements revert to default ugly browser styles or lose proper spacing/colors."
            words_breakdown = {prop: "The visual property being adjusted", val: "The specific setting or measurement applied"}

        # Check for SQL statements
        elif any(k in raw_code.upper() for k in ("CREATE TABLE", "SELECT", "INSERT", "ALTER", "PRIMARY KEY", "FOREIGN KEY")):
            what_written = f"SQL database schema or query statement: `{raw_code}`"
            simple_analogy = "Like putting a new organized filing cabinet or search label inside the library archives."
            screen_effect = "Updates database tables or reads/writes persistent records on disk."
            interconn = "Backend API services querying this table will use this new structure."
            what_breaks = "Database operations will fail to store or retrieve records properly."
            words_breakdown = {"SQL": "Database instruction language", "Statement": "Command to organize or query persistent data"}

        # Generic assignment or expression
        else:
            what_written = f"Executed code line: `{raw_code}`"
            simple_analogy = "Like a tiny gear clicking into place inside a toy clock."
            words_breakdown = {"Code": "Direct computer instructions"}

        return DiffLineExplanation(
            file_path=file_path,
            line_number=line_num,
            code_line=raw_code,
            what_is_written=what_written,
            words_breakdown=words_breakdown,
            simple_analogy=simple_analogy,
            what_happens_on_screen=screen_effect,
            interconnection_note=interconn,
            what_breaks_if_deleted=what_breaks
        )

    def _build_diff_prompt_text(self, files: List[DiffFile]) -> str:
        """Builds a condensed representation of the diff for AI prompt context."""
        parts = []
        for f in files:
            parts.append(f"--- a/{f.old_path}\n+++ b/{f.new_path}")
            for h in f.hunks:
                parts.append(h.header)
                for l in h.lines[:30]:  # limit lines per hunk to fit token budget
                    prefix = l.line_type
                    parts.append(f"{prefix}{l.content}")
        diff_str = "\n".join(parts)
        return diff_str[:4000]

    def _detect_language(self, ext: str) -> str:
        m = {
            ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
            ".jsx": "React JSX", ".tsx": "React TSX", ".html": "HTML",
            ".css": "CSS", ".sql": "SQL", ".conf": "Config",
            ".rs": "Rust", ".go": "Go", ".java": "Java", ".sh": "Shell"
        }
        return m.get(ext, "Source Code")
