import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation
from ..knowledge.catalog import SHELL_KNOWLEDGE


class ShellParser(BaseParser):
    """
    Parses Shell scripts (.sh, .bash, .zsh) line-by-line, explaining
    shebangs, strict safety flags, function definitions, sourced files,
    command invocations, loops, and pipeline operations with word-by-word
    breakdowns, 4-year-old beginner analogies, and cross-file connections.
    """

    KNOWN_COMMANDS = {
        "echo": ("Print Text", "Prints messages or variables to the terminal screen.", "Think of echo like speaking into a megaphone so everyone in the room hears your message!"),
        "cd": ("Change Directory", "Changes the working folder path.", "Think of cd like walking through a doorway into another room in your house!"),
        "mkdir": ("Make Directory", "Creates new folders on your computer.", "Think of mkdir like building a brand new toy box to put your toys inside!"),
        "rm": ("Remove Files", "Deletes files or directories.", "Think of rm like using an eraser to clean your drawing board!"),
        "cp": ("Copy File", "Duplicates files or folders.", "Think of cp like using a magic photocopy machine to make a twin of your drawing!"),
        "mv": ("Move / Rename", "Moves or renames files or directories.", "Think of mv like sliding your book from your backpack onto your desk!"),
        "curl": ("Network Request", "Downloads files or queries web URLs from the internet.", "Think of curl like sending a friendly carrier pigeon to fetch a secret letter from across the ocean!"),
        "docker": ("Container Engine", "Builds or runs virtual application containers.", "Think of docker like a magical lunchbox that keeps your food fresh and separate from everything else!"),
        "python": ("Python Interpreter", "Executes Python programming script files.", "Think of python like a helpful robot butler that reads Python recipe books and follows them step-by-step!"),
        "pytest": ("Test Suite", "Executes automated tests to verify code correctness.", "Think of pytest like a teacher checking homework with a red checkmark!"),
        "npm": ("Node Package Manager", "Installs JavaScript dependencies and runs scripts.", "Think of npm like a giant toy store where you pick and download cool blocks for your project!"),
        "pip": ("Python Package Installer", "Installs Python packages from PyPI.", "Think of pip like ordering new Lego brick packs for your Python robot!"),
        "export": ("Environment Export", "Sets environment variables for child processes.", "Think of export like writing a rule on a giant sticky note that all your helpers can read!"),
        "source": ("Source Script", "Executes another script inside the current shell.", "Think of source like borrowing your friend's pencil case and using their pens right now!"),
    }

    def __init__(self):
        super().__init__(language="Shell Script")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        analysis.beginner_story = (
            "Think of a Shell script like a checklist for a friendly robot helper! "
            "Instead of you clicking buttons, opening terminals, and typing 20 commands one by one, "
            "you hand this checklist to the computer. The computer reads line 1, finishes it, then reads "
            "line 2, and automatically sets up, tests, or launches your whole project in seconds!"
        )

        shebang = lines[0] if lines and lines[0].startswith("#!") else None
        has_strict_mode = bool(re.search(r'set\s+-[a-zA-Z]*e|set\s+-o\s+pipefail', content))
        functions = re.findall(r'(?:function\s+)?([a-zA-Z0-9_\-]+)\s*\(\s*\)\s*\{', content)
        sourced_files = re.findall(r'(?:source|\.)\s+([^\s;]+)', content)
        for s in sourced_files:
            if not s.startswith("-"):
                analysis.raw_imports.append(s)

        common_cmds = list(self.KNOWN_COMMANDS.keys()) + ["docker-compose", "yarn", "pnpm", "git", "cargo", "go", "mvn", "gradle"]
        invoked_tools = []
        for tool in common_cmds:
            if re.search(rf'\b{tool}\b', content):
                invoked_tools.append(tool)

        has_pipes = "|" in content
        has_loops = bool(re.search(r'\bfor\s+|\bwhile\s+', content))

        detected_concepts = []
        if shebang:
            detected_concepts.append(f"Interpreter Shebang (`{shebang.strip()}`)")
            kb = SHELL_KNOWLEDGE.get("shebang", {})
            words_breakdown = {
                "#": "Hash character, starts comments in shell.",
                "!": "Exclamation mark ('bang'), together with '#' forms the magical 2-byte shebang sequence.",
            }
            parts = shebang.strip()[2:].split()
            if parts:
                words_breakdown[parts[0]] = "Interpreter executable path invoked by OS kernel."
                for p in parts[1:]:
                    words_breakdown[p] = f"Interpreter flag or argument `{p}`."

            analysis.elements.append(ElementExplanation(
                name=f"Shebang: {shebang.strip()}",
                kind="directive",
                line_number=1,
                snippet=shebang.strip(),
                what_it_is=kb.get("what_it_is", "The first line telling the computer which shell program to use."),
                how_it_is_used="Instructs the OS kernel which binary executes this script file.",
                where_it_is_used="First line of the script.",
                why_it_works=kb.get("why_it_works", "The OS kernel reads magic bytes 0x23 0x21 to pick the interpreter."),
                best_practices_and_pitfalls=kb.get("best_practices", "Use `#!/usr/bin/env bash` for maximum portability."),
                simple_analogy=kb.get("simple_analogy", "Like an address label on an envelope telling the mail carrier which language to read!"),
                what_happens_on_screen=kb.get("what_happens_on_screen", "Ensures the script runs with Bash even if clicked or run from another shell."),
                what_if_removed=kb.get("what_if_removed", "The computer might run the script with the wrong program and get confused."),
                words_breakdown=words_breakdown,
                interconnection_note="Ensures all child commands and syntax run in the intended shell interpreter."
            ))

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue

            # Check for strict mode
            if re.match(r'^set\s+', clean):
                kb = SHELL_KNOWLEDGE.get("strict_mode", {})
                words_breakdown = {
                    "set": "Shell builtin command that changes internal shell execution settings.",
                }
                for tok in clean.split()[1:]:
                    words_breakdown[tok] = f"Flag `{tok}` modifying error trapping and parameter expansion rules."

                analysis.elements.append(ElementExplanation(
                    name=f"Safety Flag: {clean}",
                    kind="directive",
                    line_number=idx,
                    snippet=clean,
                    what_it_is="Strict mode safeguard configuring immediate exit on errors or unset variables.",
                    how_it_is_used=f"Configures shell runtime flags at line {idx}.",
                    where_it_is_used=f"Line {idx} error trapping initialization.",
                    why_it_works=kb.get("why_it_works", "Enforces immediate exit on command error (-e) and unset variables (-u)."),
                    best_practices_and_pitfalls=kb.get("best_practices", "Always include strict mode at the top of production shell scripts."),
                    simple_analogy=kb.get("simple_analogy", "Like a safety helmet and seatbelt for your script so nobody gets hurt if a bump happens!"),
                    what_happens_on_screen=kb.get("what_happens_on_screen", "Stops the script immediately if any error happens so broken half-finished files aren't created."),
                    what_if_removed=kb.get("what_if_removed", "The script might keep running even if files are missing, potentially corrupting data."),
                    words_breakdown=words_breakdown,
                    interconnection_note="Protects all subsequent commands from executing if previous steps fail."
                ))

            # Check for functions
            func_m = re.match(r'^(?:function\s+)?([a-zA-Z0-9_\-]+)\s*\(\s*\)\s*\{?', clean)
            if func_m:
                fn_name = func_m.group(1)
                analysis.elements.append(ElementExplanation(
                    name=f"function {fn_name}()",
                    kind="function",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Reusable shell routine `{fn_name}`.",
                    how_it_is_used=f"Defines a modular task callable by typing `{fn_name}` elsewhere in the script.",
                    where_it_is_used=f"Function definition at line {idx}.",
                    why_it_works="Stored in memory by the shell process and executed in the current shell environment.",
                    best_practices_and_pitfalls="Use `local` for variables declared inside functions to avoid polluting global state.",
                    simple_analogy=f"Think of function '{fn_name}' like a custom shortcut button on your game controller that triggers a combo move!",
                    what_happens_on_screen=f"Registers function `{fn_name}` for future execution.",
                    what_if_removed=f"Any line calling `{fn_name}` will fail with `command not found`.",
                    words_breakdown={fn_name: f"Function identifier name.", "()": "Signals to bash that this is a callable function routine."},
                    interconnection_note=f"Can be called by other functions or main execution routines in this script."
                ))

            # Check for source / imports
            src_m = re.match(r'^(?:source|\.)\s+([^\s;]+)', clean)
            if src_m:
                target_script = src_m.group(1)
                analysis.elements.append(ElementExplanation(
                    name=f"source {target_script}",
                    kind="import",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Sources and executes external file `{target_script}` in the current shell.",
                    how_it_is_used=f"Loads variables and helper routines from `{target_script}` at line {idx}.",
                    where_it_is_used=f"Import at line {idx}.",
                    why_it_works="The shell reads the specified file directly into the active execution frame without spawning a subshell.",
                    best_practices_and_pitfalls="Ensure the target file exists before sourcing, or check `[ -f ... ]`.",
                    simple_analogy=f"Think of source like borrowing your friend's coloring kit and bringing it to your desk so you can use all their markers!",
                    what_happens_on_screen=f"Loads environment variables and functions from `{target_script}` into memory.",
                    what_if_removed=f"The script loses access to helper functions and environment settings defined in `{target_script}`.",
                    words_breakdown={"source": "Shell builtin reading commands from a file into current environment.", target_script: "Target script path to load."},
                    interconnection_note=f"Direct dependency link to `{target_script}`."
                ))

            # Check for command invocations
            first_word = clean.split()[0] if clean.split() else ""
            if first_word in self.KNOWN_COMMANDS and not re.match(r'^(set|function)\b', clean):
                cmd_meta = self.KNOWN_COMMANDS[first_word]
                words_breakdown = {first_word: f"Command executable: {cmd_meta[1]}"}
                for tok in clean.split()[1:5]:
                    words_breakdown[tok] = f"Argument or parameter: `{tok}`"

                analysis.elements.append(ElementExplanation(
                    name=f"{first_word}: {clean[:40]}{'...' if len(clean) > 40 else ''}",
                    kind="command",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Command invocation: `{first_word}` ({cmd_meta[0]}).",
                    how_it_is_used=f"Executes `{clean[:50]}` at line {idx}.",
                    where_it_is_used=f"Instruction at line {idx}.",
                    why_it_works=f"The shell forks and execs the binary or executes the internal builtin.",
                    best_practices_and_pitfalls="Quote variables (`\"$VAR\"`) to prevent unexpected word splitting.",
                    simple_analogy=cmd_meta[2],
                    what_happens_on_screen=f"Runs `{first_word}` and prints output or performs file/network operations.",
                    what_if_removed="This specific automation step is skipped.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"May interact with other files or tools ({', '.join(invoked_tools[:3])})."
                ))

        if has_strict_mode:
            detected_concepts.append("Strict Shell Safety Mode (`set -e / pipefail`)")
        if has_pipes:
            detected_concepts.append("Inter-process Pipe Streams (`|`)")
        if functions:
            detected_concepts.append(f"Modular Shell Functions ({', '.join(functions[:3])})")
        if invoked_tools:
            detected_concepts.append(f"Orchestrated External Tooling ({', '.join(invoked_tools)})")

        analysis.concepts_detected = detected_concepts
        analysis.frameworks_detected = [f"CLI / Tooling Automation ({', '.join(invoked_tools)})"] if invoked_tools else ["Unix Shell Environment"]
        analysis.role_in_codebase = "Build, Automation, CI/CD or Deployment Task Runner"
        analysis.summary = (
            f"Shell automation script containing {len(lines)} lines. "
            f"{f'Targets interpreter: `{shebang}`. ' if shebang else ''}"
            f"{'Enforces strict error trapping. ' if has_strict_mode else ''}"
            f"{f'Defines {len(functions)} modular shell routine(s): {', '.join(functions)}. ' if functions else ''}"
            f"{f'Orchestrates command-line tools: {', '.join(invoked_tools)}. ' if invoked_tools else ''}"
            f"Sources {len(sourced_files)} child configuration/script file(s)."
        )
        return analysis
