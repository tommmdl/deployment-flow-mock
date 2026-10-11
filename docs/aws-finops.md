# AWS e FinOps — referência paga, não aplicada
O laboratório kind/Compose não usa AWS. Terraform descreve VPC em duas AZs, NAT por AZ, EKS 1.35, dois t3.medium, EBS gp3 criptografado, IMDSv2, logs com 7 dias, tags e orçamento. Este desenho **gera custos** se aplicado. Não há apply no workflow e nenhuma criação foi executada.

## Estado e identidade
Backend S3 existente com versionamento, criptografia, bloqueio de acesso público e política TLS obrigatório. Lock nativo `use_lockfile=true`; não usamos DynamoDB legado. O bucket e o provider OIDC não são criados neste módulo: bootstrap separado exige autorização e proteção contra remoção. O estado pode conter dados sensíveis e deve ter acesso auditado. Não incluir credenciais em backend.hcl, tfvars, arquivos plan ou logs.

```bash
python3 scripts/install_tool.py terraform
artifacts/bin/terraform -chdir=infra/aws fmt -check
artifacts/bin/terraform -chdir=infra/aws init -backend=false -input=false
artifacts/bin/terraform -chdir=infra/aws validate
# As etapas abaixo são apenas roteiro para fase AWS autorizada:
# cp infra/aws/backend.hcl.example infra/aws/backend.hcl
# cp infra/aws/terraform.tfvars.example infra/aws/terraform.tfvars
# preencher valores; arquivos reais de estado/plan/tfvars não são versionados
# terraform -chdir=infra/aws init -backend-config=backend.hcl
# terraform -chdir=infra/aws plan -input=false
```
AWS workflow é manual, só main, environment aws-plan, role assumida via OIDC por 900s. Policy de exemplo permite describe/read e lock S3 específico, sem criação/exclusão de infraestrutura. EC2 Describe e logs Describe exigem escopo amplo; demais recursos são restritos. Se o provider solicitar outro read, revisar o erro e adicionar somente ação/recurso necessários, nunca AdministratorAccess. IAM de deploy não foi criado; precisa de desenho separado antes de apply. O CNI usa policy do nó como referência inicial: produção deve mover para Pod Identity e restringir exposição de IAM aos pods. EKS access entries/addons/credenciais de pull e rede do operador são próximos passos, não uma produção pronta.

