"""Integração HTTP real, sem dependências de teste."""

import json
import sys
import urllib.request

base = sys.argv[1].rstrip("/")
for endpoint in ["/", "/health/live", "/health/ready", "/metrics"]:
    with urllib.request.urlopen(base + endpoint, timeout=5) as response:
        assert response.status == 200
req = urllib.request.Request(
    base + "/api/calculate", data=b'{"a":2,"b":3}', headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=5) as response:
    assert json.load(response) == {"result": 5}
print("Smoke HTTP: endpoints, readiness, métricas e cálculo OK")
