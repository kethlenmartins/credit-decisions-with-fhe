# FHE Credit Decision: Estabilidade de decisões de crédito com criptografia homomórfica

## Descrição do projeto

Este repositório investiga como a **precisão de quantização** de modelos de risco de crédito compatíveis com **Fully Homomorphic Encryption (FHE)** influencia a **estabilidade de decisões simuladas** e o **custo computacional da inferência cifrada**.

A proposta é comparar (1) um modelo de referência em ponto flutuante, (2) um modelo quantizado em texto claro e (3) a execução homomórfica do **mesmo modelo quantizado**. As decisões são avaliadas em políticas de cutoff de risco, aprovação por capacidade e utilidade econômica simulada.

**Pergunta central:** como a precisão de quantização de modelos de risco de crédito compatíveis com FHE afeta a estabilidade das decisões de concessão simuladas e o custo computacional da inferência criptografada?

**Situação atual:** o download do UCI 350, o baseline e os testes automatizados foram executados. A árvore Concrete ML 1.9.0 também realizou inferência FHE real, primeiro em dados sintéticos e depois em uma observação predefinida do UCI 350. Nos dois smoke tests, as classes previstas coincidiram entre execução quantizada em claro, simulação e `fhe="execute"`. Isso não demonstra equivalência de probabilidades, desempenho no conjunto completo ou estabilidade decisória.

## Objetivos e escopo

- Medir a influência da quantização nas métricas preditivas e nas decisões de crédito simuladas.
- Investigar a concentração de discordâncias na vizinhança dos limiares de aprovação.
- Medir separadamente o custo de compilação, cifragem, inferência FHE e decifragem, quando possível.
- Analisar compromissos entre precisão, estabilidade da decisão e latência.

**Limites da pesquisa:** o dataset contém **clientes que já possuíam cartão** e resultados observados subsequentes, não novas solicitações com contrafactuais de aprovação. Portanto, este trabalho **não valida políticas reais de concessão nem estima efeitos causais**. A política é calculada **após** obter/decifrar os escores; não reivindicamos aprovação fim a fim cifrada.

## Autoria

- Kethlen Martins e Daniel Augusto
- Projeto acadêmico: Criptografia avançada.

Orientação e demais colaboradores: preencher quando definidos.

## Estrutura do repositório

```text
fhe-credit-decision/
├── README.md                     # Este guia
├── AGENTS.md                    # Regras de trabalho para Codex e agentes
├── artigo/                       # Conteúdo científico em Markdown
│   ├── README.md                 # Guia de escrita científica
│   ├── artigo.md                 # Manuscrito em elaboração
│   ├── trabalhos-relacionados.md # Síntese crítica da literatura
│   ├── matriz-bibliografica.csv  # Estudos, métodos, contribuição e lacunas
│   └── protocolo-experimental.md # Perguntas, hipóteses e plano de experimento
├── docs/                         # Documentação operacional
│   ├── ambiente.md               # Configuração do computador e resolução de erros
│   └── dados.md                  # Origem e rastreabilidade dos dados
├── src/fhe_credit/               # Implementação Python em inglês
│   ├── download_data.py          # Download e manifesto UCI
│   ├── experiment_results.py     # Comparação e persistência de relatórios
│   └── policies.py               # Políticas simuladas
├── experiments/                  # Experimentos numerados
│   ├── 01_baseline.py            # Árvore sem FHE
│   ├── 02_fhe_smoke.py           # Smoke test sintético: claro, simulação e FHE
│   └── 03_fhe_uci_smoke.py       # Uma observação UCI no mesmo circuito FHE
├── tests/                         # Testes automatizados
├── data/raw/                      # Dados baixados, ignorados pelo Git
├── data/processed/                # Dados tratados, ignorados pelo Git
├── results/                       # Artefatos locais, ignorados pelo Git
├── requirements-base.txt
├── requirements-fhe.txt
├── requirements-fhe-lock.txt     # Snapshot do ambiente FHE executado
├── pytest.ini
└── .gitignore
```

## Pré-requisitos

- Git, Python e `pip`, com suporte a `venv`.
- Python 3.12.3 em Linux x86_64 foi a configuração usada no primeiro smoke test FHE. Outras versões devem ser verificadas antes da execução.
- Para inferência FHE, use Linux x86_64 e Concrete ML 1.9.0. Não presuma suporte para Python 3.14 ou macOS/Apple Silicon sem uma verificação própria.
- Acesso à Internet para baixar dependências e o conjunto UCI 350.
- GitHub autenticado (HTTPS/SSH) para acessar este repositório privado.

Dependências Python:

| Ambiente | Arquivo | Conteúdo principal |
|---|---|---|
| Baseline | `requirements-base.txt` | NumPy, pandas, scikit-learn, matplotlib, pytest, ucimlrepo |
| FHE | `requirements-fhe.txt` | Concrete ML 1.9.0 |

> `requirements-fhe.txt` seleciona Concrete ML 1.9.0 e `requirements-fhe-lock.txt` registra o primeiro ambiente FHE executado. Registrar também versões e SHA-256 dos dados nas execuções UCI.

## Inicialização em um novo computador

**1. Clonar o repositório privado**

```bash
git clone git@github.com:kethlenmartins/fhe-credit-decision.git
cd fhe-credit-decision
```

Se usar HTTPS: `git clone https://github.com/kethlenmartins/fhe-credit-decision.git` (exige autenticação adequada).

**2. Criar e ativar o ambiente do baseline**

```bash
python3.12 -m venv .venv
source .venv/bin/activate   # macOS / Linux
python -m pip install --upgrade pip
python -m pip install -r requirements-base.txt
```

