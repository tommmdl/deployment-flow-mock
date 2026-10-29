# Ponto de retomada

## Retomada em 2026-10-14

### Observabilidade concluída

Compose com API própria, Prometheus v3.15.0 e Grafana v13.2.3 validado após a implantação kind. Target em `up`, regras saudáveis, configuração completa e testes promtool aprovados. Os quatro painéis RED retornaram dados via datasource do Grafana. Carga k6 de 50s, até 10 VUs: 2.771 requisições, zero falhas, 100% dos checks e p95 8,72ms; thresholds aprovados, exit 0. [Evidência](evidence/observability-compose-2026-10-14.json), [carga](evidence/load-compose-2026-10-14.txt) e [acessos/comandos](../observability/README.md).

Serviços Compose e cluster kind deixados ligados. Próxima fase: exercitar incidente, rollback GitOps e recuperação com evidências. A janela curta não comprova o SLO de 30 dias; o Compose monitora sua própria API, e alertas não enviam notificações sem Alertmanager.

### Validação final concluída

Às 22:12 UTC (19:12 America/Sao_Paulo), Argo CD `Synced` e `Healthy` na revisão `5a217944c7d2765e2c14fc9c2c60b68ba181d42d`. Duas réplicas da API prontas, ambas com `imageID` correspondente ao digest declarado. `lab.sh verify` concluiu com exit 0: endpoints, readiness, métricas e cálculo OK.

O proprietário autorizou `read:packages` no GitHub CLI; o pacote foi confirmado como privado. O Secret `ghcr-pull` foi criado diretamente no cluster, sem registrar a credencial em arquivo local ou nas evidências. A consulta autenticada ao registry confirmou o hash do índice e o manifesto Linux AMD64 `sha256:742fe528d1c88a9a3f1563cfa5c522a9db490dd5213fdc01950cd6243d7373ec`. Isso confirma a relação de manifests; não constitui verificação criptográfica da assinatura Cosign.

[Evidência sanitizada da implantação](evidence/argocd-local-2026-10-14.json). A observabilidade prevista foi concluída e está registrada acima. O cluster permanece ligado; Docker depende do processo `dockerd` iniciado pelo proprietário.

### Preparação e impedimento resolvido

Validação local às 22:08 UTC (19:08 America/Sao_Paulo):

- Docker 29.1.3 iniciado pelo proprietário com `sudo dockerd`.
- A criação do nó falhou com `Failed to create control group inotify object: Too many open files`. O proprietário aumentou `fs.inotify.max_user_instances` de 128 para 512; a nova criação concluiu.
- Cluster dedicado `deployment-flow`, Kubernetes v1.35.8, nó `Ready`. Os clusters de outros projetos foram preservados.
- Kubeconfig exclusivo em `artifacts/kubeconfig` (ignorado pelo Git, permissões 600). Para executar os scripts nesta sessão: `export KUBECONFIG="$PWD/artifacts/kubeconfig"` na raiz do projeto.
- Argo CD v3.5.4 instalado; Application `deployment-flow` em `Synced`, saúde `Progressing`, revisão `5a217944c7d2765e2c14fc9c2c60b68ba181d42d`.
- O repositório foi consultado e está público; Argo sincronizou sem credencial Git.
- Os dois pods da API estão em `ImagePullBackOff`: Secret `ghcr-pull` ausente e GHCR retornando `401 Unauthorized` para pull anônimo do digest declarado abaixo. A sessão ativa do GitHub CLI também não tem `read:packages`.

O impedimento acima foi resolvido na validação final registrada nesta página. Nenhum recurso AWS foi criado.

## Registro anterior

Registro em 2026-10-11 (America/Sao_Paulo; merge em 2026-10-12 UTC). Retomar somente em nova sessão solicitada pelo proprietário.

## Estado concluído

