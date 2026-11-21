# Dataset, obtenção e reprodutibilidade

## Fonte e escopo

- **Repositório:** UCI Machine Learning Repository.
- **Conjunto:** [Default of Credit Card Clients (id 350)](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients).
- **Tamanho obtido no teste local:** 30.000 registros, 23 variáveis de entrada, alvo `Y`.
- **População:** titulares de cartão já existentes, acompanhados historicamente; o conjunto não mede resultados de pessoas rejeitadas em uma nova concessão.

## Download

Na raiz do repositório:

```bash
python -m src.fhe_credit.download_data
```

Saídas locais:

```text
data/raw/features.csv
data/raw/target.csv
data/raw/manifest.json
```

O manifesto registra o identificador do dataset, URL de origem, data UTC, nomes das variáveis e hashes SHA-256 dos dois CSVs. Os CSVs e o manifesto são **ignorados pelo Git**.

## Reprodutibilidade entre máquinas

- Uma nova execução do downloader não é garantia de bytes idênticos: dados remotos e serialização podem variar.
- Comparar hashes e colunas entre máquinas. Para reprodução exata de longo prazo, guardar uma cópia do conjunto permitido pelos termos da fonte, num armazenamento autorizado fora do Git, associada aos hashes.
- A primeira versão da pesquisa **não inclui** dados bancários privados, faturas individuais adicionais nem dados de clientes reais de instituições parceiras.
- Não incluir PDFs de artigos de terceiros no Git sem verificação de permissões/licenças.

## Controles de qualidade ainda pendentes

Checagem de tipos, valores ausentes, duplicatas, alvo, coluna ID, distribuições, estratificação das divisões e consistência de limites monetários. Fazer as checagens com scripts versionados antes de publicar qualquer conclusão.