## Estimativa verificável
[Calculadora oficial AWS](https://calculator.aws/) e [preços EKS](https://aws.amazon.com/eks/pricing/), [EC2](https://aws.amazon.com/ec2/pricing/on-demand/), [VPC/NAT](https://aws.amazon.com/vpc/pricing/), [EBS](https://aws.amazon.com/ebs/pricing/), [CloudWatch](https://aws.amazon.com/cloudwatch/pricing/) e [S3](https://aws.amazon.com/s3/pricing/) devem ser consultados para região/data/tributos antes de autorização. Não assumimos free tier nem preços universais.

| Recurso | Quantidade declarada | Fórmula mensal (730h) |
|---|---|---|
| EKS control plane | 1 | 730 × preço/h standard; extended support é adicional |
| EC2 t3.medium Linux On-Demand | 2 desejados, até 3 | 2 × 730 × preço/h; incluir créditos CPU quando aplicável |
| gp3 | 2 × 20 GiB | 40 × preço GiB/mês + IOPS/throughput extra |
| NAT Gateway | 2 | 2 × 730 × preço/h + GB processados × tarifa |
| IPv4 público dos NAT | 2 | 2 × 730 × tarifa/h de IPv4 |
| CloudWatch | ingestão e 7 dias | GB ingeridos × tarifa + armazenamento |
| S3 backend | estado + versões | GB/mês + requests; preservar versões durante teardown |
| Tráfego | depende de uso | egress internet e entre AZs conforme fluxo |
| Load Balancer / observabilidade persistente | não provisionados | somar em fase futura |

`python3 scripts/estimate_cost.py --rates arquivo.json` produz subtotal de compute fixo. Exemplo de formato em `infra/aws/rates.example.json` tem valores zero como placeholders; o script rejeita zeros para impedir apresentação de estimativa falsa. Registre rates com região, data, fonte e aprovação. Somar variáveis de tráfego/logs é obrigatório antes da decisão. NAT pode dominar a conta; avaliação de endpoints, arquitetura ou Spot vem após necessidade e medição.

Tags: Project, Environment, Owner, CostCenter, ManagedBy. Ativar cost allocation tags no Billing e confirmar cobertura; tags não limitam consumo. AWS Budgets do módulo notifica 80% real e 100% previsto do orçamento mensal da conta. **Não é teto automático**, não interrompe recursos e pode atrasar. Ajustar budget ao custo estimado, validar email e testar recebimento. Budget do exemplo é account-wide deliberadamente; custos de outros projetos também entram.

## Teardown verificável (futuro, após autorização)
1. Confirmar conta, região e workspace; preservar estado/versões e logs de auditoria. Listar recursos por tags e estado.
2. Remover Services LoadBalancer/ingresses/PVCs criados dentro do cluster antes de remover EKS, aguardando LBs/volumes associados. Este módulo não gerencia recursos criados por controllers externos.
3. Gerar `terraform plan -destroy -out=destroy.tfplan`, revisar cada recurso e obter autorização explícita antes de aplicar o plano. Não usar role read-only para destroy.
4. Após destroy autorizado, `terraform state list` deve estar vazio para este módulo; confirmar via APIs/console ausência de EKS/nodegroups, NAT gateways, EIPs, EC2, EBS, ENIs, LBs, logs e budgets relacionados. AWS pode manter recursos em estado deleting durante minutos.
5. Conferir Resource Groups Tagging API e Cost Explorer após atraso de billing; registrar evidências com horário/IDs. `aws resourcegroupstaggingapi get-resources --tag-filters Key=Project,Values=deployment-flow` é complementar, não cobre todo recurso/sem tags.
6. Bucket de estado/versões e role de bootstrap ficam fora do módulo; qualquer remoção separada requer aprovação, retenção e revisão. Nunca esvaziar bucket compartilhado. Custos residuais (storage/snapshots/IPv4) precisam de verificação própria.

## Cenário numérico de referência
Cenário ilustrativo de 730h, sem desconto/crédito, com tarifas publicadas em fontes oficiais consultadas em 2026-10-11. Não é uma cotação contratual de us-east-1: alguns valores são exemplos documentais da AWS, que exigem confirmação regional no Calculator.

| Item | Tarifa assumida | Estimativa mensal USD | Fonte oficial |
|---|---|---|---|
| EKS standard | 0,10/h | 73,00 | [EKS pricing](https://aws.amazon.com/eks/pricing/) |
| 2 t3.medium | 0,0416/h cada | 60,74 | [AWS instance selector](https://github.com/aws/amazon-ec2-instance-selector) |
| 2 NAT | 0,045/h cada | 65,70 | [VPC pricing](https://aws.amazon.com/vpc/pricing/) |
| 2 IPv4 | 0,005/h cada | 7,30 | [VPC pricing](https://aws.amazon.com/vpc/pricing/) |
| 40 GiB gp3 | 0,08/GB-mês | 3,20 | [EBS pricing: exemplo gp3](https://aws.amazon.com/ebs/pricing/) |
| Subtotal fixo | | **209,94** | Não inclui tráfego, logs, S3, CPU credits ou impostos |

Reproduzir com `python3 scripts/estimate_cost.py --rates infra/aws/rates.reference.json`. Orçamento default 250 USD é um valor de alerta ilustrativo; variáveis e escala até 3 nós podem ultrapassá-lo. Não aplicar para testar o alerta.
