import json
import pytest
from unittest.mock import patch, MagicMock
from explainer.engine.cloud_providers import CloudAIProvider


class TestCloudAIProvider:

    def test_supported_providers_config(self):
        providers = CloudAIProvider.SUPPORTED_PROVIDERS
        assert "groq" in providers
        assert "gemini" in providers
        assert "openai" in providers
        assert "openrouter" in providers
        assert providers["groq"]["default_model"] == "llama-3.3-70b-versatile"
        assert providers["gemini"]["default_model"] == "gemini-2.0-flash"

    def test_unsupported_provider_raises(self):
        with pytest.raises(ValueError):
            CloudAIProvider(provider="unknown_provider")

    def test_api_key_resolution_env(self, monkeypatch):
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key_12345")
        provider = CloudAIProvider(provider="groq")
        assert provider.api_key == "gsk_test_key_12345"

    def test_missing_api_key_message(self, monkeypatch):
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        with patch.object(CloudAIProvider, "CONFIG_FILE", MagicMock(exists=lambda: False)):
            provider = CloudAIProvider(provider="groq")
            provider.api_key = None
            msg = provider.stream_prompt("hello", "system")
            assert "Missing API key" in msg
            assert "GROQ_API_KEY" in msg

    @patch("requests.post")
    def test_openai_compatible_streaming(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            b'data: {"choices":[{"delta":{"content":" world"}}]}',
            b'data: [DONE]'
        ]
        mock_post.return_value = mock_resp

        provider = CloudAIProvider(provider="groq", api_key="test_key")
        received = []
        result = provider.stream_prompt(
            prompt="Hello?",
            system_prompt="You are a teacher",
            stream_callback=lambda tok: received.append(tok)
        )

        assert result == "Hello world"
        assert "".join(received) == "Hello world"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["model"] == "llama-3.3-70b-versatile"
        assert kwargs["stream"] is True

    @patch("requests.post")
    def test_gemini_streaming(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.iter_lines.return_value = [
            b'data: {"candidates":[{"content":{"parts":[{"text":"Gemini"}]}}]}',
            b'data: {"candidates":[{"content":{"parts":[{"text":" response"}]}}]}'
        ]
        mock_post.return_value = mock_resp

        provider = CloudAIProvider(provider="gemini", api_key="test_gemini_key")
        received = []
        result = provider.stream_prompt(
            prompt="Hello Gemini",
            system_prompt="You are a teacher",
            stream_callback=lambda tok: received.append(tok)
        )

        assert result == "Gemini response"
        assert "".join(received) == "Gemini response"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "gemini-2.0-flash:streamGenerateContent" in args[0]