No Windows (PowerShell): `.venv\Scripts\Activate.ps1`. A execução FHE documentada neste projeto foi validada somente em Linux x86_64.

**3. Obter os dados de forma reproduzível**

```bash
python -m src.fhe_credit.download_data
```

O script gera `data/raw/features.csv`, `data/raw/target.csv` e `data/raw/manifest.json`, incluindo data e hashes dos arquivos. **Os CSVs não são armazenados no Git.** Veja [documentação dos dados](docs/dados.md).

**4. Executar o baseline**

```bash
PYTHONPATH=. python experiments/01_baseline.py
```

**5. Executar os testes**

```bash
python -m pytest -q
```

## Ambiente FHE reproduzido

Crie um ambiente separado para não alterar o baseline. Os comandos abaixo reproduzem a configuração usada no smoke test em Linux x86_64:

```bash
python3.12 -m venv .venv-fhe
source .venv-fhe/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-base.txt
python -m pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-fhe.txt
python -m pip install --force-reinstall --no-deps "numpy==1.26.4" "contourpy==1.3.1"
```

`requirements-fhe-lock.txt` é o snapshot das versões instaladas na execução validada. Ele é um registro do ambiente, não substitui os comandos acima, pois o PyTorch CPU usa um índice próprio.

Execute o smoke test sintético:

```bash
PYTHONPATH=. .venv-fhe/bin/python experiments/02_fhe_smoke.py
```

O comando deve terminar com `FHE execute completed` e criar `results/02_fhe_smoke.json` e `.csv`. Esses arquivos são locais e ignorados pelo Git.

Após o download UCI e sem alterar hiperparâmetros, a primeira verificação no dataset real usa uma única observação de teste predefinida:

```bash
PYTHONPATH=. .venv-fhe/bin/python experiments/03_fhe_uci_smoke.py
```

Ele compara apenas rótulos do modelo float e do modelo Concrete ML com `n_bits=3`; não mede equivalência de probabilidades, desempenho preditivo ou políticas.

> Limitação conhecida: `python -m pip check` emite um aviso de plataforma para `xgboost==1.6.2`, embora o pacote, Concrete ML e os smoke tests tenham sido importados e executados neste ambiente. Registre esse aviso ao reproduzir o experimento.

## Documentação e navegação

| O que você procura? | Onde encontrar |
|---|---|
| Pergunta, hipóteses e desenho experimental | [artigo/protocolo-experimental.md](artigo/protocolo-experimental.md) |
| Artigos lidos e sua relação com o projeto | [artigo/trabalhos-relacionados.md](artigo/trabalhos-relacionados.md) |
| Matriz comparativa e rastreabilidade bibliográfica | [artigo/matriz-bibliografica.csv](artigo/matriz-bibliografica.csv) |
| Redação científica em andamento | [artigo/artigo.md](artigo/artigo.md) |
| Instalação e continuidade em outro computador | [docs/ambiente.md](docs/ambiente.md) |
| Fonte, download e integridade dos dados | [docs/dados.md](docs/dados.md) |
| Scripts, políticas e benchmarks | `src/fhe_credit/`, `experiments/`, `tests/` |

## Metodologia resumida

1. Dividir os dados em treino/validação/teste (60/20/20, estratificados, semente 42).
2. Treinar uma árvore rasa de referência; quantizar conforme suporte do Concrete ML.
3. Comparar a referência com a execução quantizada em texto claro para isolar o efeito de quantização e treinamento.
4. Comparar o **mesmo modelo** em claro e FHE para verificar consistência criptográfica.
5. Avaliar políticas pós-inferência: cutoff, capacidade fixa e utilidade simulada.
6. Medir latência FHE em amostra documentada; não extrapolar medidas de um único dispositivo como universais.

**Atenção metodológica:** o baseline exploratório já avaliou métricas na partição de teste. Antes dos experimentos confirmatórios, será necessário congelar parâmetros e protocolo sem usar essa partição para ajustar decisões; registrar o caráter exploratório desses resultados.

## Histórico de entregas

| Versão | Entrega | Estado |
|---|---|---|
| 0.1 | Repositório, download UCI, baseline e testes de políticas | Executado localmente; evidência fornecida no desenvolvimento |
| 0.2 | Estrutura do artigo, bibliografia e guia de ambiente | Preparado para revisão/publicação |
| 0.3 | Smoke test FHE real, UCI com uma observação e snapshot do ambiente | Executado localmente |
| 0.4 | Grade de quantização, políticas e análise de sensibilidade | Planejado |
| 1.0 | Artigo e experimentos reproduzíveis | Planejado |

## Execução reproduzível por unidade experimental

O registro ativo de unidades está em [experiments/registry.yaml](experiments/registry.yaml). Para usar o interpretador local disponível, prefira `venv/bin/python`; não presuma que `python` esteja no `PATH`.

```bash
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments list
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments plan --config experiments/historical/HIST01_uci_plaintext_baseline/config.yaml
PYTHONPATH=src venv/bin/python -m fhe_credit.experiments run --config experiments/historical/HIST01_uci_plaintext_baseline/config.yaml --execute
```

O último comando requer os dados UCI locais e cria uma execução privada com `Run ID` na unidade HIST01. Para verificar uma execução, use `analyze` ou `verify` com o ID explícito. Veja [REPRODUCIBILITY.md](REPRODUCIBILITY.md) e [experiments/README.md](experiments/README.md).

Os smoke tests históricos estão organizados como HIST02 e HIST03. Seus relatórios legados podem ser importados para um Run ID novo sem executar FHE; os resultados continuam históricos e não são benchmarks. O procedimento completo para novas unidades está em [experiments/README.md](experiments/README.md).
