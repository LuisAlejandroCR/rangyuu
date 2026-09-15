# test_config.py: configuration precedence. A real environment variable must always beat
# .env.local, so a deployed secret is never shadowed by a stale file left in the image.

from rangyuu import config


def _write(tmp_path, text):
    (tmp_path / config.ENV_FILE).write_text(text, encoding="utf-8")


def test_env_file_is_read_when_the_variable_is_absent(tmp_path, monkeypatch):
    _write(tmp_path, "# comentario\nRING_WEBHOOK_SECRET='s3cr3t'\nRING_CLIENT_ID=\"abc\"\n\nVACIO=\n")
    monkeypatch.chdir(tmp_path); monkeypatch.delenv("RING_WEBHOOK_SECRET", raising=False); config.reset()
    assert config.get("RING_WEBHOOK_SECRET") == "s3cr3t"
    assert config.get("RING_CLIENT_ID") == "abc"
    assert config.get("VACIO", "fallback") == "fallback"


def test_real_environment_wins_over_the_file(tmp_path, monkeypatch):
    _write(tmp_path, "RING_WEBHOOK_SECRET=from-file\n")
    monkeypatch.chdir(tmp_path); monkeypatch.setenv("RING_WEBHOOK_SECRET", "from-env"); config.reset()
    assert config.get("RING_WEBHOOK_SECRET") == "from-env"


def test_missing_file_is_not_an_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path); monkeypatch.delenv("RING_CLIENT_SECRET", raising=False); config.reset()
    assert config.get("RING_CLIENT_SECRET") == ""
