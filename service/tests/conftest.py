import pytest

pytest_plugins = ("anyio",)


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("OCTOPRINT_URL", "http://octoprint.local")
    monkeypatch.setenv("OCTOPRINT_API_KEY", "test-api-key")
    monkeypatch.setenv("SYNAPSE_URL", "http://synapse.local")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456789")

    # Must clear lru_cache so Settings is re-read from the patched env.
    # config module may not exist yet, so guard the import.
    try:
        from config import get_settings
        get_settings.cache_clear()
    except ImportError:
        pass
    yield
    try:
        from config import get_settings
        get_settings.cache_clear()
    except ImportError:
        pass
