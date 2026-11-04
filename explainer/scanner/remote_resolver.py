import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional
import requests


class RemoteResolver:
    """
    Resolves remote Git repositories (GitHub/GitLab) and remote raw file URLs
    into local sandbox paths for instant analysis by CodeExplainer.
    """

    CACHE_DIR = Path.home() / ".cache" / "explainer" / "remote"

    @classmethod
    def is_remote_url(cls, target: str) -> bool:
        """Returns True if the target string is an HTTP/HTTPS remote URL."""
        if not target or not isinstance(target, str):
            return False
        clean = target.strip().lower()
        return clean.startswith("http://") or clean.startswith("https://")

    @classmethod
    def resolve(cls, url: str) -> Tuple[Path, bool, str]:
        """
        Resolves a remote URL into a local filesystem path.
        Returns: (local_path, is_single_file, display_label)
        """
        clean_url = url.strip()
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Single GitHub blob file URL:
        # e.g. https://github.com/pallets/flask/blob/main/src/flask/app.py
        github_blob_pattern = r"^https?://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$"
        m_blob = re.match(github_blob_pattern, clean_url, re.IGNORECASE)
        if m_blob:
            user, repo, branch, file_path = m_blob.groups()
            raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
            local_file = cls._download_raw_file(raw_url, Path(file_path).name)
            return local_file, True, f"{user}/{repo}:{file_path}"

        # 2. Raw file URL:
        # e.g. https://raw.githubusercontent.com/... or any direct file URL
        if "raw.githubusercontent.com" in clean_url or any(clean_url.endswith(ext) for ext in [
            ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".sql", ".conf", ".rs", ".go", ".java", ".sh"
        ]):
            file_name = clean_url.split("?")[0].rstrip("/").split("/")[-1] or "downloaded_file.txt"
            local_file = cls._download_raw_file(clean_url, file_name)
            return local_file, True, file_name

        # 3. Full Git Repository URL:
        # e.g. https://github.com/user/repo or https://github.com/user/repo.git
        repo_name = clean_url.rstrip("/").split("/")[-1].replace(".git", "")
        repo_cache_path = cls.CACHE_DIR / repo_name

        # If already cached, update with git pull or re-clone
        if (repo_cache_path / ".git").exists():
            try:
                subprocess.run(
                    ["git", "pull", "--depth", "1"],
                    cwd=str(repo_cache_path),
                    capture_output=True,
                    text=True,
                    timeout=20,
                    check=False
                )
            except Exception:
                pass
            return repo_cache_path, False, repo_name

        # Shallow clone to save bandwidth and disk space
        try:
            if repo_cache_path.exists():
                shutil.rmtree(repo_cache_path, ignore_errors=True)

            res = subprocess.run(
                ["git", "clone", "--depth", "1", clean_url, str(repo_cache_path)],
                capture_output=True,
                text=True,
                timeout=60,
                check=False
            )
            if res.returncode == 0 and repo_cache_path.exists():
                return repo_cache_path, False, repo_name
            else:
                err_msg = res.stderr.strip() or res.stdout.strip() or "Git clone failed"
                raise RuntimeError(f"Could not clone repository '{clean_url}': {err_msg}")
        except FileNotFoundError:
            raise RuntimeError("Git is required to clone remote repositories. Please install Git and try again.")

    @classmethod
    def _download_raw_file(cls, url: str, filename: str) -> Path:
        """Downloads a single raw file into the cache directory."""
        temp_dir = cls.CACHE_DIR / "files"
        temp_dir.mkdir(parents=True, exist_ok=True)
        dest_path = temp_dir / filename

        res = requests.get(url, timeout=30)
        if res.status_code != 200:
            raise RuntimeError(f"Failed to download remote file (HTTP {res.status_code}) from {url}")

        dest_path.write_bytes(res.content)
        return dest_path
