# Evidências de validação
Executado em 2026-10-11, Linux AMD64, Python 3.12.3. Não há badges nem resultados simulados.

| Verificação executada | Resultado observado |
|---|---|
| Instalação `pip install --require-hashes -r app/requirements-dev.txt` | Concluída; `pip check`: No broken requirements found |
| Ruff check + format check | All checks passed; arquivos formatados |
| `.venv/bin/pytest -q` | 8 passed, 1 warning (depreciação Starlette/httpx), 1.03s |
| Uvicorn real em localhost:18001 + `scripts/smoke.py` | Endpoints, readiness, métricas e cálculo OK |
| Integração HTTP via subprocess no pytest | Passou; servidor iniciado e finalizado no teste |
| Rollback Git em fixture temporária | Passou; digest anterior restaurado e mudança independente preservada |
| `pip-audit -r app/requirements.txt --require-hashes` | No known vulnerabilities found |
| `bash scripts/validate_manifests.sh` | Local e production: 3 recursos cada, Valid 3, Invalid 0, Errors 0, Skipped 0; políticas de segurança/SHAs OK |
| `trivy config --severity HIGH,CRITICAL --exit-code 1 gitops/base` | 3 arquivos, zero achados no filtro HIGH/CRITICAL |
| `promtool check rules observability/rules.yaml` | SUCCESS: 4 rules found |
| `promtool check config --syntax-only observability/prometheus.yaml` | Sintaxe válida; paths /etc/prometheus resolvem no Compose |
| `promtool test rules rules.test.yaml` em observability/ | SUCCESS; cenários disponível/indisponível |
| Terraform 1.16.5 `init -backend=false` | Provider AWS 6.68.0 instalado e assinatura HashiCorp verificada; lock gerado |
| Terraform fmt -check / validate | Sem diferenças; Success! The configuration is valid |
| Parse YAML/JSON e bash -n | Sem erros |
| Estimador FinOps | Subtotal ilustrativo USD 209.94; rejeita rates zerados com exit != 0 |
| Gitleaks dir app e git com redaction | No leaks found; git verificou 2 commits, ~2.83 MB |
| k6 2.3.0 contra Uvicorn localhost, 50s, até 10 VUs | 2803 requisições; 0 falhas; checks 100%; p95 5.54ms; thresholds passaram, exit 0 |

Kubeconform usa schemas 1.35.0 estritos vendorizados com commit/checksum de origem. kind está pinado a node 1.35.8 por digest. Scans descrevem o estado das bases no horário da execução; não são garantia futura.

## Impedimentos e etapas não executadas localmente
Docker instalado, mas `docker info` falha: socket `/var/run/docker.sock` inexistente. Tentativa de iniciar serviço com `sudo -n service docker start` fora do sandbox retornou `sudo: a password is required`. Não contornamos a autenticação do host.

Por isso build Docker, scan de imagem, integração kind/Argo e Compose não foram executados localmente. O CI entregue executa build/scan e cluster temporário num runner hospedado; seu resultado será registrado após execução. Publicação GHCR, SBOM, Cosign e promoção GitOps aguardam merge e configuração do proprietário. Reconciliação/rollback em cluster ainda não foram comprovados. Terraform plan com backend remoto/OIDC, apply e destroy não foram executados; nenhum recurso AWS foi criado.

Algumas validações iniciais encontraram problemas que foram corrigidos: linhas Ruff longas formatadas, HCL com blocos compactos reescrito e formatado, schema remoto lento substituído por arquivos fixados. Verificação completa do config Prometheus no host exige mapear paths do container; sintaxe e regras foram checadas separadamente.

Resumo original de carga em [evidence/load-local.json](evidence/load-local.json). Este teste mediu o processo local, sem limites de container; não representa capacidade de produção nem resultados de kind.

PR de entrega: https://github.com/tommmdl/deployment-flow-mock/pull/1. O [primeiro CI](https://github.com/tommmdl/deployment-flow-mock/actions/runs/38182350181) construiu a imagem Bookworm, mas falhou no gate de vulnerabilidades HIGH/CRITICAL do sistema. Alteração: Alpine 3.24 com digest e gate mantido; resultado final deve ser conferido nos checks do PR. A execução inicial não chegou à integração kind.
