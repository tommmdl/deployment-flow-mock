import re
import sys
from pathlib import Path

image, digest = sys.argv[1:]
if not re.fullmatch(r"ghcr\.io/[a-z0-9._/-]+", image):
    raise SystemExit("Imagem GHCR inválida")
if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
    raise SystemExit("Digest inválido")
p = Path("gitops/overlays/production/kustomization.yaml")
s = re.sub(r"newName: .*", f"newName: {image}", p.read_text())
s = re.sub(r"digest: sha256:[a-f0-9]{64}", f"digest: {digest}", s)
p.write_text(s)
