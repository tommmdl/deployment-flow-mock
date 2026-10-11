# Observabilidade local
Laboratório complementar via Compose, sem AWS. API: 8000, Prometheus: 9090, Grafana: 3000, todos vinculados a localhost. Grafana permite leitura anônima só neste laboratório; não exponha essa configuração em produção.

```bash
docker compose -f observability/compose.yaml up --build -d
docker compose -f observability/compose.yaml run --rm --entrypoint promtool prometheus check rules /etc/prometheus/rules.yaml
docker run --rm -v "$PWD/observability:/work:ro" -w /work --entrypoint promtool prom/prometheus:v3.15.0 test rules rules.test.yaml
docker run --rm --network deployment-flow-mock_default -v "$PWD/observability/load.js:/load.js:ro" grafana/k6:2.3.0 run /load.js
docker compose -f observability/compose.yaml down -v --remove-orphans
```
Use `docker network ls` para conferir o nome da rede se renomear o diretório. Dashboard RED provisionado. Prometheus retém 24 horas / 256 MB. Alertas são avaliados, mas sem Alertmanager/receiver não enviam mensagens.

SLO proposto: 99,9% das requisições da aplicação sem 5xx em janela de 30 dias; p95 menor que 300ms. Orçamento de erro: 0,1% das requisições. Probes e scrape ficam fora do denominador. Falhas antes de chegar à API não entram neste SLI: próxima fase adiciona blackbox externo e duas janelas de burn rate. Não há histórico suficiente no MVP para afirmar cumprimento de SLO.

Este Compose observa sua própria API; não observa automaticamente os pods kind. Próxima fase: Prometheus Operator no cluster, ServiceMonitor por pod, kube-state-metrics, node-exporter, Alertmanager, armazenamento e autenticação. Coletar somente o Service pode ocultar falha de uma réplica.
