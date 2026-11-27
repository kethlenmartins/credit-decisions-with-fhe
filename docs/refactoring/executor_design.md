# Executor experimental central — etapa 2

## Escopo

O executor conecta registro, configuração, adaptador e manifesto sem modificar os scripts históricos. Sua única execução permitida nesta etapa é `synthetic-executor-smoke`: vetores artificiais determinísticos para testar infraestrutura. As métricas MAE, RMSE, erro máximo e concordância de classes nesse experimento não são evidência sobre crédito, Freddie Mac, TFHE, CKKS, Concrete ML ou políticas financeiras.

## Comandos

Como o projeto ainda não é instalável, use o interpretador disponível:

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments list
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments describe --experiment-id synthetic-executor-smoke
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments validate --config configs/experiments/synthetic_executor_smoke.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config configs/experiments/synthetic_executor_smoke.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments run --config configs/experiments/synthetic_executor_smoke.yaml --execute
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments analyze --run-id RUN_ID
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments status --run-id RUN_ID
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments verify --run-id RUN_ID
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments resume --run-id RUN_ID --execute
```

`run` e `resume` recusam processamento sem `--execute`. `plan`, `validate`, `list`, `describe`, `analyze`, `status` e `verify` não iniciam adaptadores. O caminho de configuração deve estar em `configs/`, corresponder ao registro e não escapar por `..` ou symlink.

## Contrato do adaptador

Um adaptador é registrado em `adapters.py` e declara identificador e `supports_computational_resume`. Ele recebe a configuração já validada e o diretório exclusivo da execução. Não recebe comandos de shell nem caminhos livres do usuário. Deve gravar somente os artefatos esperados no diretório fornecido.

O adaptador sintético não declara retomada computacional: não possui checkpoint. A retomada administrativa preserva Run ID e tentativas nos utilitários de manifesto, mas não é apresentada como retomada de computação. Um adaptador futuro só poderá habilitar `resume --execute` se implementar essa capacidade de fato.

## Ciclo de vida e falhas

Uma execução autorizada cria `results/runs/<run-id>/`, escreve configuração efetiva e ambiente, cria manifesto, entra em `RUNNING`, executa o adaptador e só entra em `COMPLETED` após hash dos artefatos obrigatórios. Falhas registram `FAILED` com tipo de erro sanitizado; `KeyboardInterrupt` registra `INTERRUPTED`. SIGKILL, falha de energia ou defeitos de sistema podem impedir a última escrita atômica e permanecem limitações documentadas.

`analyze` só lê manifestos, configuração, métricas e hashes. `verify` verifica hashes persistidos. Ambos não alteram resultados. Um lock consultivo local impede duas execuções/retomadas simultâneas para o mesmo Run ID; ele não é lock distribuído.

## Proveniência

O manifesto preserva `git_commit` e `git_dirty`. `effective_code_hash` é SHA-256 de uma representação ordenada de hashes de arquivos em `src/fhe_credit/`, `configs/` e arquivos `requirements-*.txt`. Ele exclui deliberadamente dados, resultados, chaves, ambientes, `datasets/`, `ckksml/` e tudo fora desse escopo. Portanto, não representa dependências não registradas ou componentes externos.

`environment.json` registra versões/implementação Python, plataforma, arquitetura, CPU quando disponível, núcleos, memória instalada quando disponível, configuração explícita de threads e distribuições Python instaladas. Não varre variáveis de ambiente. Seu JSON canônico gera `environment_hash`; ele identifica o ambiente observado, não substitui um lockfile reprodutível.
