# Decisões arquiteturais e ameaças
## ADR 001 — monorepo e laboratório isolado
App, infraestrutura, estado desejado e operação são revisados juntos. kind valida comportamento Kubernetes sem cobrar AWS. Compose oferece observabilidade de uma instância independente. Produção exige contas, identidades, rede e custos próprios.

## ADR 002 — dependências imutáveis
Python 3.14.8, requisitos diretos fixados, lock transitivo com hashes gerado por pip-tools. Docker base Python 3.14.8/Alpine 3.24 por digest. O primeiro scan CI bloqueou Bookworm por CVEs do sistema; migramos a runtime para Alpine, mantendo o gate HIGH/CRITICAL. Dependências possuem wheels musllinux; CI deve confirmar build e execução para detectar incompatibilidades de libc. Actions por SHA verificado e ferramentas Linux AMD64 por checksum da origem oficial. Pip e ensurepip são removidos depois da instalação no build: seus instaladores e dependências vendorizadas não são necessários na API. Detalhes em `docs/python314-ci.md`. Atualizações são PRs revisados; pins envelhecem, por isso Dependabot e scans não são opcionais. A migração para 3.14 preserva as versões/hashes existentes, originalmente resolvidos em 3.12, e valida instalação/testes em 3.14. O lock deve ser regenerado com Python 3.14 e `pip-compile --allow-unsafe --strip-extras --generate-hashes`.

## ADR 003 — promoção por digest
CI precede publicação. Uma imagem é construída e promovida pelo seu digest; rollback restaura um digest já publicado. Não reconstruir uma tag antiga e chamá-la de rollback. `release.yml` ignora alteração somente GitOps e docs para evitar loops. Não compartilhar cache de build gravável entre PR não confiável e release.

## ADR 004 — identidade efêmera
Cosign usa OIDC, sem chave privada persistente. AWS plan usa OIDC restrito ao repository/environment com role sem permissão de criação. Não há workflow de apply. O token GitOps de curta validade tem escopo mínimo ao repositório; evolução: GitHub App com token de instalação.

## Modelo de ameaças
| Ameaça / fronteira | Controle | Residual |
|---|---|---|
| PR malicioso → runner | pull_request, contents read, sem secrets, runner hospedado | Rede e consumo de runner; não usar self-hosted com PR público |
| Action/dependência comprometida | SHAs, hashes, lock, scan, revisão | Hash não prova ausência de código malicioso; instaladores de Actions podem buscar ferramentas transitivas |
| Artefato adulterado → cluster | Digest, Cosign, SBOM, proveniência | Admission enforcement não implementado; revisão humana deve verificar identidade |
| Container → host/API Kubernetes | UID 10001, filesystem RO, sem token/caps, seccomp, PSA restricted | kind e Argo exigem Docker/controle do cluster local |
| Credencial GitOps exposta | Só job trusted, environment, token repo-scoped, expiração | Código em main pode usar token; proteção e revisão de workflows são essenciais |
| AWS role → conta | Trust aud/sub exatos, policy de plan, S3 por prefixo | Describe EC2 exige `*`; criação futura exige policy distinta revisada |
| Métricas → dados sensíveis/DoS | Sem payload, caminho desconhecido agregador, métodos limitados | Endpoint interno sem auth; sem rate limit; não expor publicamente |
| Gastos inesperados → AWS | Plan manual, estimativa, tags, alertas, teardown | Budget não bloqueia gastos; alertas e billing podem atrasar |

## Limitações conhecidas
Sem TLS/auth/rate limiting na API, banco, ingress, NetworkPolicy efetiva, autoscaling, multi-cluster, DR real ou admission controller. kind padrão não garante enforcement de NetworkPolicy. Argo vendorizado precisa de revisão e updates. GHCR e repo privados exigem secrets externos ao Git. Digest inicial é bootstrap. Workflows são entregues para execução no GitHub; evidências distinguem checks feitos dos pendentes. TestClient sinaliza depreciação do httpx em Starlette atual; migração para httpx2 precisa de revisão futura. OIDC e produção não foram exercitados contra AWS.

## Próximas fases
1. Instrumentação por pod, blackbox, Alertmanager com receiver testado, burn rate de duas janelas e histórico SLO.
2. Policy de admissão verifica Cosign/identidade; CNI com NetworkPolicy, ingress TLS, auth e rate limit.
3. Separar conta AWS de sandbox, bootstrap de estado, role de aplicação mínima, CNI via Pod Identity, EKS access entries e addons versionados.
4. Testar recuperação de estado S3 e rollback automatizado, medir RTO/RPO, calibrar requests com carga, avaliar Spot e savings apenas com dados.
