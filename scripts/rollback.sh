#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
commit=${1:?Informe o commit anterior que contém o digest desejado}
file=gitops/overlays/production/kustomization.yaml
[[ $(git branch --show-current) != main ]] || { echo 'Crie uma branch de rollback'; exit 1; }
[[ -z $(git status --porcelain) ]] || { echo 'Working tree deve estar limpo'; exit 1; }
rollback_file=$(mktemp)
trap 'rm -f "$rollback_file"' EXIT
git show "$commit:$file" > "$rollback_file"
python3 - "$rollback_file" <<'CHECK'
import re,sys
s=open(sys.argv[1]).read()
assert re.search(r'digest: sha256:[a-f0-9]{64}',s)
assert 'sha256:'+'0'*64 not in s
CHECK
cp "$rollback_file" "$file"
git add "$file"
git commit -m "revert: restaurar versão declarada de $commit"
echo 'Abra PR, revise e faça merge. Argo CD reconcilia; execute scripts/lab.sh verify.'
