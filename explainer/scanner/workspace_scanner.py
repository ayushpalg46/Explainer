import os
from pathlib import Path
from typing import List, Tuple

IGNORE_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "__pycache__", ".venv", "venv", "env",
    "target", "dist", "build", ".next", ".nuxt", ".cache", ".idea", ".vscode",
    "coverage", ".pytest_cache", ".gemini", "explainer_output"
}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".mp4", ".mp3",
    ".zip", ".tar", ".gz", ".7z", ".pdf", ".lock", ".pyc", ".pyd", ".dll",
    ".exe", ".so", ".dylib", ".wasm", ".bin", ".gguf"
}


class WorkspaceScanner:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).resolve()

    def scan(self) -> List[Tuple[Path, str]]:
        """Return list of (absolute_path, relative_path) for all valid source files."""
        if self.root.is_file():
            return [(self.root, self.root.name)]

        valid_files = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            # Prune ignored directories in-place
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix.lower() in IGNORE_EXTENSIONS:
                    continue
                if fname.startswith(".") and fname not in (".env.example", ".dockerignore"):
                    continue

                try:
                    rel_path = fpath.relative_to(self.root).as_posix()
                    valid_files.append((fpath, rel_path))
                except ValueError:
                    continue

        return sorted(valid_files, key=lambda x: x[1])
