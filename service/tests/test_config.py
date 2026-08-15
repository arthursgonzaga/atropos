import pytest
from pydantic import ValidationError
from config import get_settings


def test_settings_load_from_env():
    s = get_settings()
    assert s.octoprint_url == "http://octoprint.local"
    assert s.octoprint_api_key == "test-api-key"
    assert s.synapse_url == "http://synapse.local"
    assert s.telegram_chat_id == "123456789"


def test_settings_raises_when_env_missing(monkeypatch):
    monkeypatch.delenv("OCTOPRINT_URL", raising=False)
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()
    get_settings.cache_clear()
