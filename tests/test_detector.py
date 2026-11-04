import unittest
from explainer.core.detector import ProjectDetector
from explainer.core.parsers.html_parser import HTMLFileParser
from explainer.core.parsers.python_parser import PythonFileParser


class TestProjectDetector(unittest.TestCase):
    def test_detector_architecture_classification(self):
        html_a = HTMLFileParser().parse("index.html", "<html><body><h1>App</h1></body></html>")
        py_a = PythonFileParser().parse("main.py", "def run(): pass")

        detector = ProjectDetector(".")
        arch = detector.detect_architecture([html_a, py_a])

        self.assertIn("Full-Stack", arch["architecture_type"])
        self.assertEqual(arch["total_files"], 2)
        self.assertIn("HTML", arch["languages"])
        self.assertIn("Python", arch["languages"])

    def test_detector_compatibility_checks(self):
        py_a = PythonFileParser().parse("main.py", "print('hello')")
        detector = ProjectDetector(".")
        checks = detector.evaluate_compatibility([py_a])

        self.assertTrue(any(c["category"] == "Python Ecosystem" for c in checks))


if __name__ == "__main__":
    unittest.main()