- CI, publicação no GHCR, assinatura Cosign e promoção GitOps concluídos.
- [PR GitOps #8](https://github.com/tommmdl/gitops-delivery-platform/pull/8) mesclado em `5a217944c7d2765e2c14fc9c2c60b68ba181d42d` (`5a21794`). O diff alterou somente o digest em `gitops/overlays/production/kustomization.yaml`.
- [CI do commit revisado](https://github.com/tommmdl/gitops-delivery-platform/actions/runs/38188707704/job/114616572758): `quality` passou em `3851ee7be1ed0b18ab3da2a15e36e1360c4240e8`.
- [Release concluída](https://github.com/tommmdl/gitops-delivery-platform/actions/runs/38188436861): publicação e etapa de assinatura passaram; o digest usado na assinatura corresponde ao declarado no GitOps. Não foi realizada verificação criptográfica independente contra o registry nesta sessão.
- Imagem declarada e renderizada com Kustomize:

```text
ghcr.io/tommmdl/deployment-flow-mock@sha256:64720297e2f409652bb02a12d981a0aaddb0d02b3fe39695f3a6897383e87b9c
```

Após o merge, as consultas não encontraram workflows para o commit nem novo PR GitOps aberto. A release filtra caminhos que excluem `gitops/**`; o CI roda em PR ou como workflow reutilizável. Não houve publicação redundante ou ciclo observado. Isso registra a observação desta sessão, não monitoramento contínuo.

## Validação final pendente

O socket `/var/run/docker.sock` estava ausente. O contexto `kind-deployment-flow` não existia; somente `kind-lab` estava configurado. Não houve validação de reconciliação Argo CD, imagem efetivamente executada nem smoke tests no laboratório final. O CI em kind temporário não comprova essa implantação.

## Sequência da retomada

1. Consultar este registro, atualizar uma branch de trabalho com `origin/main` e confirmar que o digest esperado continua declarado. Não republicar a imagem apenas para retomar o laboratório.
2. Iniciar Docker pelo mecanismo do host/WSL, com autenticação do proprietário se necessária. Confirmar `docker info`. Não reutilizar o cluster `kind-lab` de outro projeto.
3. Preparar as ferramentas conforme o README e executar `bash scripts/lab.sh prepare`.
4. Configurar acesso read-only do Argo ao repositório privado e o pull secret `ghcr-pull` no namespace `deployment-flow`, fora do Git. Seguir o README; nunca registrar tokens ou senhas nas evidências.
5. Executar `bash scripts/lab.sh argocd`. Não executar `lab.sh deploy` após ativar Argo: esse comando aplica o overlay local.
6. Aguardar a Application `Synced` e `Healthy` e registrar a revisão Git reconciliada. Confirmar a imagem do Deployment e os `imageID` dos containers dos pods prontos. Um `imageID` de plataforma pode diferir do digest do índice publicado; nesse caso confirmar a relação usando o manifesto do registry, sem presumir igualdade literal.
7. Executar `bash scripts/lab.sh verify` e guardar saídas sanitizadas e horários. Somente então declarar a implantação final validada. Se falhar, consultar os runbooks e registrar a causa.

Comandos de inspeção, após preparar o laboratório:

```bash
kubectl --context kind-deployment-flow -n argocd get applications.argoproj.io -o yaml
kubectl --context kind-deployment-flow -n deployment-flow get deployment api -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl --context kind-deployment-flow -n deployment-flow get pods -l app=api -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{range .status.containerStatuses[*]}{.name}{" "}{.ready}{" "}{.imageID}{"\n"}{end}{end}'
bash scripts/lab.sh verify
```

## Fases seguintes

- Observabilidade: executar Prometheus/Grafana localmente, validar scrape, dashboards, regras e teste de carga.
- SRE: medir SLO, exercitar incidente, rollback GitOps e recuperação com evidências.
- Terraform/AWS: revisar arquitetura, OIDC, IAM mínimo e estado remoto. Não executar operações AWS nesta pausa. Criação de recursos pagos depende de autorização explícita.
- FinOps: atualizar estimativas por recurso, tags e procedimento verificável de teardown. Alertas de orçamento notificam; não são limite automático de gastos.

Referências: [README](../README.md), [runbooks](runbooks.md), [AWS/FinOps](aws-finops.md), [configurações do proprietário](github-owner.md) e [validações históricas](validation.md). Evidências antigas devem ser lidas com suas datas; este registro atualiza o estado da publicação e promoção.

Nenhum recurso AWS foi criado. O trabalho está pausado após este registro.
