# 🔍 CodeExplainer - Dual-Engine Codebase & File Explainer

An advanced, pedagogical code intelligence and explanation engine that delivers comprehensive architectural dossiers, tech stack compatibility evaluations, cross-file interconnection graphs, and deep file-by-file breakdowns across 11+ programming languages and frameworks.

Designed with a **Dual-Engine Architecture**:
- ⚡ **Pure Knowledge & AST Engine (Zero-AI Mode)**: 100% deterministic, offline, and instant. Analyzes syntax trees, language grammar, and design patterns, cross-referencing an exhaustive built-in semantic knowledge dictionary to produce elaborated, high-fidelity explanations without needing an AI model.
- 🧠 **Local AI Engine**: Seamlessly connects to local LLMs (Ollama, LM Studio, or local GGUF models) to provide conversational synthesis while anchoring all facts to ground-truth AST data.

---

## 🌟 Key Capabilities

### 1. High-Level Architecture & Tech Stack Ecosystem
- **Architectural Style Classification**: Identifies SPA, Microservices, Decoupled Client-Server, MVC, Systems Engineering, and Cloud Native architectures.
- **Tech Stack Compatibility**: Analyzes language versions, build tools, package managers, and container configurations, explaining how the stack layers collaborate.
- **Subsystem & Directory Mapping**: Classifies directory roles (`components/`, `routes/`, `models/`, `utils/`, `tests/`, etc.).

### 2. Deep File-by-File Explainer (11+ Supported Languages)
For every file in the codebase, CodeExplainer breaks down:
- **Language, Size & Role**: Core function within the repository.
- **Summary & Purpose**: Multi-paragraph executive summary.
- **Concepts & Design Patterns**: Detected patterns (e.g. Hooks, Object-Oriented, Immutability, Reactive Streams, Concurrency).
- **Styling & Motion Details**: Flexbox/Grid layouts, design tokens, keyframe animations, Canvas/WebGL rendering.
- **Exhaustive Element Breakdown**: Every tag, component, hook, class, directive, and function explained across 5 critical dimensions:
  1. **What It Is**: Architectural & technical definition.
  2. **How It's Used**: Syntactic usage and execution context.
  3. **Where It's Used**: Line numbers and file references.
  4. **Why It Works**: Underlying runtime mechanics (e.g. DOM/CSSOM, React Fiber, JVM bytecode, LLVM machine code).
  5. **Best Practices & Pitfalls**: Production recommendations and caveats.

| Language / Format | Covered Constructs & Features |
| :--- | :--- |
| **HTML (`.html`, `.htm`)** | All HTML5 tags (`<main>`, `<header>`, `<nav>`, `<form>`, `<canvas>`, etc.), meta tags, SEO, accessibility hooks (`aria-*`, `role`), SPA anchors (`#root`), asset links. |
| **CSS (`.css`, `.scss`)** | Flexbox, CSS Grid, media query breakpoints, CSS custom properties (variables), `@keyframes` animations, transitions, utility frameworks (Tailwind). |
| **JavaScript / TypeScript (`.js`, `.ts`)** | Imports/exports, module resolution, Promises, async/await, API fetch pipelines, type interfaces. |
| **React (`.jsx`, `.tsx`)** | Components, props, Virtual DOM reconciliation, React Hooks (`useState`, `useEffect`, `useMemo`, `useCallback`, `useRef`, `useContext`, custom hooks). |
| **Python (`.py`)** | AST-parsed classes, inheritance, decorators, functions, type hints, docstrings, frameworks (FastAPI, Flask, Django, Pydantic). |
| **Rust (`.rs`)** | Structs, enums, traits, `impl` blocks, macros, ownership, lifetimes, `Result`/`Option` error handling. |
| **Java (`.java`)** | Classes, interfaces, packages, annotations (`@RestController`, `@Service`, `@Autowired`), Spring Boot patterns. |
| **Go (`.go`)** | Packages, structs, interfaces, methods, goroutines, channels, HTTP handlers. |
| **Docker (`Dockerfile`, `compose.yml`)** | Multi-stage builds, base images (`FROM`), layer caching (`COPY`, `RUN`), ports (`EXPOSE`), volumes, entrypoints. |
| **Shell (`.sh`, `.bash`, `.zsh`)** | Shebangs, safety flags (`set -euo pipefail`), pipes, loops, traps, external CLI orchestration. |

