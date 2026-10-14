# Observabilidade local
Laboratório complementar via Compose, sem AWS. API: 8000, Prometheus: 9090, Grafana: 3000, todos vinculados a localhost. Grafana permite leitura anônima só neste laboratório; não exponha essa configuração em produção.

Validado localmente em 2026-10-14: target `api:8000` em `up`, configuração e quatro regras aprovadas pelo promtool, testes das regras aprovados, dashboard RED provisionado e seus quatro painéis retornando dados pelo datasource do Grafana. Carga de 50s com até 10 VUs: 2.771 requisições, zero falhas, checks 100%, p95 8,72ms. [Evidência](../docs/evidence/observability-compose-2026-10-14.json) e [resumo original da carga](../docs/evidence/load-compose-2026-10-14.txt). Validação do Grafana via API, sem inspeção visual no navegador.

Acessos: [Prometheus](http://localhost:9090), [dashboard Grafana](http://localhost:3000/d/deployment-flow) e [API](http://localhost:8000). Serviços deixados ligados após a validação.

Nesta sessão, o plugin `docker compose` não estava instalado. O binário oficial Compose v5.6.0 foi baixado e teve seu SHA256 verificado; está em `artifacts/bin/docker-compose` (ignorado pelo Git). Nesse ambiente, substitua `docker compose` por `artifacts/bin/docker-compose` nos comandos abaixo. A exportação JSON do k6 falhou por permissão no bind mount; o resumo textual da execução foi preservado.

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

Também é possível validar regras e executar carga sem Docker após instalar os binários com lock:

```bash
python3 scripts/install_tool.py promtool
python3 scripts/install_tool.py k6
artifacts/bin/promtool check rules observability/rules.yaml
(cd observability && ../artifacts/bin/promtool test rules rules.test.yaml)
artifacts/bin/k6 run -e BASE_URL=http://127.0.0.1:8000 observability/load.js
```
