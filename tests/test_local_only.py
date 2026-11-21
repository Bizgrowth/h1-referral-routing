"""Hard rule 1: no data leaves this machine. Hard rule 4: no data in the repo."""

import ast
from pathlib import Path
import shutil
import socket
import subprocess

import pytest

from h1 import importer, scoring
from scripts import check_no_data

ROOT = Path(__file__).resolve().parent.parent
CODE = [*ROOT.glob("h1/*.py"), *ROOT.glob("scripts/*.py"), ROOT / "app.py"]
BANNED = {"requests", "httpx", "urllib3", "aiohttp", "websocket", "websockets", "socket", "http.client",
          "urllib.request", "ftplib", "smtplib", "anthropic", "openai", "ollama", "cohere", "mistralai",
          "google.generativeai", "google.genai", "boto3", "langchain"}
DATA_FILES = ["data/Referrals.xlsx", "data/anything.txt", "output/scoring.json", "logs/decisions.jsonl",
              "export.csv", "x/Referrals.xlsx", "old.xls", "export.tsv", "db.accdb", "db.mdb", "local.db"]


def imported_modules(path):
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module
            yield from (f"{node.module}.{alias.name}" for alias in node.names)


@pytest.mark.parametrize("path", CODE, ids=lambda p: p.name)
def test_no_http_client_or_ai_api_imports(path):
    found = {m for m in imported_modules(path) for b in BANNED if m == b or m.startswith(b + ".")}
    assert not found, f"{path.name} imports {found}"


@pytest.mark.parametrize("path", [p for p in CODE if p.name != "app.py"], ids=lambda p: p.name)
def test_no_urls_on_data_path(path):
    assert "http://" not in path.read_text(encoding="utf-8") and "https://" not in path.read_text(encoding="utf-8")


def test_pipeline_runs_with_network_disabled(xlsx_path, monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("Network access attempted on the data path")
    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    assert scoring.score(importer.load(xlsx_path).rows)["overall"]["n"] == 5


def test_streamlit_usage_stats_off():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "gatherUsageStats = false" in config and 'address = "localhost"' in config


def test_precommit_check_blocks_data_files():
    assert check_no_data.blocked(DATA_FILES) == DATA_FILES
    assert check_no_data.blocked(["app.py", "h1/importer.py", "README.md", "requirements.txt"]) == []
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "scripts/check_no_data.py" in hook


@pytest.mark.skipif(not shutil.which("git"), reason="git not installed")
def test_gitignore_excludes_data_files():
    for path in DATA_FILES:
        result = subprocess.run(["git", "check-ignore", "--no-index", "-q", path], cwd=ROOT)
        assert result.returncode == 0, f"{path} is not ignored"
