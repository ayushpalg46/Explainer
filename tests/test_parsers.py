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


if __name__ == "__main__":
    unittest.main()
