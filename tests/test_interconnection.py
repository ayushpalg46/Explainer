import unittest
from explainer.core.interconnection import InterconnectionGraph
from explainer.core.parsers.html_parser import HTMLFileParser
from explainer.core.parsers.css_parser import CSSFileParser


class TestInterconnection(unittest.TestCase):
    def test_interconnection_linking(self):
        html_code = '<html><head><link rel="stylesheet" href="style.css"></head></html>'
        css_code = 'body { color: red; }'

        html_a = HTMLFileParser().parse("index.html", html_code)
        css_a = CSSFileParser().parse("style.css", css_code)

        graph = InterconnectionGraph([html_a, css_a])
        graph.build_graph()

        links = graph.edges
        self.assertGreaterEqual(len(links), 1)
        self.assertEqual(links[0]["from"], "index.html")
        self.assertEqual(links[0]["to"], "style.css")
        self.assertEqual(links[0]["type"], "styles")
        self.assertIn("style.css", links[0]["how"])


if __name__ == "__main__":
    unittest.main()
