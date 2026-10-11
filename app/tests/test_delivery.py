"""Integração com servidor real e restauração da versão declarada em Git."""

import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_real_http_smoke():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(100):
            assert process.poll() is None, "Servidor terminou antes da readiness"
            try:
                with urllib.request.urlopen(base + "/health/ready", timeout=0.2) as response:
                    if response.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.05)
        else:
            raise AssertionError("Servidor não ficou pronto")
        subprocess.run([sys.executable, "scripts/smoke.py", base], cwd=ROOT, check=True)
    finally:
        process.terminate()
        process.wait(timeout=10)


def test_rollback_restores_only_declared_version(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=tmp_path, text=True).strip()

    git("init", "-b", "main")
    git("config", "user.email", "test@example.invalid")
    git("config", "user.name", "Test")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy(ROOT / "scripts/rollback.sh", scripts / "rollback.sh")
    image = tmp_path / "gitops/overlays/production/kustomization.yaml"
    image.parent.mkdir(parents=True)
    original = "digest: sha256:" + "a" * 64 + "\n"
    image.write_text(original)
    git("add", ".")
    git("commit", "-m", "versão anterior")
    previous = git("rev-parse", "HEAD")
    image.write_text("digest: sha256:" + "b" * 64 + "\n")
    (tmp_path / "unrelated.txt").write_text("manter mudança independente")
    git("add", ".")
    git("commit", "-m", "versão nova")
    git("switch", "-c", "fix/rollback")
    subprocess.run(["bash", "scripts/rollback.sh", previous], cwd=tmp_path, check=True)
    assert image.read_text() == original
    assert (tmp_path / "unrelated.txt").read_text() == "manter mudança independente"
    assert git("status", "--porcelain") == ""
    assert "restaurar versão" in git("log", "-1", "--format=%s")
