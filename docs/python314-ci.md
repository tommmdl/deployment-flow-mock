# CI da migração Python 3.14

PR #2: https://github.com/tommmdl/gitops-delivery-platform/pull/2.

O CI inicial construiu a imagem 3.14.8/Alpine 3.24, mas o Trivy encontrou quatro achados HIGH: msgpack 1.1.2 (GHSA-6v7p-g79w-8964), setuptools 70.3.0 (CVE-2025-47273), urllib3 2.7.0 (CVE-2026-97687 e CVE-2026-97689). Fonte: https://github.com/tommmdl/gitops-delivery-platform/actions/runs/38183209859.

A inspeção das camadas Linux AMD64 da base, verificadas pelo digest publicado, confirmou essas versões em `usr/local/lib/python3.14/site-packages/pip/_vendor/vendor.txt`. São dependências internas do pip 26.2.1, também listadas em sua [fonte oficial](https://github.com/pypa/pip/blob/26.2.1/src/pip/_vendor/vendor.txt). Instalar versões novas desses pacotes no site-packages da aplicação não atualiza as cópias privadas do pip.

O Dockerfile instala a aplicação com os hashes existentes e remove pip e ensurepip ao finalizar o build. A API não instala dependências em execução e usa filesystem read-only. O gate HIGH/CRITICAL continua ativo, sem ignore ou exclusão de caminhos do scan. A versão/digest da base, UID não root e demais controles permanecem fixados.

CI passa a executar testes e ferramentas em Python 3.14.8, alinhado ao container. Os requisitos mantêm suas versões e hashes; a instalação em 3.14 é validada pelo CI. Próximas atualizações devem regenerar os locks com Python 3.14. Os registros históricos de validação em Python 3.12 não foram reescritos.

A validação final de build, vulnerabilidades e smoke/carga kind aparece nos checks do próprio PR. Nenhum merge ou publicação GHCR é realizado por esta correção.
