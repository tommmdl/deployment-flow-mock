# Runbooks
## Incidente: 5xx ou latência
1. Registrar horário, commit/digest, impacto, taxa de erro e p95; nomear responsável.
2. Confirmar se alerta é de scrape ou de usuários; executar smoke, verificar pods/events/logs no contexto kind explícito.
3. Correlacionar com rollout recente. Investigar OOMKilled, readiness, CPU throttling e imagem.
4. Se regressão após release, restaurar digest pelo fluxo abaixo. Não editar manualmente Deployment controlado pelo Argo.
5. Confirmar Healthy/Synced, digest, rollout e smoke. Acompanhar métricas por 15 minutos e registrar causas e prevenção. Não declarar recuperação somente porque rollout terminou.

## Rollback GitOps
```bash
git fetch origin
git switch -c fix/rollback origin/main
git log --oneline -- gitops/overlays/production/kustomization.yaml
bash scripts/rollback.sh COMMIT_COM_DIGEST_ANTERIOR
git push -u origin fix/rollback
gh pr create --title 'revert: restaurar imagem anterior' --body 'Restaura digest conhecido; validar assinatura, Argo e smoke.'
```
O script exige working tree limpo e impede uso em main. Restaura somente a versão declarada do GitOps, permitindo rollback de imagem sem desfazer mudanças independentes. Revise e faça merge; Argo com self-heal reconcilia. `kubectl rollout undo` sozinho é revertido pelo Argo. Se precisar reverter configuração além da imagem, use `git revert` do commit GitOps completo em outro PR.

## Recuperação do laboratório
Repositório é fonte da configuração; API não guarda dados. Remover kind é destrutivo para todos os recursos desse cluster, inclusive credenciais do Argo. Execute `bash scripts/lab.sh remove`, prepare e reinstale Argo; restaure credenciais read-only e pull secrets fora do Git. Confirme reconciliação + smoke. Prometheus local usa dados efêmeros; histórico é perdido no teardown. RTO alvo experimental de 15 minutos, sem medição ou garantia.

## Supply chain
Se scan/signature/provenance falhar: bloquear promoção, preservar logs sem secrets, confirmar issuer e workflow identity, comparar SBOM/digest, atualizar fonte/base e repetir CI. Em suspeita de comprometimento: revogar token GitOps, revisar audit log, bloquear branch, girar credenciais externas e republicar de fonte revisada. Digest só evita substituição, não valida conteúdo.

## AWS recovery / teardown
Somente após autorização explícita, consultar [aws-finops.md](aws-finops.md). Estado S3 versionado, restrito e com lockfile. Nunca force-unlock sem confirmar ausência de operação ativa. Restore de versão de estado deve ser revisto e seguido de plan; estado não é backup de dados de aplicação.
