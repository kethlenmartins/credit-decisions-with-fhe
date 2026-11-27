# Experimentos orientados a investigação

Cada unidade reúne seu contexto científico, configuração, notebook e resultados privados. Código reutilizável permanece em `src/fhe_credit/`; dados não são copiados para unidades experimentais.

O registro ativo está em `experiments/registry.yaml`. As unidades históricas são `HIST01` (baseline em claro), `HIST02` (smoke sintético FHE) e `HIST03` (smoke FHE UCI); scripts numerados históricos permanecem nos caminhos originais.

Resultados ficam em `results/runs/` de cada unidade e são ignorados pelo Git. Use Run IDs explicitamente: o executor não escolhe a execução mais recente.

## Criar uma unidade futura

1. Defina um `experiment_id` estável, em minúsculas, no registro único `experiments/registry.yaml`.
2. Crie `experiments/<área>/<unidade>/` com `README.md`, `config.yaml`, `experiment.ipynb` a partir de `templates/experiment_template.ipynb` e `results/public/.gitkeep`.
3. Preserve no notebook o modo `analyze`, um Run ID explícito, proveniência, limitações e a separação entre resultados e análise derivada.
4. Declare a configuração com status, dependências, parâmetros já aprovados, entradas e classificação de publicação; valide com `validate` e planeje com `plan`.
5. Registre a unidade apontando para um adaptador explicitamente permitido. Reutilize o executor; YAML não pode escolher código arbitrário.
6. Execute somente com `--execute` quando houver autorização metodológica. Localize, verifique e analise o Run ID retornado antes de concluir.
7. Referencie artefatos de outra unidade pelo Run ID e hash verificado; não selecione a execução mais recente e não copie dados privados para o Git.
8. Documente conclusões como condicionais ao escopo, distinguindo resultado original, reprodução e análise derivada.
