import unittest
from explainer.diff.git_diff_explainer import GitDiffExplainer, DiffFile, DiffLine
from explainer.parsers.registry import ParserRegistry


SAMPLE_DIFF = """diff --git a/server.py b/server.py
index 1111111..2222222 100644
--- a/server.py
+++ b/server.py
@@ -10,6 +10,8 @@ def start_server():
     app = Flask(__name__)
+    import jwt
+    token = request.headers.get("Authorization")
     return app
diff --git a/schema.sql b/schema.sql
new file mode 100644
index 0000000..3333333
--- /dev/null
+++ b/schema.sql
@@ -0,0 +1,5 @@
+CREATE TABLE accounts (
+    id INT PRIMARY KEY,
+    balance DECIMAL(10,2) NOT NULL
+);
"""


class TestGitDiffExplainer(unittest.TestCase):
    def test_parse_diff(self):
        explainer = GitDiffExplainer()
        files = explainer.parse_diff(SAMPLE_DIFF)

        self.assertEqual(len(files), 2)
        f1 = files[0]
        self.assertEqual(f1.new_path, "server.py")
        self.assertEqual(f1.language, "Python")
        self.assertEqual(len(f1.added_lines), 2)
        self.assertIn("import jwt", f1.added_lines[0].content)

        f2 = files[1]
        self.assertEqual(f2.new_path, "schema.sql")
        self.assertEqual(f2.status, "added")
        self.assertEqual(len(f2.added_lines), 4)

    def test_analyze_diff_static_mode(self):
        explainer = GitDiffExplainer()
        files = explainer.parse_diff(SAMPLE_DIFF)
        analysis = explainer.analyze_diff(files, "sample-ref", mode="static")

        self.assertEqual(analysis.total_files_changed, 2)
        self.assertTrue(len(analysis.line_explanations) > 0)
        self.assertTrue(analysis.big_picture_story)
        self.assertIn("Lego", analysis.big_picture_story)

        # Check Python line explanation
        jwt_exp = [e for e in analysis.line_explanations if "import jwt" in e.code_line][0]
        self.assertTrue(jwt_exp.simple_analogy)
        self.assertIn("import", jwt_exp.words_breakdown)
        self.assertTrue(jwt_exp.what_happens_on_screen)
        self.assertTrue(jwt_exp.what_breaks_if_deleted)

        # Check SQL line explanation
        sql_exp = [e for e in analysis.line_explanations if "CREATE TABLE" in e.code_line][0]
        self.assertTrue(sql_exp.simple_analogy)
        self.assertIn("CREATE TABLE", sql_exp.what_is_written)


if __name__ == "__main__":
    unittest.main()
