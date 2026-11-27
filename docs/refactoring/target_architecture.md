# Arquitetura-alvo de infraestrutura experimental

## Escopo desta decisão

Esta arquitetura organiza a execução reproduzível sem congelar target, features, divisão temporal, pré-processamento, políticas ou hipóteses de Freddie Mac. O UCI 350 continua histórico: seus scripts permanecem nos caminhos atuais e não são evidência para a pesquisa com Freddie Mac.

```text
configs/                         dados declarativos e versionados
  schema/                        contrato de configuração
  experiments/                   configurações por investigação
  registry/                      catálogo estável de Experiment IDs
src/fhe_credit/                  validação, registro e utilitários reutilizáveis
results/runs/<run-id>/           saída privada e imutável por execução
results/public/                  somente inclusão deliberada após revisão
experiments/                     scripts históricos preservados nesta fase
notebooks/                       análise por padrão; execução só explícita (etapa futura)
```

## Identificadores e rastreabilidade

- **Experiment ID** identifica uma investigação estável no registro.
- **Configuration ID** identifica uma configuração legível e versionada; o `config_hash` identifica seu conteúdo canônico validado.
- **Run ID** é único por tentativa independente e não contém identidade da máquina. Retomadas mantêm o mesmo `Run ID` e acrescentam uma tentativa.

Um manifesto contém o commit e a condição `git_dirty`, mas não trata o commit como hash integral do código efetivo. O `effective_code_hash` é calculado a partir de um escopo filtrado e documentado de código, configuração e requisitos; ele não inclui dados, segredos ou artefatos privados e não substitui a revisão do conteúdo efetivo.

## Configurações

As configurações são YAML carregadas exclusivamente com `yaml.safe_load`; não são avaliadas como código. O validador exige schema versão `1.0`, IDs, descrição, status científico, dependências, parâmetros, referências de entrada, modo de execução e classificação de publicação. Caminhos declarados devem ser relativos ao repositório e não podem escapar com `..`.

Os valores científicos permitidos são `HISTORICAL`, `EXPLORATORY`, `PRELIMINARY` e `CONFIRMED`. As classificações de publicação são `PRIVATE`, `REVIEW_REQUIRED` e `PUBLIC_APPROVED`.

As configurações históricas de HIST02 e HIST03 autorizam apenas a importação explícita de relatórios JSON legados pelo adaptador permitido. Essa importação não inicia FHE nem altera os scripts existentes; a configuração sintética do executor permanece independente de dados de crédito.

## Ciclo de uma execução

1. A etapa futura lê registro e configuração validada.
2. Gera um `Run ID` e cria exclusivamente `results/runs/<run-id>/`.
3. Persiste manifestos e status por substituição atômica de arquivo.
4. Registra transições entre `CREATED`, `RUNNING`, `FAILED`, `INTERRUPTED` e `COMPLETED`.
5. Só marca `COMPLETED` quando todos os artefatos obrigatórios existem e seus SHA-256 foram calculados. Os hashes podem ser verificados posteriormente.

O executor central implementado opera apenas o adaptador sintético permitido. Não há dashboard, benchmark, treinamento ou inferência FHE.

## Privacidade e publicação

`results/runs/` é sempre ignorado. `results/public/` também é ignorado por padrão: somente seu `.gitkeep` é permitido automaticamente. A inclusão de um artefato público exige revisão e uma ação Git deliberada; a regra não libera a pasta inteira. Dados, predições individuais, identificadores, modelos, chaves, checkpoints, logs, saídas de notebooks, `datasets/` e `ckksml/` estão protegidos por regras explícitas.

## Ambientes e notebooks

`PyYAML` foi acrescentado ao ambiente base como dependência mínima para o formato de configuração. Concrete ML, CKKSML e ambientes existentes não foram alterados. Os notebooks serão implementados em etapa própria: modo padrão `analyze`, e `execute` sempre explícito para evitar iniciar FHE ao executar células de análise.

## Executor implementado

Os módulos em `src/fhe_credit/experiments/` separam CLI, planejamento, adaptadores, artefatos, execução, proveniência e erros. Adaptadores são um registro explícito em código; YAML apenas escolhe um identificador previamente permitido. Nenhum comando, módulo ou script arbitrário é executado a partir de YAML.

O `machine_id` passou a ser UUID aleatório persistido em `state/machine_id`, que é ignorado pelo Git e criado com permissões restritivas quando suportado. Ele não usa hostname, usuário ou MAC. Reinstalar a instalação altera o ID; copiar o arquivo de estado pode duplicá-lo. O manifesto registra ainda `hardware_fingerprint` e `environment_hash` separadamente.

## Unidades experimentais

O registro ativo está em `experiments/registry.yaml`. Para uma unidade registrada, a raiz padrão de novas execuções é `experiments/<área>/<unidade>/results/runs/<run-id>/`; a raiz global anterior `results/runs/` continua localizada para consultas de compatibilidade. O executor rejeita Run IDs ausentes ou ambíguos em vez de escolher um candidato.

HIST01 estabelece o padrão de reprodução controlada: contexto no README, configuração local, adaptador autorizado, notebook em modo analyze e resultados privados. HIST02 e HIST03 estabelecem o padrão de importação: o executor só encapsula um relatório legado em novo Run ID, com hash calculado na importação e lacunas de proveniência explícitas; ele não chama FHE. Configurações globais existentes permanecem durante a transição; o registro anterior apenas redireciona para a fonte ativa e não mantém uma segunda lista de experimentos.

Uma nova investigação deve criar a unidade, partir do template de notebook, declarar sua configuração, registrar o ID no catálogo único, validar e planejar antes de qualquer execução autorizada. Artefatos entre unidades são referenciados por Run ID e hash verificado. Essa regra não autoriza antecipadamente decisões científicas, novos adaptadores ou novos sistemas de orquestração.
