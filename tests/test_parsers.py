import unittest
from explainer.parsers.html_parser import HtmlParser
from explainer.parsers.css_parser import CssParser
from explainer.parsers.js_ts_parser import JsTsParser
from explainer.parsers.python_parser import PythonParser
from explainer.parsers.rust_parser import RustParser
from explainer.parsers.java_parser import JavaParser
from explainer.parsers.go_parser import GoParser
from explainer.parsers.docker_parser import DockerParser
from explainer.parsers.shell_parser import ShellParser
from explainer.parsers.generic_parser import GenericParser


class TestFileParsers(unittest.TestCase):
    def test_html_parser(self):
        content = """<!DOCTYPE html>
        <html lang="en">
        <head>
          <title>Test Page</title>
          <link rel="stylesheet" href="style.css">
          <script src="app.js"></script>
        </head>
        <body>
          <div id="root">
            <header><h1>Title</h1></header>
            <canvas id="stage"></canvas>
          </div>
        </body>
        </html>"""
        parser = HtmlParser()
        analysis = parser.parse("index.html", content, "index.html")

        self.assertEqual(analysis.language, "HTML")
        self.assertIn("style.css", analysis.raw_imports)
        self.assertIn("app.js", analysis.raw_imports)
        tag_names = [e.name for e in analysis.elements]
        self.assertIn("<html>", tag_names)
        self.assertIn("<canvas>", tag_names)
        self.assertTrue(any("SPA" in c for c in analysis.concepts_detected))
        self.assertTrue(len(analysis.elements) > 0)
        first_el = analysis.elements[0]
        self.assertTrue(first_el.simple_analogy)
        self.assertTrue(first_el.words_breakdown)
        self.assertTrue(first_el.what_happens_on_screen)
        self.assertTrue(first_el.what_if_removed)

    def test_css_parser(self):
        content = """
        :root { --main-bg: #121212; }
        .hero { display: flex; justify-content: center; align-items: center; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(3, 1fr); }
        @keyframes pulse { 0% { opacity: 0; } 100% { opacity: 1; } }
        @media (min-width: 1024px) { .hero { padding: 40px; } }
        """
        parser = CssParser()
        analysis = parser.parse("style.css", content, "style.css")

        self.assertEqual(analysis.language, "CSS")
        self.assertTrue(any("Flexbox" in c for c in analysis.concepts_detected))
        self.assertTrue(any("CSS Grid" in c for c in analysis.concepts_detected))
        self.assertTrue(any("pulse" in c for c in analysis.concepts_detected))
        self.assertTrue(len(analysis.elements) > 0)
        el = analysis.elements[1]
        self.assertTrue(el.words_breakdown)
        self.assertTrue(el.simple_analogy)

    def test_js_ts_jsx_parser(self):
        content = """
        import React, { useState, useEffect } from 'react';
        import { Button } from './components/Button';
        import './style.css';

        export function Counter() {
            const [val, setVal] = useState(0);
            useEffect(() => { document.title = `Count: ${val}`; }, [val]);
            return <Button onClick={() => setVal(val + 1)}>Count</Button>;
        }
        """
        parser = JsTsParser(is_typescript=False, is_jsx=True)
        analysis = parser.parse("Counter.jsx", content, "Counter.jsx")

        self.assertIn("React.js", analysis.frameworks_detected)
        self.assertIn("./components/Button", analysis.raw_imports)
        self.assertTrue(any("useState" in e.name for e in analysis.elements))
        self.assertTrue(any("Counter" in e.name for e in analysis.elements))
        btn_el = [e for e in analysis.elements if "useState" in e.name][0]
        self.assertTrue(btn_el.words_breakdown)
        self.assertTrue(btn_el.simple_analogy)

    def test_python_parser(self):
        content = """
        from dataclasses import dataclass
        import sys

        @dataclass
        class Config:
            host: str
            port: int

        def start_server(cfg: Config) -> bool:
            return True
        """
        parser = PythonParser()
        analysis = parser.parse("server.py", content, "server.py")

        self.assertEqual(analysis.language, "Python")
        self.assertIn("sys", analysis.raw_imports)
        names = [e.name for e in analysis.elements]
        self.assertTrue(any("Config" in n for n in names))
        self.assertTrue(any("start_server" in n for n in names))
        cfg_el = [e for e in analysis.elements if "Config" in e.name][0]
        self.assertTrue(cfg_el.words_breakdown)
        self.assertTrue(cfg_el.simple_analogy)

    def test_rust_parser(self):
        content = """
        use std::collections::HashMap;
        pub struct Cache {
            data: HashMap<String, u64>,
        }
        pub fn init_cache() -> Cache {
            Cache { data: HashMap::new() }
        }
        """
        parser = RustParser()
        analysis = parser.parse("engine.rs", content, "engine.rs")

        self.assertEqual(analysis.language, "Rust")
        self.assertTrue(any("Cache" in e.name for e in analysis.elements))
        cache_el = [e for e in analysis.elements if "Cache" in e.name][0]
        self.assertTrue(cache_el.words_breakdown)
        self.assertTrue(cache_el.simple_analogy)

    def test_java_parser(self):
        content = """
        package com.example.service;
        import org.springframework.stereotype.Service;

        @Service
        public class PaymentService {
            public boolean process() { return true; }
        }
        """
        parser = JavaParser()
        analysis = parser.parse("PaymentService.java", content, "PaymentService.java")

        self.assertEqual(analysis.language, "Java")
        self.assertTrue(any("Spring Boot" in f for f in analysis.frameworks_detected))
        self.assertTrue(any("PaymentService" in e.name for e in analysis.elements))
        ps_el = [e for e in analysis.elements if "PaymentService" in e.name][0]
        self.assertTrue(ps_el.words_breakdown)
        self.assertTrue(ps_el.simple_analogy)

    def test_go_parser(self):
        content = """
        package main
        import "net/http"

        type Server struct {
            Port string
        }

        func handleHome(w http.ResponseWriter, r *http.Request) {
            w.Write([]byte("ok"))
        }
        """
        parser = GoParser()
        analysis = parser.parse("main.go", content, "main.go")

        self.assertEqual(analysis.language, "Go")
        self.assertTrue(any("Server" in e.name for e in analysis.elements))
        srv_el = [e for e in analysis.elements if "Server" in e.name][0]
        self.assertTrue(srv_el.words_breakdown)
        self.assertTrue(srv_el.simple_analogy)

    def test_docker_parser(self):
        content = """
        FROM node:20-alpine AS builder
        WORKDIR /app
        COPY package.json .
        RUN npm install
        COPY . .
        EXPOSE 3000
        CMD ["npm", "start"]
        """
        parser = DockerParser()
        analysis = parser.parse("Dockerfile", content, "Dockerfile")

        self.assertEqual(analysis.language, "Dockerfile")
        self.assertIn("package.json", analysis.raw_imports)
        self.assertTrue(any("FROM" in e.name for e in analysis.elements))
        from_el = [e for e in analysis.elements if "FROM" in e.name][0]
        self.assertTrue(from_el.words_breakdown)
        self.assertTrue(from_el.simple_analogy)
        self.assertTrue(from_el.what_if_removed)

    def test_shell_parser(self):
        content = """#!/usr/bin/env bash
        set -euo pipefail
        source ./config.sh
        docker build -t app:latest .
        """
        parser = ShellParser()
        analysis = parser.parse("build.sh", content, "build.sh")

        self.assertEqual(analysis.language, "Shell Script")
        self.assertIn("./config.sh", analysis.raw_imports)
        self.assertTrue(len(analysis.elements) > 0)
        sh_el = analysis.elements[0]
        self.assertTrue(sh_el.words_breakdown)
        self.assertTrue(sh_el.simple_analogy)

    def test_generic_manifest_parser(self):
        pkg_content = """{
            "name": "my-web-app",
            "version": "1.0.0",
            "scripts": { "dev": "vite", "build": "vite build" },
            "dependencies": { "react": "^18.2.0" }
        }"""
        parser = GenericParser()
        analysis = parser.parse("package.json", pkg_content, "package.json")
        self.assertIn("react", analysis.raw_imports)
        self.assertTrue(any("vite" in e.how_it_is_used for e in analysis.elements))
        el = analysis.elements[0]
        self.assertTrue(el.words_breakdown)
        self.assertTrue(el.simple_analogy)


    def test_user_exact_toy_box_example(self):
        content = """<div id="root" class="container">
  <h1 class="title">My Toy Box</h1>
  <button class="btn-magic" onclick="openBox()">Open Box!</button>
</div>
<link rel="stylesheet" href="style.css">
<script src="app.js"></script>"""
        parser = HtmlParser()
        analysis = parser.parse("index.html", content, "index.html")

        from explainer.renderers.markdown_renderer import MarkdownRenderer
        from explainer.models import CodebaseAnalysis, TechStackInfo

        codebase = CodebaseAnalysis(
            root_path=".",
            project_name="ToyBoxApp",
            total_files=1,
            total_lines=len(content.splitlines()),
            tech_stack=TechStackInfo(languages={"HTML": 1}),
            files={"index.html": analysis},
            architecture_style="Single Page Application (SPA)",
            architecture_summary="Single page application structure."
        )

        renderer = MarkdownRenderer()
        md = renderer._build_single_file_markdown("index.html", analysis, codebase)

        # Verify exact standard formatting requested by user
        self.assertIn("#### 🧸 1. The Big Picture Story (What is this code?)", md)
        self.assertIn("│ \"Imagine this code is a real physical toy box sitting on a stage", md)
        self.assertIn("──────", md)
        self.assertIn("#### 🔍 2. Line-by-Line & Word-by-Word Breakdown", md)
        self.assertIn("#### Line 1: <span style=\"color: #3b82f6;\"><font color=\"#3b82f6\">`<div id=\"root\" class=\"container\">`</font></span>", md)
        self.assertIn("• What is written?: A <div> tag with 2 label(s): id=\"root\" and class=\"container\".", md)
        self.assertIn("• What does every word mean?:", md)
        self.assertIn("• div: Short for \"division\". An invisible cardboard box used to bundle things together.", md)
        self.assertIn("• id=\"root\": A unique name-tag (like a personal ID card).", md)
        self.assertIn("• class=\"container\": A style group label / costume label.", md)
        self.assertIn("• 🧸 4-Year-Old Analogy: Think of this like setting down an empty laundry basket before you put clothes in it.", md)
        self.assertIn("• 🖥️ What happens on screen?: Nothing visible yet! It creates an invisible box on a new line where child elements will sit.", md)
        self.assertIn("• 🔗 Interconnection with other files:", md)
        self.assertIn("app.js searches for this exact box using document.getElementById('root')", md)
        self.assertIn("• 💥 What breaks if deleted?: The title and button lose their container, spill across the screen", md)
        self.assertIn("#### Line 2: <span style=\"color: #3b82f6;\"><font color=\"#3b82f6\">`<h1 class=\"title\">My Toy Box</h1>`</font></span>", md)
        self.assertIn("#### Line 3: <span style=\"color: #3b82f6;\"><font color=\"#3b82f6\">`<button class=\"btn-magic\" onclick=\"openBox()\">Open Box!</button>`</font></span>", md)
        self.assertIn("#### Line 5: <span style=\"color: #3b82f6;\"><font color=\"#3b82f6\">`<link rel=\"stylesheet\" href=\"style.css\">`</font></span>", md)
        self.assertIn("#### Line 6: <span style=\"color: #3b82f6;\"><font color=\"#3b82f6\">`<script src=\"app.js\"></script>`</font></span>", md)


if __name__ == "__main__":
    unittest.main()
