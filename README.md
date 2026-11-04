# 🔍 CodeExplainer (`expl`)

> **Deep Codebase & Per-File Architecture Intelligence Engine**  
> *Explaining code line-by-line and word-by-word for beginners and 4-year-olds with real-world analogies.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Tests: 19 Passed](https://img.shields.io/badge/Tests-19%20Passed-success.svg)](tests/)

---

## 🌟 What is CodeExplainer?

**CodeExplainer** is a developer tool and learning engine that breaks down any software codebase into plain, beginner-friendly explanations. Whether you are an absolute beginner who has never touched code or a developer trying to understand a massive unfamiliar project, CodeExplainer reads every single file in your repository and explains what is written **line-by-line, word-by-word, and tag-by-tag**.

It operates under the persona of a **World-Class Senior Developer & Master System Architect** who translates complex software concepts into fun, vivid real-world analogies (toys, Lego blocks, kitchen blenders, doorbell buttons, and helpful robot assistants).

---

## ⚡ Dual-Engine Parity

CodeExplainer offers two distinct execution engines that produce the **exact same standardized line-by-line format**:

1. **Option 1: Without-AI Explanation (Deterministic Pure AST & Knowledge Engine - 100% Offline & Precise) [Default]**
   - ⚡ **Zero-Latency & Instant**: Runs 100% locally and offline without needing an internet connection, GPU, or AI model.
   - 🎯 **AST Grammar & Semantic Catalog**: Extracts exact code lines, attributes, properties, functions, and cross-file dependencies with mathematical precision.
   - 🧸 **Deep Pedagogical Catalog**: Powered by an extensive semantic dictionary containing 4-year-old analogies, screen outcomes, and failure consequences.

2. **Option 2: Local AI Explanation (Local Ollama / Qwen2.5-Coder Model)**
   - 🧠 **Authentic Neural Intelligence**: Auto-detects and connects to your local Ollama models (e.g. `Qwen2.5-Coder-7B` or `Qwen3.5`).
   - 🎓 **Senior Developer (ELI4) Prompt**: Instructed to analyze every file line-by-line and word-by-word using the exact standardized template.
   - 🛡️ **Zero Cloud Dependency**: Runs entirely on your local machine with full data privacy.

---

## 📖 The Standard Output Format

Every single file in your codebase receives an explanation structured in this exact standard template:

```markdown
#### 🧸 1. The Big Picture Story (What is this code?)

│ "Imagine this code is a real physical toy box sitting on a stage. It puts down an empty box on the floor (<div>), paints a big sign above it that says 'My Toy Box' (<h1>), and puts a shiny red doorbell button on the front (<button>). Then it calls the painter (style.css) to paint it with colors, and hires an invisible robot assistant (app.js) to open the box whenever someone presses the doorbell!"
──────
#### 🔍 2. Line-by-Line & Word-by-Word Breakdown

#### Line 1: <div id="root" class="container">

• What is written?: A <div> tag with 2 label(s): id="root" and class="container".
• What does every word mean?:
    • div: Short for "division". An invisible cardboard box used to bundle things together.
    • id="root": A unique name-tag (like a personal ID card). There is only one "root" box in the whole world.
    • class="container": A style group label / costume label. It tells CSS: "Treat this like a container box."
• 🧸 4-Year-Old Analogy: Think of this like setting down an empty laundry basket before you put clothes in it.
• 🖥️ What happens on screen?: Nothing visible yet! It creates an invisible box on a new line where child elements will sit.
• 🔗 Interconnection with other files:
    • app.js searches for this exact box using document.getElementById('root') to place the app inside it.
    • style.css uses .container to apply styling and layout rules.
• 💥 What breaks if deleted?: The title and button lose their container, spill across the screen, and the JavaScript code crashes because it cannot find "root".
──────
#### Line 2: <h1 class="title">My Toy Box</h1>

• What is written?: An <h1> heading with the text "My Toy Box".
• What does every word mean?:
    • h1: "Heading 1" — the biggest, most important title on the page.
    • class="title": A style group label / costume label. It tells CSS: "Treat this like a title box."
    • "My Toy Box": The actual words displayed to the user.
• 🧸 4-Year-Old Analogy: Like the big colorful title on the front cover of a storybook.
• 🖥️ What happens on screen?: Big, bold text appears on the screen reading: My Toy Box.
• 💥 What breaks if deleted?: Visitors won't see any title and won't know what this page is for.
──────
#### Line 3: <button class="btn-magic" onclick="openBox()">Open Box!</button>

• What is written?: A clickable button that runs openBox().
• What does every word mean?:
    • button: An interactive push-button.
    • class="btn-magic": A style group label / costume label. It tells CSS: "Treat this like a btn-magic box."
    • onclick="openBox()": An "ear" listening for clicks. The moment a finger or mouse clicks this button, it shouts: "Robot, run the openBox recipe now!"
    • "Open Box!": The actual words displayed to the user.
• 🧸 4-Year-Old Analogy: Like a doorbell on a front door. When you push it, the bell rings inside the house!
• 🖥️ What happens on screen?: Renders a clickable rectangular button that sinks slightly when clicked.
• 🔗 Interconnection with other files:
    • Directly triggers the openBox() function written inside connected JavaScript files.
• 💥 What breaks if deleted?: Users have no way to open the box or trigger the action.
──────
#### Line 5: <link rel="stylesheet" href="style.css">

• What is written?: A link tag importing style.css.
• What does every word mean?:
    • link: Connects an outside file to this HTML page.
    • rel="stylesheet": Tells the browser: "This outside file contains stylesheet rules."
    • href="style.css": The address of the linked resource: "style.css".
• 🧸 4-Year-Old Analogy: Like calling the painter: "Please bring your paint cans and dress up my toy box!"
• 🖥️ What happens on screen?: The plain black-and-white page transforms into beautiful colors, fonts, and shadows.
• 🔗 Interconnection with other files:
    • Pulls all design rules, colors, and fonts from style.css.
• 💥 What breaks if deleted?: All colors, fonts, centering, and button designs vanish, leaving bare, ugly text.
──────
#### Line 6: <script src="app.js"></script>

• What is written?: A script tag loading the JavaScript code from app.js.
• What does every word mean?:
    • script: Tells the browser: "Here is a book of code instructions."
    • src="app.js": The file path where the brain code lives: "app.js".
• 🧸 4-Year-Old Analogy: Like inserting the batteries and brain chip into a toy robot so it can move and talk!
• 🖥️ What happens on screen?: Invisible on screen, but gives the page life so clicks actually do things.
• 🔗 Interconnection with other files:
    • Directly loads and executes the JavaScript code inside app.js.
• 💥 What breaks if deleted?: The page is frozen like a statue. Clicking the button does absolutely nothing.
──────
```

---

## 🛠️ Supported Languages & Manifests

CodeExplainer extracts exact code lines and builds word-by-word dictionaries across all major development stacks:

| Language / Filetype | What Gets Explained Line-by-Line |
| :--- | :--- |
| **HTML (`.html`, `.htm`)** | Tags (`<html>`, `<head>`, `<body>`, `<div>`, `<span>`, `<h1>-<h6>`, `<button>`, `<canvas>`, `<a>`, `<img>`), attributes (`id`, `class`, `src`, `href`, `rel`, `onclick`), inner text. |
| **CSS (`.css`, `.scss`)** | Selectors (`.class`, `#id`, `:root`, `element`), properties (`display: flex`, `grid`, `background`, `padding`, `margin`, `border-radius`, custom `--variables`), `@keyframes` animations, `@media` queries. |
| **JavaScript / TypeScript / React (`.js`, `.jsx`, `.ts`, `.tsx`)** | ES module imports/exports, components, JSX tags, React hooks (`useState`, `useEffect`), event handlers (`onClick`), functions, async/await flows. |
| **Python (`.py`)** | Imports, classes, `@dataclass`, functions, parameters, return types, main execution guards (`if __name__ == '__main__':`). |
| **Go (`.go`)** | Package clauses, imports, composite structs, interfaces, methods, functions, goroutines (`go ...`), channels (`chan`). |
| **Rust (`.rs`)** | `use` declarations, modules, structs, enums, traits, functions, ownership/borrowing mechanics, Tokio async tasks. |
| **Java (`.java`)** | Package namespaces, imports, annotations (`@SpringBootApplication`, `@Service`, `@RestController`), classes, methods. |
| **Dockerfile & Docker Compose** | Build directives (`FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, `CMD`, `ENTRYPOINT`), microservice definitions, ports, volumes, environment links. |
| **Shell Scripts (`.sh`, `.bash`, `.zsh`)** | Shebang lines (`#!/usr/bin/env bash`), strict safety flags (`set -euo pipefail`), sourced scripts, functions, CLI tools (`docker`, `python`, `npm`, `curl`, `mkdir`). |
| **Manifests & Config (`package.json`, `requirements.txt`, `.env`)** | npm scripts, production & dev dependencies, pinned Python libraries, environment secrets, YAML/TOML settings, Markdown headers. |

---

## 🚀 Quick Start

### Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/ayushpalg46/Explainer.git
cd Explainer
pip install -e .
```

This registers the global CLI command `expl` in your PATH.

---

## 🖥 How to Use It

### The Interactive CLI (`expl`)

1. Open **CMD** or **PowerShell** and navigate to your codebase directory:
   ```bash
   cd D:\my-awesome-project
   ```

2. Run the command:
   ```bash
   expl
   ```

3. **Step 1: Choose Explanation Mode** (Default: `[1]`):
   ```text
   Choose Explanation Mode:
     [1] Without-AI Explanation (Deterministic Pure AST & Knowledge Engine - 100% Offline & Precise) [Default]
     [2] AI Explanation (Local Ollama / Qwen Model)
   Select mode [1]:
   ```
   - Press **Enter** to run in instant, zero-latency Without-AI mode.
   - Or press **2** to select from your installed local Ollama models (with an option `[4] ↩ GO BACK` to return to the menu).

4. **Step 2: Existing Folder Handling (Safe & Clean Updates)**:
   If `<Codebase>-EXPL` already exists from a previous run, the tool prompts you:
   ```text
   Folder 'my-awesome-project-EXPL' already exists! Choose an action:
     [1] Update & refresh existing folder (Default / Clean update)
     [2] Create a new timestamped folder (Keep both)
   Select option [1]:
   ```
   - **Option 1**: Cleans any deleted files and refreshes the dossier in-place.
   - **Option 2**: Preserves your existing folder and creates a timestamped archive (e.g. `my-awesome-project-EXPL_20261104_120000`).

5. **Step 3: Dedicated Multi-File Output Generation**:
   The tool analyzes the codebase and generates:
   ```text
   📁 <Codebase_Name>-EXPL/
   ├── 📁 files/
   │   ├── index.html.md    <-- Dedicated line-by-line breakdown of index.html
   │   ├── style.css.md     <-- Dedicated line-by-line breakdown of style.css
   │   ├── app.jsx.md       <-- Dedicated line-by-line breakdown of app.jsx
   │   ├── server.py.md     <-- Dedicated line-by-line breakdown of server.py
   │   └── Dockerfile.md    <-- Dedicated line-by-line breakdown of Dockerfile
   ├── INDEX.md             <-- Architecture summary & file catalog with links
   └── FULL_REPORT.md       <-- Consolidated comprehensive dossier
   ```

6. **Step 4: Interactive CLI File Inspector**:
   The tool immediately opens the rich terminal interface:
   - Displays project architecture cards, tech stack compatibility, and cross-file links.
   - Launches an interactive terminal menu where you can type any file number to deeply inspect its lines, word-by-word dictionaries, 4-year-old analogies, and failure consequences right in your terminal (or press `q` to exit).

---

## 💻 CLI Flags (Non-Interactive / Scripting Mode)

You can also run CodeExplainer via direct command-line flags:

```bash
# Run Without-AI analysis and generate markdown and terminal output
python -m explainer.cli analyze ./my-project --mode static --format all

# Run with Local AI (Ollama)
python -m explainer.cli analyze ./my-project --mode ai --ai-model qwen2.5-coder:7b --format all

# Inspect a single file directly in terminal
python -m explainer.cli analyze ./my-project --inspect index.html --format terminal
```

---

## 🧪 Running Automated Tests

Run the full automated test suite (19 unit & integration tests):

```bash
pytest tests/ -v
```

All 19 tests pass in under 1 second.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
