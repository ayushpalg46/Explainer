import unittest
from explainer.models import FileAnalysis, TechStackInfo
from explainer.graph.dependency_builder import DependencyGraphBuilder
from explainer.engine.rule_engine import RuleExplainerEngine


class TestGraphAndEngine(unittest.TestCase):
    def test_dependency_builder(self):
        html_fa = FileAnalysis(
            file_path="/app/index.html",
            relative_path="index.html",
            language="HTML",
            file_size_bytes=200,
            line_count=20,
            summary="HTML index",
            role_in_codebase="Entrypoint",
            raw_imports=["styles.css", "./src/app.js"]
        )

        css_fa = FileAnalysis(
            file_path="/app/styles.css",
            relative_path="styles.css",
            language="CSS",
            file_size_bytes=150,
            line_count=15,
            summary="Global CSS",
            role_in_codebase="Styles"
        )

        js_fa = FileAnalysis(
            file_path="/app/src/app.js",
            relative_path="src/app.js",
            language="JavaScript",
            file_size_bytes=300,
            line_count=30,
            summary="App logic",
            role_in_codebase="Logic",
            raw_imports=["../styles.css"]
        )

        files = {
            "index.html": html_fa,
            "styles.css": css_fa,
            "src/app.js": js_fa
        }

        builder = DependencyGraphBuilder(files)
        conns = builder.build_interconnections()

        self.assertGreaterEqual(len(conns), 2)
        # Verify index.html -> styles.css
        h_css = [c for c in conns if c.source_file == "index.html" and c.target_file == "styles.css"]
        self.assertEqual(len(h_css), 1)
        self.assertEqual(h_css[0].relation_type, "styles")
        self.assertIn("CSSOM", h_css[0].how_it_works)

    def test_rule_engine_synthesis(self):
        files = {
            "index.html": FileAnalysis(
                file_path="/app/index.html", relative_path="index.html", language="HTML",
                file_size_bytes=100, line_count=10, summary="HTML", role_in_codebase="View"
            )
        }
        tech_stack = TechStackInfo(
            languages={"HTML": 1},
            frameworks=["React.js"],
            compatibility_analysis="Multi-language ecosystem test."
        )

        engine = RuleExplainerEngine()
        codebase = engine.analyze_codebase("/app", files, tech_stack, [])
        self.assertEqual(codebase.project_name, "app")
        self.assertIn("Single Page Application", codebase.architecture_style)
        self.assertIn("root", codebase.folder_roles)


if __name__ == "__main__":
    unittest.main()
