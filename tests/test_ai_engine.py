import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from explainer.models import FileAnalysis, TechStackInfo, FileInterconnection, ElementExplanation
from explainer.engine.ai_engine import AIExplainerEngine
from explainer.renderers.markdown_renderer import MarkdownRenderer


class TestAIEngine:
    @patch("requests.post")
    def test_ai_engine_full_analysis(self, mock_post):
        # Mock Ollama API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Deep AI breakdown: This file provides state management and lifecycle hooks."
        }
        mock_post.return_value = mock_response

        engine = AIExplainerEngine(
            endpoint_url="http://localhost:11434/api/generate",
            model_name="mock-coder-model",
            provider="ollama"
        )

        sample_file = FileAnalysis(
            file_path="src/App.jsx",
            relative_path="src/App.jsx",
            language="JavaScript/React",
            file_size_bytes=1024,
            line_count=45,
            summary="Main React component",
            role_in_codebase="UI Root",
            elements=[
                ElementExplanation(
                    name="useState",
                    kind="hook",
                    line_number=5,
                    what_it_is="React state hook",
                    how_it_is_used="Stores component state",
                    where_it_is_used="Top level function body",
                    why_it_works="Maintains state across re-renders"
                )
            ]
        )

        files = {"src/App.jsx": sample_file}
        tech_stack = TechStackInfo(
            languages={"JavaScript": 1},
            frameworks=["React"],
            compatibility_analysis="Compatible"
        )
        interconnections = []

        progress_calls = []
        def on_progress(c, t, f):
            progress_calls.append((c, t, f))

        analysis = engine.analyze_codebase(
            root_path=".",
            files=files,
            tech_stack=tech_stack,
            interconnections=interconnections,
            progress_callback=on_progress
        )

        # Assert AI model output was populated
        assert analysis.ai_model_name == "mock-coder-model"
        assert analysis.ai_architecture_critique is not None
        assert "Deep AI breakdown" in analysis.ai_architecture_critique

        file_res = analysis.files["src/App.jsx"]
        assert file_res.ai_insights is not None
        assert "Deep AI breakdown" in file_res.ai_insights
        assert file_res.ai_model_used == "mock-coder-model"
        assert len(progress_calls) == 1
        assert progress_calls[0] == (1, 1, "src/App.jsx")

        # Verify Markdown Renderer includes AI sections
        renderer = MarkdownRenderer()
        single_md = renderer._build_single_file_markdown("src/App.jsx", file_res, analysis)
        assert "🧠 Neural AI Deep Code Analysis (`mock-coder-model`)" in single_md
        assert "Deep AI breakdown" in single_md

        index_md = renderer._build_index_markdown(analysis, {})
        assert "🧠 Neural AI Architectural Review (`mock-coder-model`)" in index_md
