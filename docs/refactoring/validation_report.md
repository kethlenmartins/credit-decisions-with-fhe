# Relatório da etapa 1 — infraestrutura segura

Data: 27 de novembro de 2026.

## Arquivos criados

- `configs/schema/experiment.schema.yaml`
- `configs/experiments/historical_fhe_smoke_synthetic.yaml`
- `configs/registry/experiments.yaml`
- `src/fhe_credit/configuration.py`
- `src/fhe_credit/experiment_registry.py`
- `src/fhe_credit/run_manifest.py`
- `tests/test_configuration.py`
- `tests/test_run_manifest.py`
- `results/public/.gitkeep`
- `docs/refactoring/target_architecture.md`
- `docs/refactoring/progress.md`
- Este relatório.

## Arquivos modificados

- `.gitignore`
- `requirements-base.txt` (adição de `PyYAML>=6,<7`)

Não foram modificados scripts históricos, protocolo, auditoria de datasets, dados, resultados históricos ou artefatos CKKSML.

## Decisões técnicas

- YAML é lido com `yaml.safe_load`; nenhum campo é avaliado como código.
- A configuração é canonizada em JSON ordenado antes do SHA-256, evitando que formatação YAML mude o `config_hash`.
- O diretório de uma execução é criado com `exist_ok=False`; portanto, um `Run ID` repetido não sobrescreve resultados.
- Escritas de manifesto e status usam arquivo temporário no mesmo diretório e `os.replace`.
- O fingerprint de máquina usa somente sistema, release, arquitetura e implementação Python; hostname e nome de conta não são registrados.

## Comandos executados e resultado

```bash
PYTHONPATH=. python -m pytest -q
venv/bin/python -m pytest -q
venv/bin/python -m py_compile src/fhe_credit/configuration.py \
  src/fhe_credit/experiment_registry.py src/fhe_credit/run_manifest.py
git check-ignore -v <amostras de caminhos restritos>
git ls-files datasets ckksml data results models keys
```

O primeiro comando não pôde iniciar porque `python` não está disponível no `PATH` (saída 127). Após instalar a dependência declarada no `venv`, o segundo comando passou: **15 testes em 0,64 s**. A compilação de sintaxe não reportou erro.

`git check-ignore` confirmou proteção para `datasets/`, `ckksml/`, dados brutos e processados, resultados privados, runs, arquivos não revisados em `results/public/`, logs, chaves, modelos e checkpoints de notebooks. A listagem de rastreados exibiu somente `data/raw/.gitkeep`, `data/processed/.gitkeep` e `results/.gitkeep` nessas áreas; não identificou dados ou artefatos restritos rastreados.

## Exemplo de configuração válida

Na etapa 1, o arquivo `configs/experiments/historical_fhe_smoke_synthetic.yaml` possuía `scientific_status: HISTORICAL`, `execution.mode: analyze` e não referenciava dados reais. Na etapa 4 ele foi convertido em configuração de importação explícita de relatório legado, sem execução FHE; o estado final está em `final_validation.md`.

## Exemplo de manifesto sintético

Um manifesto criado por `build_manifest(...)` contém, entre outros, a seguinte estrutura. Os valores abaixo são ilustrativos; não representam uma execução científica realizada.

```json
{
  "schema_version": "1.0",
  "run_id": "run-20261127T000000000000Z-<uuid>",
  "experiment_id": "synthetic-test",
  "configuration_id": "synthetic-config",
  "status": "CREATED",
  "artifact_hashes": {},
  "visibility": "PRIVATE"
}
```

Os testes criam esse tipo de manifesto apenas em diretórios temporários, verificam rejeição de sobrescrita, completam uma execução sintética com um artefato obrigatório e detectam sua adulteração por hash.

## Limitações e bloqueadores

- O executor central, checkpoints de modelos e integração dos scripts históricos pertencem à etapa 2 e não foram implementados.
- `effective_code_hash` e `environment_hash` permanecem explicitamente indisponíveis no manifesto, com justificativa; commit Git não representa alterações locais.
- Nenhuma compatibilidade técnica de CKKSML foi verificada.
- Freddie Mac 2022--2024 segue pendente de aquisição e auditoria; target, features, divisão temporal e pré-processamento não foram definidos.

## Decisões que exigem aprovação

1. Autorizar a etapa 2 para implementar o executor central em modo seguro.
2. Definir, em etapa posterior, a estratégia de snapshot filtrado do código efetivo e do ambiente.
3. Aprovar separadamente qualquer migração ou adaptação dos scripts históricos.
