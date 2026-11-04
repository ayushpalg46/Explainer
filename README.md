# ⚡ Explainer: Dual-Engine Codebase & Deep File Architecture Analysis Tool

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Engine: Dual](https://img.shields.io/badge/Engine-Zero--AI%20%7C%20Local%20LLM-emerald.svg)](#dual-engine-architecture)

**Explainer** is a high-precision, deep-dive software intelligence engine that analyzes, dissects, and explains entire codebases and individual files in exhaustive pedagogical detail.

It uncovers architecture styles, audits tech stack compatibility, generates cross-file interconnection graphs explaining **HOW** and **WHY** files connect, and inspects every element, tag, symbol, and design concept across **all major programming formats** (`.html`, `.css`, `.js`, `.jsx`, `.ts`, `.tsx`, `.py`, `.rs`, `.java`, `.go`, `Dockerfile`, `.sh`).

---

## 🌟 Key Highlights

### 1. Dual-Engine Parity Workflow
Explainer gives users the choice between two operating modes with **identical analytical depth**:
- ⚡ **Pure Knowledge & AST Engine (Zero-AI Deterministic Mode)**:
  - 100% Offline, instantaneous, zero GPU/VRAM requirement.
  - Pure grammar parsing, tokenizer, and deterministic architectural rule engine.
  - Generates the exact same rich, exhaustive breakdown as an AI model.
- 🧠 **Local AI Brain Mode**:
  - Connects to local Ollama models (`qwen35-uncensored`, `qwen2.5-coder`, `llama3`, etc.) or LM Studio / local OpenAI-compatible endpoints.
  - Synthesizes conversational summaries and contextual analogies.

---

### 2. Supported File Formats & Deep Per-File Inspection

| File Format | Exhaustive Analysis Capabilities |
| :--- | :--- |
| **`.html`** | All HTML5 tags, semantic landmarks (`<main>`, `<nav>`, `<header>`), forms, media, `<link>` stylesheets, `<script>` module invocations, SPA root mount points (`#root`), responsive viewport meta, ARIA accessibility attributes, and DOM tree construction. |
| **`.css`** | CSS variables / design tokens (`:root`), Flexbox one-dimensional flow, CSS Grid two-dimensional layouts, `@keyframes` motion sequences, responsive `@media` query breakpoints, and UI framework class detection. |
| **`.js` / `.jsx` / `.ts` / `.tsx`** | ES6 module imports/exports, React component hierarchies, React Hooks (`useState`, `useEffect`, `useContext`), state updates, props flow, JSX render trees, and client-side `fetch` / `axios` API calls. |
| **`.py`** | Full Python AST parsing: classes, inheritance, functions, async coroutines, decorators, Pydantic schemas, and web framework route decorators (`@app.get(...)`). |
| **`.rs`** | Rust crates, `use` declarations, structs, enums, traits, `impl` blocks, `tokio` async runtimes, and thread-safe concurrency primitives (`Arc`, `Mutex`). |
| **`.java`** | Package namespaces, class hierarchies, interfaces, methods, and enterprise annotations (`@SpringBootApplication`, `@RestController`, `@Autowired`). |
| **`.go`** | Go packages, structs, interfaces, methods, receiver functions, CSP concurrency (`go` routines, `chan` channels), and HTTP handlers. |
| **`Dockerfile`** | Multi-stage build pipelines, base images (`FROM`), layer caching (`COPY`, `RUN`), port exposures (`EXPOSE`), entrypoints (`ENTRYPOINT`, `CMD`), and container security best practices. |
| **`.sh`** | Shebang interpreters, strict safety flags (`set -euo pipefail`), functions, environment variable exports, CLI tool invocations, and command pipelines. |

---

### 3. Cross-File Interconnection Graph (HOW & WHY It Works)
Explainer maps every relationship between files across the codebase and answers two critical questions for every connection:
- **HOW it works**: The syntactic mechanism (e.g. `<link rel="stylesheet">`, ES module import, Docker `COPY`, API route binding).
- **WHY it works**: The architectural rationale (e.g. separation of presentation from content, reusable component composition, container environment isolation).

---

### 4. Multi-Channel Output System
1. 🖥️ **Interactive Terminal UI**: High-fidelity formatted tables, architecture overview cards, and color-coded status badges via `rich`.
2. 📝 **Comprehensive Markdown Report (`EXPLAINER_REPORT.md`)**: Complete technical dossier with embedded Mermaid dependency graphs.
3. 🌐 **Interactive Web Dashboard (`explainer_dashboard.html`)**: Self-contained, responsive single-page web application with interactive draggable network graphs, live search, and file detail drawers.

---

## 🚀 Installation & Quick Start

### Prerequisites
- Python 3.9+
- (Optional for AI mode): Ollama or local LLM server

### Clone & Install
```bash
git clone https://github.com/ayushpalg46/Explainer.git
cd Explainer
pip install -e .
```

### Run Explainer

#### 1. Interactive Wizard
Simply run:
```bash
explainer
# or
python -m explainer.cli
```
The interactive wizard will guide you through choosing:
1. Target codebase path
2. Engine mode (Pure Knowledge AST Engine vs Local AI Model)
3. Output format (Terminal, Markdown, HTML Dashboard, or All)

#### 2. Direct CLI Commands
```bash
# Scan a codebase using deterministic Zero-AI mode and generate all reports
explainer scan ./samples --mode static --format all

# Inspect an individual file in deep detail
explainer scan ./samples --inspect app.jsx

# Connect to local Ollama model
explainer scan ./samples --mode ai --ai-provider ollama --ai-model qwen35-uncensored:latest

# Run automated tests
pytest tests/ -v
```

---

## 📂 Project Structure

```
Explainer/
├── explainer/
│   ├── cli.py                     # CLI entrypoint & interactive wizard
│   ├── models.py                  # Pydantic data schemas
│   ├── scanner/                   # Workspace scanner & tech stack detector
│   ├── parsers/                   # Multi-language AST & token parsers
│   │   ├── html_parser.py         # HTML semantic tag & accessibility parser
│   │   ├── css_parser.py          # CSS design tokens, Flexbox & Grid parser
│   │   ├── js_ts_parser.py        # JavaScript / TypeScript / React parser
│   │   ├── python_parser.py       # Python AST & framework parser
│   │   ├── rust_parser.py         # Rust struct, trait & concurrency parser
│   │   ├── java_parser.py         # Java class, interface & Spring parser
│   │   ├── go_parser.py           # Go struct, interface & goroutine parser
│   │   ├── docker_parser.py       # Dockerfile multi-stage & security parser
│   │   ├── shell_parser.py        # Shell script pipeline & flag parser
│   │   └── generic_parser.py      # Config, JSON, YAML, SQL parser
│   ├── graph/                     # Cross-file dependency & interconnection builder
│   ├── engine/                    # Dual analysis engines (Rule/AST + Local AI)
│   ├── knowledge/                 # Pedagogical technical catalog & rulebook
│   └── renderers/                 # Terminal, Markdown & HTML Dashboard generators
├── samples/                       # Demonstration multi-language test codebase
├── tests/                         # Comprehensive unit & integration tests
├── pyproject.toml                 # Package configuration
└── setup.py                       # Packaging script
```

---

## 📄 License
MIT License. Free for open-source and commercial use.
