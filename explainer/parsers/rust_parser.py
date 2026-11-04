import re
from typing import List, Dict
from .base import BaseParser
from ..models import FileAnalysis, ElementExplanation


class RustParser(BaseParser):
    """
    Parses Rust source files line-by-line, extracting use declarations,
    structs, enums, traits, and functions with word-by-word breakdowns,
    4-year-old beginner analogies, and cross-file crate connections.
    """

    def __init__(self):
        super().__init__(language="Rust")

    def parse(self, file_path: str, content: str, relative_path: str) -> FileAnalysis:
        analysis = self.create_base_analysis(file_path, content, relative_path)
        lines = content.splitlines()

        analysis.beginner_story = (
            "Think of a Rust file like an ultra-safe high-tech suit of armor! "
            "Rust has a very strict teacher called the Borrow Checker. Before your program is allowed to run, "
            "the teacher double-checks every single toy and tool so nobody drops anything, loses memory, or crashes. "
            "Once approved, your program runs with lightning speed like a supersonic jet!"
        )

        # Uses: use crate::... or use std::...
        uses = re.findall(r'use\s+([^;]+);', content)
        for u in uses:
            analysis.raw_imports.append(u.strip())

        # Modules: mod foo;
        mods = re.findall(r'mod\s+([a-zA-Z0-9_]+)\s*;', content)
        for m in mods:
            analysis.raw_imports.append(f"mod::{m}")

        for idx, line in enumerate(lines, 1):
            clean = line.strip()
            if not clean or clean.startswith("//"):
                continue

            # use declaration
            if clean.startswith("use ") and clean.endswith(";"):
                target = clean[4:-1].strip()
                words_breakdown = {
                    "use": "Rust keyword bringing external modules or types into current scope.",
                    target: f"Path of the module, trait, or type being imported."
                }
                analysis.elements.append(ElementExplanation(
                    name=f"use {target}",
                    kind="import",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Rust import bringing `{target}` into scope.",
                    how_it_is_used=f"Imports `{target}` at line {idx} for local access without full path prefix.",
                    where_it_is_used=f"Import block at line {idx}.",
                    why_it_works="The Rust compiler resolves symbol paths at compile time.",
                    best_practices_and_pitfalls="Group imports logically (std, third-party crates, local crate).",
                    simple_analogy=f"Think of use like keeping your favorite book on your desk instead of walking to the library shelf every time!",
                    what_happens_on_screen=f"Makes `{target}` available to functions in this file.",
                    what_if_removed="Code using these types will fail to compile unless fully qualified.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Dependency link to `{target}`."
                ))

            # Struct
            struct_m = re.match(r'(?:pub\s+)?struct\s+([a-zA-Z0-9_]+)', clean)
            if struct_m:
                s_name = struct_m.group(1)
                words_breakdown = {
                    "struct": "Rust keyword declaring a typed data structure.",
                    s_name: f"The identifier name of this custom data type."
                }
                if "pub" in clean:
                    words_breakdown["pub"] = "Makes this struct public and visible outside this module."

                analysis.elements.append(ElementExplanation(
                    name=f"struct {s_name}",
                    kind="struct",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Rust data structure `{s_name}` defining memory layout and fields.",
                    how_it_is_used=f"Provides type-safe modeling for `{s_name}` state.",
                    where_it_is_used=f"Type definition at line {idx}.",
                    why_it_works="Rust guarantees memory safety without GC via compile-time ownership and borrowing rules.",
                    best_practices_and_pitfalls="Derive common traits: `#[derive(Debug, Clone, PartialEq)]`.",
                    simple_analogy=f"Think of struct '{s_name}' like a custom blueprint for a Lego spaceship!",
                    what_happens_on_screen=f"Defines the layout of `{s_name}` in memory.",
                    what_if_removed=f"Any code instantiating or referencing `{s_name}` will fail to compile.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Core domain entity passed across functions and crates."
                ))

            # Function
            fn_m = re.match(r'(?:pub\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*\((.*?)\)', clean)
            if fn_m:
                f_name = fn_m.group(1)
                params = fn_m.group(2)
                words_breakdown = {
                    "fn": "Rust keyword declaring a function.",
                    f_name: f"Identifier name of the function.",
                    "()": "Argument list."
                }
                if "pub" in clean:
                    words_breakdown["pub"] = "Makes the function publicly accessible outside this module."
                if "async" in clean:
                    words_breakdown["async"] = "Returns a Future executed by an asynchronous executor (like Tokio)."

                analysis.elements.append(ElementExplanation(
                    name=f"fn {f_name}()",
                    kind="function",
                    line_number=idx,
                    snippet=clean,
                    what_it_is=f"Rust function `{f_name}` implementing typed logic.",
                    how_it_is_used=f"Executes operations according to Rust's ownership rules.",
                    where_it_is_used=f"Function declaration at line {idx}.",
                    why_it_works="Compiled down to native machine code with zero-cost abstractions via LLVM.",
                    best_practices_and_pitfalls="Return `Result<T, E>` for recoverable errors rather than panicking.",
                    simple_analogy=f"Think of function '{f_name}' like a reliable kitchen blender: press the button and it blends perfectly every time!",
                    what_happens_on_screen=f"Executes `{f_name}` logic when called.",
                    what_if_removed=f"Callers invoking `{f_name}` will fail to compile.",
                    words_breakdown=words_breakdown,
                    interconnection_note=f"Callable within this module or across crates if public."
                ))

        structs = re.findall(r'(?:pub\s+)?struct\s+([a-zA-Z0-9_]+)', content)
        enums = re.findall(r'(?:pub\s+)?enum\s+([a-zA-Z0-9_]+)', content)
        traits = re.findall(r'(?:pub\s+)?trait\s+([a-zA-Z0-9_]+)', content)
        functions = re.findall(r'(?:pub\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)', content)

        detected_concepts = []
        if structs:
            detected_concepts.append(f"Data Structures ({', '.join(structs[:3])})")
        if enums:
            detected_concepts.append(f"Algebraic Data Types / Enums ({', '.join(enums[:3])})")
        if traits:
            detected_concepts.append(f"Trait Abstractions ({', '.join(traits[:3])})")
        if "Result<" in content or "Option<" in content or "?" in content:
            detected_concepts.append("Rust Zero-Cost Error Handling (Result / Option / ?)")
        if "tokio" in content or "async fn" in content:
            detected_concepts.append("Async Tokio Runtime & Concurrency")

        analysis.concepts_detected = detected_concepts
        analysis.role_in_codebase = "Rust Systems Service / High-Performance Core Engine"
        analysis.summary = (
            f"Rust module declaring {len(structs)} struct(s), {len(enums)} enum(s), {len(traits)} trait(s), "
            f"and {len(functions)} function(s). Uses {len(analysis.raw_imports)} crate/module imports."
        )
        return analysis
