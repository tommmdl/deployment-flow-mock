# Fontes oficiais consultadas em 2026-10-11
Versões foram verificadas nas APIs de releases do GitHub upstream, PyPI e registry Terraform. Os pins estão no lock de ferramentas, requisitos e Actions. Verificar novamente antes de atualizar; não interpretar estes pins como garantia permanente de latest.

- [FastAPI containers](https://fastapi.tiangolo.com/deployment/docker/): imagem própria, processo do servidor.
- [kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start/): kind 0.33.0, runtime local.
- [Argo CD instalação](https://argo-cd.readthedocs.io/en/stable/operator-manual/installation/): instalação declarativa; release 3.5.4 vendorizada.
- [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use): SHAs completos, privilégio mínimo e PRs não confiáveis.
- [Artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations): disponibilidade depende de visibilidade/plano.
- [Sigstore verificação](https://docs.sigstore.dev/cosign/verifying/verify/): verificar identity e issuer, não só existência de assinatura.
- [Prometheus alerting](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/): avaliação e entrega são componentes diferentes.
- [AWS GitHub OIDC claims](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_iam-condition-keys.html): trust aud/sub.
- [EKS platform versions](https://docs.aws.amazon.com/eks/latest/userguide/platform-versions.html): 1.35 suportada; fixada para reprodutibilidade, não latest obrigatório.
- [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3): use_lockfile e IAM por objeto.
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html): monitoramento e notificações, sem teto automático de consumo.

Binários: checksums publicados no campo digest da API de releases do GitHub; Terraform usa SHA256SUMS do domínio releases.hashicorp.com. Base Python resolvida pelo Docker Registry oficial para digest de manifest. Hashes conferidos antes da instalação. Arquitetura alvo Linux AMD64; outras plataformas exigem locks próprios.

Schemas Kubernetes estritos 1.35.0: [upstream do kubeconform](https://github.com/yannh/kubernetes-json-schema), arquivos e SHAs de origem em `infra/schemas/sources.json`. Node kind 1.35.8 por digest publicado na release oficial kind 0.33.0; kubectl 1.35.8 com checksum de dl.k8s.io. Python base atualizado para patch 3.12.15 por digest. Buildx 0.38.0 e BuildKit 0.34.0 verificados nas releases upstream; BuildKit e gerador SBOM Syft scanner 1.12.0 por digest Docker Registry. Cosign 3.1.3 instalado diretamente por checksum oficial, sem instalador transitivo mutável.
