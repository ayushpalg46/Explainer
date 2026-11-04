import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from explainer.scanner.remote_resolver import RemoteResolver


class TestRemoteResolver:

    def test_is_remote_url(self):
        assert RemoteResolver.is_remote_url("https://github.com/user/repo") is True
        assert RemoteResolver.is_remote_url("http://gitlab.com/user/repo.git") is True
        assert RemoteResolver.is_remote_url("https://raw.githubusercontent.com/user/repo/main/app.py") is True
        assert RemoteResolver.is_remote_url("samples/server.py") is False
        assert RemoteResolver.is_remote_url("C:\\path\\to\\file.py") is False
        assert RemoteResolver.is_remote_url("") is False
        assert RemoteResolver.is_remote_url(None) is False

    @patch("requests.get")
    def test_github_blob_url_resolution(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"print('hello from github blob')"
        mock_get.return_value = mock_resp

        with patch.object(RemoteResolver, "CACHE_DIR", tmp_path / "cache"):
            url = "https://github.com/pallets/flask/blob/main/src/flask/app.py"
            local_path, is_single, label = RemoteResolver.resolve(url)

            assert is_single is True
            assert "pallets/flask:src/flask/app.py" in label
            assert local_path.exists()
            assert local_path.name == "app.py"
            assert "hello from github blob" in local_path.read_text()
            mock_get.assert_called_once_with(
                "https://raw.githubusercontent.com/pallets/flask/main/src/flask/app.py",
                timeout=30
            )

    @patch("requests.get")
    def test_raw_file_url_resolution(self, mock_get, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"def hello(): pass"
        mock_get.return_value = mock_resp

        with patch.object(RemoteResolver, "CACHE_DIR", tmp_path / "cache"):
            url = "https://example.com/scripts/worker.py"
            local_path, is_single, label = RemoteResolver.resolve(url)

            assert is_single is True
            assert label == "worker.py"
            assert local_path.exists()
            assert local_path.name == "worker.py"
            assert "def hello(): pass" in local_path.read_text()

    @patch("subprocess.run")
    def test_git_repo_clone_resolution(self, mock_subproc, tmp_path):
        cache_base = tmp_path / "cache"
        repo_dir = cache_base / "my-repo"

        def fake_clone(cmd, **kwargs):
            repo_dir.mkdir(parents=True, exist_ok=True)
            (repo_dir / ".git").mkdir()
            (repo_dir / "main.py").write_text("print('repo')")
            res = MagicMock()
            res.returncode = 0
            return res

        mock_subproc.side_effect = fake_clone

        with patch.object(RemoteResolver, "CACHE_DIR", cache_base):
            url = "https://github.com/user/my-repo.git"
            local_path, is_single, label = RemoteResolver.resolve(url)

            assert is_single is False
            assert label == "my-repo"
            assert local_path.exists()
            assert (local_path / "main.py").exists()
