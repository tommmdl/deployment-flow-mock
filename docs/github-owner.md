# Configurações do proprietário
Nada abaixo deve ser tratado como já configurado só porque o YAML existe.

- Revisar visibilidade do repositório e pacote GHCR. Este repositório foi criado privado. Plano GitHub privado pode restringir protections, reviewers e artifact attestations; conferir direitos antes da release. Publicação do portfólio exige decisão do proprietário.
- Ruleset de main: exigir PR, pelo menos uma aprovação, checks `CI / quality` (conferir nome real após primeira execução), impedir force push/deleção, resolver conversas e limitar bypass. Branch não deve aceitar alterações de workflow sem revisão. Não exigir assinatura de commit sem configurar a identidade do bot.
- Environments `release`, `gitops`, `aws-plan`: permitir apenas main, required reviewer quando suportado, bloquear self-review. Criar antes de habilitar publicação; o YAML não define reviewers.
- `gitops`: secret `GITOPS_PR_TOKEN`, fine-grained token para somente este repo com Contents write e Pull requests write, validade curta. Não conceder administração, packages ou AWS. Token diferente de GITHUB_TOKEN permite CI no PR automatizado; manter autor separado para aprovação humana.
- Atestações GitHub: `ENABLE_GITHUB_ATTESTATIONS=true` somente se o plano privado suportar; público habilita automaticamente. Proveniência/SBOM OCI do BuildKit não dependem dessa API.
- GHCR: conceder ao GITHUB_TOKEN do repo publicação de packages e associar pacote ao repo. Para pull privado em kind/EKS, criar secret fora do Git ou tornar apenas o pacote público com autorização.
- Argo: acesso Git read-only para o repo privado, credencial de imagem fora do Git, rotação da senha inicial. Não publicar senha/Secret nos logs ou commits.
- OIDC AWS: provider `token.actions.githubusercontent.com` preexistente, trust exato de `oidc-trust.json.example`, policy de plan ajustada a ACCOUNT_ID/STATE_BUCKET, região e paths. Environment aws-plan só main e reviewer. Nenhuma AWS access key em secrets.
- Vars de aws-plan: `AWS_PLAN_ROLE_ARN`, `TF_STATE_BUCKET`, `RESOURCE_OWNER`, `BUDGET_EMAIL`, `ADMIN_CIDRS_JSON` (lista JSON de CIDRs administrativos). Bootstrap backend e role é uma fase futura autorizada; não executado no MVP.
- Verificar quotas de minutos/storage do Actions antes de uso intenso, retenção do GHCR e notificações de alertas. Aprovar execuções de PR de forks conforme política. Não habilitar PRs não confiáveis em runners self-hosted.
- Dependabot: revisar PRs e regenerar locks/hashes. Não auto-merge mudanças de supply chain sem checks.
