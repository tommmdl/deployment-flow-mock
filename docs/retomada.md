# Ponto de retomada — trabalho pausado

Registro em 2026-10-11 (America/Sao_Paulo; merge em 2026-10-12 UTC). Retomar somente em nova sessão solicitada pelo proprietário.

## Estado concluído

- CI, publicação no GHCR, assinatura Cosign e promoção GitOps concluídos.
- [PR GitOps #8](https://github.com/tommmdl/deployment-flow-mock/pull/8) mesclado em `5a217944c7d2765e2c14fc9c2c60b68ba181d42d` (`5a21794`). O diff alterou somente o digest em `gitops/overlays/production/kustomization.yaml`.
- [CI do commit revisado](https://github.com/tommmdl/deployment-flow-mock/actions/runs/38188707704/job/114616572758): `quality` passou em `3851ee7be1ed0b18ab3da2a15e36e1360c4240e8`.
- [Release concluída](https://github.com/tommmdl/deployment-flow-mock/actions/runs/38188436861): publicação e etapa de assinatura passaram; o digest usado na assinatura corresponde ao declarado no GitOps. Não foi realizada verificação criptográfica independente contra o registry nesta sessão.
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