### 3. Cross-File Interconnection Graph (How & Why Files Connect)
Maps all dependencies across your project:
- Resolves relative imports, stylesheet links, script tags, Docker context copies, and shell execution links.
- Explains **HOW** the files communicate technically (e.g. module imports, HTTP endpoints, CSSOM cascade).
- Explains **WHY** the interconnection exists architecturally (e.g. separation of concerns, presentation vs state, environment parity).

---

## 🚀 Quick Start

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/ayushpalg46/Explainer.git
cd Explainer
pip install -r requirements.txt
```

Or install in editable mode:

```bash
pip install -e .
```

---

## 🖥 Usage

### 1. Interactive Workflow with `expl` Command (Recommended)

1. Open **CMD** or **PowerShell** inside any codebase folder:
   ```bash
   cd path/to/your/codebase
   ```
2. Type and run:
   ```bash
   expl
   ```
   *(or `EXPL` / `explainer`)*

3. **Step 1: Choose Mode** (Default: `[1]`):
   ```text
   Choose Explanation Mode:
     [1] Without-AI Explanation (Deterministic Pure AST & Knowledge Engine - 100% Offline & Precise) [Default]
     [2] AI Explanation (Local Ollama / Qwen Model)
   Select mode [1]:
   ```
4. **Step 2: Automatic Multi-File Folder Generation**:
   The tool analyzes all files and creates a dedicated folder named:
   `📁 <Codebase_Folder_Name>-EXPL/`
   Containing:
   * `files/<filename>.md`: **Individual, exhaustive explanation document for each file in the codebase** (tags, symbols, functions, hooks, and how/why connections).
   * `INDEX.md`: Master architecture index, tech stack compatibility, directory roles, and Mermaid dependency graph.
   * `dashboard.html`: Interactive visual web GUI with draggable network graph.
   * `FULL_REPORT.md`: Consolidated single-file dossier.

5. **Step 3: Choose How to View** (Default: `[1]`):
   ```text
   ✔ Work has been done successfully!
   📁 Created Folder: <Codebase_Folder_Name>-EXPL

   How would you like to view the explanation?
     [1] Want To See In Codebase Files Explanation In CLI [Default]
     [2] Want To See In Codebase Files Explanation In Webpage (GUI)
   Choose view format [1]:
   ```
   * **Option 1 (CLI)**: Displays the project overview and an interactive file selector to inspect any file's deep tags and symbols directly in your terminal.
   * **Option 2 (Webpage GUI)**: Automatically launches `dashboard.html` in your default web browser!

---

### 2. Direct Command-Line Execution

#### Run with Pure Static Engine (Zero-AI, Fast & Deterministic):
```bash
python -m explainer.cli analyze ./my-project --mode static --format all
```

#### Run with Local AI Model (Ollama):
```bash
python -m explainer.cli analyze ./my-project --mode ai --ai-provider ollama --ai-model llama3 --format all
```

#### Run with LM Studio or Local OpenAI-Compatible Server:
```bash
python -m explainer.cli analyze ./my-project --mode ai --ai-provider openai_compatible --ai-endpoint http://localhost:1234/v1 --ai-model local-model --format all
```

#### Inspect a Specific File in Terminal:
```bash
python -m explainer.cli analyze ./my-project --inspect src/App.jsx --format terminal
```

---

## 📊 Output Formats

1. **Rich Terminal Interface**:
   - Styled cards, color-coded tables, and formatted pedagogical descriptions directly in your terminal.
2. **Markdown Dossier (`EXPLAINER_REPORT.md`)**:
   - Complete GitHub-flavored Markdown document with Mermaid architecture flowcharts, tables, and section anchors.
3. **Interactive Visual Dashboard (`explainer_dashboard.html`)**:
   - 100% self-contained single-file HTML report.
   - Interactive Network Dependency Graph (zoom, pan, drag, click to highlight inbound/outbound links).
   - Sidebar file tree with live search & filtering.
   - Tabbed inspector for Architecture, Dependency Graph, and granular Element Tables.

---

## 🧪 Running Automated Tests

Run the test suite using Python's standard `unittest`:

```bash
python -m unittest discover tests
```

---

## 📄 License

MIT License. Designed and developed with care.
