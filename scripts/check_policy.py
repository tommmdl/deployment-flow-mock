"""Invariantes de segurança complementares ao schema Kubernetes."""

import re
from pathlib import Path

import yaml

for overlay in ["local", "production"]:
    docs = list(yaml.safe_load_all(Path(f"artifacts/{overlay}.yaml").read_text()))
    deployment = next(x for x in docs if x["kind"] == "Deployment")
    spec = deployment["spec"]["template"]["spec"]
    assert spec["automountServiceAccountToken"] is False
    assert spec["securityContext"]["runAsNonRoot"] is True
    for container in spec["containers"]:
        assert container["securityContext"]["readOnlyRootFilesystem"] is True
        assert container["securityContext"]["allowPrivilegeEscalation"] is False
        assert container["securityContext"]["capabilities"]["drop"] == ["ALL"]
        assert {"requests", "limits"} <= container["resources"].keys()
        assert {"livenessProbe", "readinessProbe", "startupProbe"} <= container.keys()
        if overlay == "production":
            assert re.search(r"@sha256:[0-9a-f]{64}$", container["image"])
for path in Path(".github/workflows").glob("*.yml"):
    text = path.read_text()
    assert "pull_request_target" not in text
    for action in re.findall(r"uses: ([^\s]+)", text):
        assert action.startswith("./") or re.search(r"@[0-9a-f]{40}$", action), action
print("Políticas: manifests e SHAs de Actions OK")
