import unittest
from pathlib import Path
from click.testing import CliRunner
from explainer.cli import main, explain_file_cmd
from explainer.parsers.registry import ParserRegistry


class TestSingleFileCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_direct_file_arg_routing(self):
        result = self.runner.invoke(main, ["samples/server.py", "--mode", "static"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("File Overview: server.py", result.output)
        self.assertIn("The Big Picture Story", result.output)
        self.assertIn("Line-by-Line & Word-by-Word Breakdown", result.output)
        self.assertIn("What is written?:", result.output)
        self.assertIn("4-Year-Old Analogy:", result.output)

    def test_schema_sql_single_file(self):
        result = self.runner.invoke(main, ["samples/schema.sql", "--mode", "static"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("File Overview: schema.sql", result.output)
        self.assertIn("CREATE TABLE users", result.output)
        self.assertIn("PRIMARY KEY", result.output)
        self.assertIn("FOREIGN KEY", result.output)
        self.assertIn("SELECT", result.output)

    def test_nginx_conf_single_file(self):
        result = self.runner.invoke(main, ["samples/nginx.conf", "--mode", "static"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("File Overview: nginx.conf", result.output)
        self.assertIn("server", result.output)
        self.assertIn("listen", result.output)
        self.assertIn("proxy_pass", result.output)

    def test_nonexistent_file_error(self):
        result = self.runner.invoke(main, ["non_existent_file.xyz", "--mode", "static"])
        self.assertNotEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
