# Publicação e segurança da imagem

[Voltar ao README](../README.md)

PRs executam em runners hospedados efêmeros com token read-only, sem secrets. A publicação executa apenas no push de `main`, após CI e environment `release`. A atualização GitOps usa um token dedicado no environment `gitops`, para que o novo PR dispare CI (PRs criados por `GITHUB_TOKEN` normalmente não disparam outros workflows). Mudanças somente em GitOps/docs não publicam outra imagem.

Verifique antes da promoção (requer login GHCR se pacote privado):
```bash
cosign verify ghcr.io/tommmdl/deployment-flow-mock@sha256:DIGEST \
  --certificate-identity=https://github.com/tommmdl/gitops-delivery-platform/.github/workflows/release.yml@refs/heads/main \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com
# Atestação GitHub adicional: repositório público ou plano compatível
gh attestation verify oci://ghcr.io/tommmdl/deployment-flow-mock@sha256:DIGEST --repo tommmdl/gitops-delivery-platform
```
O repositório se chamava `deployment-flow-mock` até 29/10/2026. As imagens publicadas antes dessa data continuam no pacote `ghcr.io/tommmdl/deployment-flow-mock` e foram assinadas com a identidade `https://github.com/tommmdl/deployment-flow-mock/.github/workflows/release.yml@refs/heads/main`. A próxima release publica em `ghcr.io/tommmdl/gitops-delivery-platform`, e o `update_digest.py` atualiza nome e digest juntos no overlay de produção.
BuildKit publica SBOM e proveniência como attestations OCI, além da atestação GitHub quando disponível no plano. Em repositório privado, a atestação GitHub adicional só roda com a variável `ENABLE_GITHUB_ATTESTATIONS=true`; SBOM/proveniência BuildKit continuam obrigatórias. Não afirmamos um nível SLSA certificado. A verificação é operacional; uma admission policy obrigatória ainda é evolução futura.

