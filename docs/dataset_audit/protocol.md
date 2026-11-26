# Protocolo operacional da auditoria de datasets

Esta auditoria é exploratória e não altera o protocolo experimental principal, não treina modelos e não executa FHE. Os arquivos brutos são lidos somente em modo streaming.

## Fontes locais inspecionadas

- Freddie Mac: amostras anuais de 2015 a 2021, layout XLSX, cabeçalhos ZIP e `user_guide.pdf` (Release 48, outubro de 2026).
- LendingClub: `accepted_2007_to_2018Q4.csv.gz`.

O acesso local não constitui autorização de redistribuição. O guia do Freddie Mac declara que o uso está sujeito aos seus termos; como os termos não acompanham os arquivos, a situação de licença permanece pendente de confirmação. Não foi localizada documentação de termos do LendingClub junto ao arquivo.

## Execução

```bash
PYTHONPATH=. venv/bin/python experiments/dataset_audit/run_audit.py
```

As saídas agregadas são locais em `results/dataset_audit/`, já cobertas por `.gitignore`. A execução pode ser demorada: os arquivos Freddie Mac somam múltiplos gigabytes após descompressão e o LendingClub é lido em blocos de 100.000 linhas.

Para executar ou retomar uma safra individual do Freddie Mac, use `--freddie-year 2019 --skip-lending`. A cada safra concluída, três CSVs são persistidos em `results/dataset_audit/freddie_mac/checkpoints/`. Para executar somente LendingClub, use `--lending-only`.

## Limites metodológicos

O layout oficial disponível é de julho de 2026; por decisão metodológica registrada, ele será usado como **referência operacional provisória** para as amostras de 2015–2021, pois é o único layout publicado disponível localmente. A coincidência do número de campos é uma checagem estrutural, não prova de semântica histórica. A classificação de leakage inicial é conservadora e precisa de validação variável a variável antes de qualquer modelagem.
