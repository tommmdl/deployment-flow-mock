#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p artifacts
for overlay in local production; do
  kubectl kustomize "gitops/overlays/$overlay" > "artifacts/$overlay.yaml"
  artifacts/bin/kubeconform -strict -summary -kubernetes-version 1.35.0 -schema-location 'infra/schemas/{{.ResourceKind}}{{.KindSuffix}}.json' "artifacts/$overlay.yaml"
done
python3 scripts/check_policy.py
