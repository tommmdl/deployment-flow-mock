"""Instala binários Linux AMD64 com hashes revisáveis no lock."""

import hashlib
import io
import json
import os
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

name = sys.argv[1]
entry = json.loads(Path("infra/tools.lock.json").read_text())[name]
cache = Path("artifacts/downloads") / name
data = cache.read_bytes() if cache.exists() else urllib.request.urlopen(entry["url"], timeout=120).read()
if hashlib.sha256(data).hexdigest() != entry["sha256"]:
    raise SystemExit("Checksum divergente: " + name)
if entry["format"] == "tar":
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        member = next(m for m in archive.getmembers() if m.name.split("/")[-1] == name and m.isfile())
        data = archive.extractfile(member).read()
elif entry["format"] == "zip":
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        data = archive.read(name)
out = Path("artifacts/bin") / name
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(data)
os.chmod(out, 0o755)
print(out)
