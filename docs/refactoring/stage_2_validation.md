# Relatório de validação — etapa 2

## Implementação

Foram criados `src/fhe_credit/experiments/` (CLI, planejador, executor, adaptadores, artefatos, erros e proveniência), a configuração e o registro do smoke sintético, e quatro módulos de teste do executor. Foram atualizados `run_manifest.py`, `configuration.py`, `.gitignore` e a documentação de refatoração.

## Evidências de segurança

- Configuração é carregada com YAML seguro e caminhos são resolvidos dentro de diretórios autorizados, inclusive contra fuga por symlink.
- O adaptador é obtido apenas do registro Python explícito; não há `eval`, `exec`, `shell=True`, importação arbitrária ou execução de script definido em YAML.
- `run` e `resume` exigem `--execute`.
- Diretórios de Run ID usam criação exclusiva; manifestos/status usam escrita atômica; lock consultivo protege retomadas concorrentes locais.
- O estado local de máquina é ignorado pelo Git. Dados, resultados e artefatos das outras frentes não foram modificados.

## Validações automatizadas

```bash
venv/bin/python -m pytest -q
venv/bin/python -m py_compile src/fhe_credit/run_manifest.py src/fhe_credit/experiments/*.py
```

Na última execução antes deste relatório, a suíte passou com **32 testes em 1,79 s**. Ela cobre o legado, YAML, planejamento sem efeitos, autorização explícita, execução sintética, análise somente leitura, adulteração, adaptador desconhecido, erro, interrupção, lock, retomada compatível/incompatível, ID de máquina, hash de código e hash do ambiente.

## Execução sintética de ponta a ponta

Foi executado pela CLI um run sintético em diretório temporário, com Run ID `run-20261127T130654159769Z-0e8f588a10824833a33590890860eddd`. O manifesto foi `COMPLETED`, continha `environment_hash` e 28 arquivos no escopo de `effective_code_hash`; `verify` retornou verdadeiro. As métricas produzidas foram: MAE `0.007719725000000021`, RMSE `0.008941704209467027`, erro absoluto máximo `0.014191900000000035` e concordância de classe `1.0`, sobre oito valores artificiais e threshold ilustrativo `0.2`.

Esses valores demonstram somente o fluxo técnico de configuração, artefatos, manifestos e verificação. Não são resultado de crédito, de FHE, de CKKS, de TFHE ou de política financeira.

O manifesto efetivo incluiu a estrutura abaixo (campos de hash completos permanecem no artefato privado da execução temporária):

```json
{
  "schema_version": "1.0",
  "run_id": "run-20261127T130654159769Z-0e8f588a10824833a33590890860eddd",
  "experiment_id": "synthetic-executor-smoke",
  "configuration_id": "cfg-synthetic-executor-smoke-v1",
  "status": "COMPLETED",
  "visibility": "PRIVATE"
}
```

## Limitações e próximos passos

- A recuperação após SIGKILL/energia não é garantida; arquivos já persistidos são preservados quando possível.
- Não existe retomada computacional para o adaptador sintético por não haver checkpoint.
- O hash de código tem escopo parcial explicitamente documentado.
- O executor ainda não adapta nem executa os scripts históricos UCI e não realiza FHE.

A próxima etapa proposta é criar adaptadores de análise dos experimentos históricos, sem mudar sua implementação ou metodologia, mediante aprovação específica.
