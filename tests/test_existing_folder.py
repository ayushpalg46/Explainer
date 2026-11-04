import pytest
from pathlib import Path
import tempfile
import shutil
from explainer.scanner.workspace_scanner import WorkspaceScanner
from explainer.models import FileAnalysis, TechStackInfo, CodebaseAnalysis, ElementExplanation
from explainer.renderers.markdown_renderer import MarkdownRenderer


class TestExistingFolderBehavior:
    def test_scanner_prunes_all_expl_folders(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_p = Path(tmp_dir)
            (tmp_p / "main.py").write_text("print('hello')", encoding="utf-8")

            # Create standard -EXPL folder
            expl_dir = tmp_p / "app-EXPL"
            expl_dir.mkdir()
            (expl_dir / "INDEX.md").write_text("# Old Index", encoding="utf-8")

            # Create timestamped -EXPL folder
            timestamped_dir = tmp_p / "app-EXPL-20261104_104500"
            timestamped_dir.mkdir()
            (timestamped_dir / "INDEX.md").write_text("# Old Timestamped Index", encoding="utf-8")

            scanner = WorkspaceScanner(str(tmp_p))
            scanned = scanner.scan()

            rel_paths = [r for _, r in scanned]
            assert "main.py" in rel_paths
            # Must NOT scan any -EXPL files
            for p in rel_paths:
                assert "-EXPL" not in p

    def test_renderer_cleans_stale_markdown_files_on_update(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_dir = Path(tmp_dir) / "output-EXPL"
            files_dir = out_dir / "files"
            files_dir.mkdir(parents=True)

            # Create a stale markdown file from a previously deleted source file
            stale_file = files_dir / "deleted_file.py.md"
            stale_file.write_text("# Stale old file", encoding="utf-8")
            assert stale_file.exists()

            # Render new analysis with only current_file.py
            fa = FileAnalysis(
                file_path="current_file.py",
                relative_path="current_file.py",
                language="Python",
                file_size_bytes=20,
                line_count=1,
                summary="Current file",
                role_in_codebase="Script",
                elements=[]
            )
            analysis = CodebaseAnalysis(
                root_path=tmp_dir,
                project_name="TestApp",
                total_files=1,
                total_lines=1,
                tech_stack=TechStackInfo(),
                architecture_style="Modular",
                architecture_summary="Test summary",
                files={"current_file.py": fa}
            )

            renderer = MarkdownRenderer()
            renderer.render_multi_file_dossier(analysis, str(out_dir))

            # The new file must exist, and the stale file MUST be cleaned up!
            assert (files_dir / "current_file.py.md").exists()
            assert not stale_file.exists()
