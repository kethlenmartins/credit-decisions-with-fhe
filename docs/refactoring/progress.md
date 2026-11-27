# Progresso da refatoração

## Etapa 1 — infraestrutura segura

**Situação:** concluída para o escopo autorizado em 27 de novembro de 2026.

### Implementado

- Regras explícitas de proteção no `.gitignore` para dados, artefatos CKKSML, resultados privados, modelos, chaves, logs, checkpoints e saídas locais de notebooks.
- Schema declarativo e configuração YAML histórica sintética, sem criar parâmetros científicos Freddie Mac.
- Registro declarativo de Experiment ID para o smoke test sintético histórico.
- Carregamento seguro e validação de YAML, inclusive IDs, status, publicação, tipos e caminhos relativos seguros.
- Geração de Run IDs, manifestos portáveis, escrita atômica, diretórios independentes, transições de estado, retomada e verificação de SHA-256.
- Testes automatizados para configurações, registro, IDs, não sobrescrita, integridade de artefatos e retomada.

### Preservado

- `experiments/01_baseline.py`, `02_fhe_smoke.py` e `03_fhe_uci_smoke.py`.
- Protocolo científico existente e documentação UCI.
- Código/resultados da auditoria de datasets, datasets locais, ambientes locais e artefatos CKKSML.

## Etapa 2 — executor central seguro

**Situação:** COMPLETED em 27 de novembro de 2026, após aprovação da etapa 4.

- Implementado CLI, planejamento somente leitura, análise somente leitura, execução sintética explicitamente autorizada, consulta de status, verificação e retomada condicionada à capacidade real do adaptador.
- Criado o experimento `synthetic-executor-smoke`, destinado exclusivamente a testar infraestrutura. Ele não usa dados de crédito, FHE, Concrete ML ou CKKSML.
- Implementada proveniência inicial de código, ambiente e máquina pseudonimizada localmente.
- Os scripts UCI históricos, o protocolo, a auditoria de dados e os artefatos CKKSML foram preservados.

Detalhes, limitações e evidências constam em `docs/refactoring/executor_design.md` e `docs/refactoring/stage_2_validation.md`.

### Próxima etapa proposta — adaptação histórica controlada

Após aprovação, definir adaptadores de análise para os experimentos históricos sem mover ou refatorar seus scripts. A execução só deve ser conectada após comparação de comportamento e uma autorização específica.

## Etapa 3 — unidades experimentais científicas

**Situação:** concluída para o escopo autorizado em 27 de novembro de 2026.

- O registro ativo foi centralizado em `experiments/registry.yaml`; o registro anterior tornou-se um redirecionamento de compatibilidade, sem entradas independentes.
- HIST01 ganhou unidade local com configuração recuperada, README, resultados privados por Run ID e notebook de análise.
- O executor deriva o diretório de resultados da unidade registrada e localiza Run IDs sem selecionar silenciosamente uma execução ambígua. A raiz global antiga continua consultável para compatibilidade.
- A reexecução controlada de HIST01 foi equivalente à saída do script original no arredondamento histórico; detalhes em `historical_migration.md`.
- Foram criados notebook de visão geral, template científico e validação em kernel limpo com dependências opcionais.

HIST02 e HIST03 permanecem preservados e apenas registrados como históricos. Não foram executados ou migrados.

## Etapa 4 — encerramento estrutural

**Situação:** COMPLETED em 27 de novembro de 2026, após aprovação da etapa 4.

- IDs válidos e únicos foram atribuídos aos notebooks que não os tinham, sem mudança de conteúdo científico.
- HIST02 e HIST03 receberam unidades históricas, configuração, notebook de análise e importação rastreável dos relatórios legados locais; os scripts FHE originais permanecem intactos e não foram executados.
- O registro de importação distingue hash calculado agora de proveniência originalmente registrada.
- A equivalência de HIST01 permanece limitada às métricas agregadas arredondadas; os artefatos não permitem demonstrar identidade integral de predições históricas.
- As instruções de reprodução, proteção de resultados e criação de novas unidades foram revisadas. Auditorias concorrentes não foram migradas nem alteradas.

Não há nova etapa de refatoração estrutural autorizada. Qualquer mudança futura de infraestrutura requer necessidade concreta de experimento científico e aprovação apropriada. A integração das auditorias científicas permanece condicionada a autorização explícita.
