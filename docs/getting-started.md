# Executar o laboratório

[Voltar ao README](../README.md)

## API e implantação local

Execute os comandos na raiz do repositório. Escolha entre o overlay local e o fluxo GitOps; aplicar o overlay local após ativar Argo no mesmo namespace altera os recursos gerenciados por ele.
Pré-requisitos: Linux AMD64 (ou WSL2 com Docker acessível), Python 3.14.8, Git, Docker Engine + Compose v2, kubectl, kind 0.33.0, curl. Recomenda-se 4 CPUs, 8 GiB de RAM e 15 GiB de disco livres para kind + Argo CD. `make` é opcional.

```bash
git clone https://github.com/tommmdl/gitops-delivery-platform.git
cd gitops-delivery-platform
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r app/requirements-dev.txt
.venv/bin/ruff check app scripts
.venv/bin/ruff format --check app scripts
.venv/bin/pytest -q
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
# Em outro terminal:
python3 scripts/smoke.py http://127.0.0.1:8000
```

API: `GET /`, `POST /api/calculate` com `{"a":2,"b":3}`, `GET /health/live`, `GET /health/ready`, `GET /metrics`. Readiness é falsa fora do ciclo de vida; liveness independe dela. O serviço é stateless, sem banco ou autenticação no laboratório.

```bash
python3 scripts/install_tool.py kind
python3 scripts/install_tool.py kubectl
export PATH="$PWD/artifacts/bin:$PATH"
bash scripts/lab.sh prepare
bash scripts/lab.sh deploy
bash scripts/lab.sh verify
kubectl --context kind-deployment-flow -n deployment-flow port-forward service/api 8000:8000
# Finalizar o port-forward com Ctrl+C antes de remover:
bash scripts/lab.sh remove
```
Todos os comandos Kubernetes dos scripts usam explicitamente `kind-deployment-flow`. Eles não alteram seu contexto global. A imagem local tem tag `local`; produção usa digest imutável. Alterações locais exigem novo build/load e reinício do Deployment (`kubectl --context kind-deployment-flow -n deployment-flow rollout restart deployment/api`), pois reaplicar a mesma tag não muda o Pod template.

## GitOps com Argo CD
O manifesto oficial Argo CD 3.5.4 está vendorizado, com origem e checksum em [argocd-source.txt](argocd-source.txt). Não usamos a branch mutável `stable` durante instalação.

1. Para reproduzir em um fork, ajuste o proprietário, o endereço do repositório no Argo e a imagem GHCR. Configure os environments e tokens conforme [configurações do proprietário](github-owner.md).
2. O overlay deste projeto já declara um digest publicado. Em um fork, publique sua imagem pelo fluxo de release e revise o PR que atualiza o digest antes de sincronizar. Um digest zerado de bootstrap não é executável.
3. O overlay production referencia o Secret `ghcr-pull`: crie o Secret docker-registry no namespace deployment-flow fora do Git antes da sincronização. Se tornar o pacote público, remova a referência em um PR. O repositório Git foi confirmado público na validação de 14/10/2026; o pacote GHCR foi confirmado privado. Se usar um repositório Git privado, configure também credencial read-only no Argo pela UI/CLI, fora do Git.
4. Execute `bash scripts/lab.sh prepare` e `bash scripts/lab.sh argocd`. Não execute o deploy local após ativar o Argo no mesmo namespace: ele sobrescreveria a versão declarada.
5. Acesse com `kubectl --context kind-deployment-flow -n argocd port-forward svc/argocd-server 8080:443`, use HTTPS em localhost e a senha inicial fornecida pelo Secret do Argo. Rotacione a senha após login. Configure a credencial Git na UI se necessário.
6. Aguarde `Synced` e `Healthy`, confirme o digest com `kubectl --context kind-deployment-flow -n deployment-flow get deployment api -o jsonpath='{.spec.template.spec.containers[0].image}'` e execute `bash scripts/lab.sh verify`.

O AppProject limita fonte, destino e tipos de recursos. O Argo CD padrão ainda tem privilégios amplos no cluster: esta instalação é exclusiva do laboratório.


## Observabilidade

Consulte [o guia de Prometheus e Grafana](../observability/README.md) para iniciar o Compose. Essa stack monitora sua própria API; não coleta automaticamente os pods kind.

## Troubleshooting
| Sintoma | Verificação / ação |
|---|---|
| Docker socket indisponível | `docker info`; iniciar Docker Desktop/Engine no host. Não execute os scripts com sudo por rotina. |
| kind lento / OOM | Liberar RAM/disco; conferir `docker stats`, `docker system df`; não remover recursos de outros projetos. |
| ImagePullBackOff | Verificar digest, visibilidade GHCR e pull secret; confira se o digest declarado existe no registry. |
| Argo Repository error | Repositório privado exige credencial read-only no Argo; não no YAML. |
| Argo OutOfSync | Conferir branch/path, commit e permissões do AppProject; evitar `kubectl edit` com self-heal. |
| Readiness falha | `kubectl --context kind-deployment-flow -n deployment-flow logs -l app=api` e `describe pods`. |
| Scan falha | Investigar CVE e atualizar dependência/base; não adicionar ignore genérico. DB/schema externos exigem rede. |
| PR GitOps não roda CI | Usar `GITOPS_PR_TOKEN` dedicado, não o token padrão; conferir proteção/env. |
| Dashboard sem dados | Gerar tráfego, aguardar scrape + janela; conferir targets em localhost:9090. |
