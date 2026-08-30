from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace


def _load_script_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "setup_linkedin_personal.py"
    spec = spec_from_file_location("setup_linkedin_personal", script)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_set_env_values_updates_and_preserves(tmp_path):
    module = _load_script_module()
    env = tmp_path / ".env"
    env.write_text(
        "PUBLISHER_ENABLED=true\nDRY_RUN=false\nKEEP_ME=value\nLINKEDIN_ACCESS_TOKEN=old\n",
        encoding="utf-8",
    )

    module._set_env_values(
        env,
        {
            "PUBLISHER_ENABLED": "false",
            "DRY_RUN": "true",
            "LINKEDIN_ACCESS_TOKEN": "new-token",
            "LINKEDIN_PERSON_URN": "urn:li:person:abc123",
        },
    )

    content = env.read_text(encoding="utf-8")
    assert "PUBLISHER_ENABLED=false" in content
    assert "DRY_RUN=true" in content
    assert "KEEP_ME=value" in content
    assert "LINKEDIN_ACCESS_TOKEN=new-token" in content
    assert "LINKEDIN_PERSON_URN=urn:li:person:abc123" in content
    assert "old" not in content


def test_read_windows_clipboard(monkeypatch):
    module = _load_script_module()
    monkeypatch.setattr(module.sys, "platform", "win32")
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="linkedin-token\r\n"),
    )
    assert module._read_windows_clipboard() == "linkedin-token"
