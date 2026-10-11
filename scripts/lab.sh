#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
NAME=deployment-flow
CTX=kind-deployment-flow
k() { kubectl --context "$CTX" "$@"; }
case "${1:-}" in
  prepare)
    for tool in docker kind kubectl curl; do command -v "$tool" >/dev/null; done
    docker info >/dev/null
    if ! kind get clusters | grep -qx "$NAME"; then
      kind create cluster --name "$NAME" --config infra/kind/cluster.yaml --wait 120s
    fi
    ;;
  deploy)
    docker build -t deployment-flow:local .
    kind load docker-image deployment-flow:local --name "$NAME"
    k apply -k gitops/overlays/local
    k -n deployment-flow rollout status deployment/api --timeout=180s
    ;;
  verify)
    k -n deployment-flow rollout status deployment/api --timeout=180s
    k -n deployment-flow port-forward service/api 18000:8000 > /tmp/deployment-flow-forward.log 2>&1 &
    forward=$!
    trap 'kill "$forward" 2>/dev/null || true' EXIT
    for _ in $(seq 1 30); do curl -fsS http://127.0.0.1:18000/health/ready >/dev/null && break; sleep 1; done
    python3 scripts/smoke.py http://127.0.0.1:18000
    ;;
  argocd)
    k create namespace argocd --dry-run=client -o yaml | k apply -f -
    k apply --server-side --force-conflicts -n argocd -f infra/kind/argocd-install.yaml
    k -n argocd rollout status deployment/argocd-server --timeout=300s
    k apply -f gitops/argocd/project.yaml
    k apply -f gitops/argocd/application.yaml
    ;;
  remove)
    kind delete cluster --name "$NAME"
    if kind get clusters | grep -qx "$NAME"; then exit 1; fi
    ;;
  *) echo "Uso: $0 {prepare|deploy|verify|argocd|remove}" >&2; exit 2 ;;
esac
