# Guia de ambiente e continuidade entre computadores

## Objetivo

Conseguir clonar o projeto e repetir o baseline sem compartilhar manualmente arquivos do ambiente virtual ou dados tratados. A etapa FHE será executada somente após confirmar compatibilidade da biblioteca na máquina escolhida.

## 1. Git e autenticação

```bash
git --version
git clone git@github.com:kethlenmartins/fhe-credit-decision.git
cd fhe-credit-decision
```

Para SSH: testar `ssh -T git@github.com`. Para HTTPS: usar o Git Credential Manager ou autenticação GitHub CLI (`gh auth login`).

**Se o trabalho local ainda não foi enviado do Mac anterior, primeiro fazer commit e `git push` nesse computador.** Arquivos ignorados pelo Git, incluindo `data/raw`, não serão copiados.

## 2. Python e ambiente virtual

Usar Python 3.11 como versão de referência inicial para reduzir discrepâncias entre máquinas. Verificar a instalação:

```bash
python3.11 --version
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-base.txt
python -m pytest -q
```

Em Windows PowerShell: `py -3.11 -m venv .venv` e `.venv\Scripts\Activate.ps1`.

**Não copiar a pasta `.venv` entre computadores.** Os binários e caminhos internos dependem da plataforma.

## 3. Dados

```bash
python -m src.fhe_credit.download_data
cat data/raw/manifest.json
PYTHONPATH=. python experiments/01_baseline.py
```

Repetir o download pode gerar hashes diferentes se a fonte, serializer ou versão do pandas mudar. Comparar os campos de `manifest.json`; não supor equivalência binária.

## 4. Instalação experimental de Concrete ML

O pacote `concrete-ml` tem dependências nativas e versões suportadas específicas de Python e plataforma. Não considerar que funciona no Python 3.14 ou em qualquer arquitetura macOS.

- Verificar a matriz de suporte e as instruções da versão escolhida no [Concrete ML](https://github.com/zama-ai/concrete-ml).
- Preferir ambiente Linux x86-64 compatível se o dispositivo local não tiver wheels disponíveis.
- Criar um ambiente virtual **separado** do baseline, quando útil: `.venv-fhe`.
- Instalar `requirements-base.txt` e depois `requirements-fhe.txt` **apenas quando a versão for validada**.
- Executar `python experiments/02_fhe_smoke.py` e registrar resultado, erros e duração.
- Após êxito, fixar versão de Concrete ML e dependências transitivas num arquivo de lock ou snapshot do ambiente.

### Primeiro smoke test: ambiente isolado

Em Linux x86-64 com Python 3.12, a configuração candidata registrada para o primeiro smoke test é `concrete-ml==1.9.0`. Ela deve ser instalada fora do ambiente `venv/` já usado no baseline:

```bash
python3 -m venv .venv-fhe
source .venv-fhe/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-base.txt
python -m pip install -r requirements-fhe.txt
PYTHONPATH=. python experiments/02_fhe_smoke.py
```

O script usa uma árvore sintética rasa, `n_bits=3`, semente 42 e compara `fhe="disable"`, `fhe="simulate"` e `fhe="execute"` sobre as mesmas duas observações. Ele só cria `results/02_fhe_smoke.json` e `.csv` depois que `fhe="execute"` termina.

O primeiro smoke test foi executado neste ambiente com Concrete ML 1.9.0. O snapshot das dependências efetivamente instaladas está em `requirements-fhe-lock.txt`.

Com os dados baixados, executar `PYTHONPATH=. .venv-fhe/bin/python experiments/03_fhe_uci_smoke.py` para uma verificação FHE de uma única observação. Esse script não substitui o benchmark planejado e não percorre a grade de quantização.

`python -m pip check` ainda emite `xgboost 1.6.2 is not supported on this platform`, embora `import xgboost` retorne a versão 1.6.2 e a execução da árvore FHE tenha sido concluída. Tratar esse aviso de validação do wheel como limitação conhecida; não o omitir ao reproduzir ou relatar o ambiente.

## 5. Diagnóstico rápido

| Sintoma | Ação inicial |
|---|---|
| `ModuleNotFoundError: No module named 'src'` | Rodar `python -m pytest -q`; conferir `pytest.ini`; no baseline usar `PYTHONPATH=.` |
| `No module named 'ucimlrepo'` | Ativar `.venv` e instalar `requirements-base.txt` |
| Falha na instalação de `concrete-ml` | Conferir `python --version`, arquitetura `uname -m`, sistema e versão do pacote; considerar Linux compatível |
| `data/raw/features.csv` ausente | Reexecutar o downloader da UCI |
| `git status` mostra CSV ou segredos | Revisar `.gitignore` e não executar `git add -f` para dados/segredos |

## 6. Registro mínimo por experimento

Registrar: data/hora UTC, commit Git, versão Python, dependências instaladas (`python -m pip freeze`), CPU/arquitetura, sistema operacional, semente, ID/hash dos dados, configuração de bits, tempo de compilação e inferência. Salvar relatórios locais em `results/` e incorporar apenas tabelas/gráficos selecionados e não sensíveis quando a metodologia estiver congelada.

## 7. Flujo recomendado de trabalho

```bash
git pull --ff-only
python -m pytest -q
# trabalhar / salvar alterações
git status
git add README.md artigo/ docs/ pytest.ini
git commit -m "docs: organizar artigo e guia de ambiente"
git push
```

Usar branches por experimento se mais de uma pessoa ou máquina estiver trabalhando simultaneamente; antes de mudar de computador, conferir `git status` limpo e `git push` concluído.
