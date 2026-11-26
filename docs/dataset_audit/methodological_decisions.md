# Decisões metodológicas exploratórias

Estas decisões orientam a auditoria; não alteram nem congelam o protocolo experimental principal.

## Target e tempo

O candidato principal é a primeira ocorrência de atraso de pelo menos 90 dias em 12 meses. A referência exploratória é `First Payment Date`; o horizonte termina no mês de referência mais 12 meses. `Monthly Reporting Period` mede períodos de reporte, não deve ser substituído por contagem de linhas.

Serão comparados 30+, 60+, 90+, encerramento adverso documentado e composto documentado, nos horizontes 6/12/24/36. S01 usa classificação binária observável; S02 exclui quitações anteriores; S03 trata quitação como risco concorrente e considera Aalen–Johansen, não Kaplan–Meier com quitação censurada.

## Zero Balance Code

Fonte primária: *Single-Family Loan-Level Dataset General User Guide*, Release 48, páginas 11 e 16, arquivo local. A classificação é:

| Código | Significado oficial | Categoria exploratória |
|---|---|---|
| 01 | Prepaid or Matured (Voluntary Payoff) | PREPAYMENT |
| 02 | Third Party Sale | ADVERSE_TERMINATION |
| 03 | Short Sale or Charge Off | ADVERSE_TERMINATION |
| 09 | REO Disposition | ADVERSE_TERMINATION |
| 15 | Whole Loan Sales | REPURCHASE_OR_TRANSFER |
| 16 | Reperforming Loan Securitizations | REPURCHASE_OR_TRANSFER |
| 96 | Confirmed Underwriting Defect or Major Servicing Defect prior to credit event | ADMINISTRATIVE_CENSORING |

Código ausente ou não documentado permanece `UNKNOWN`; encerramento adverso não é automaticamente atraso de 90+ dias.

## Leakage e divisão temporal

O cenário A é simulação retrospectiva de concessão sobre operações originadas, sem rejeitados nem contrafactuais. O cenário B avalia operação já originada. Features X, contexto financeiro Z, targets Y e resultados W devem permanecer separados. Configuração temporal exploratória Freddie: 2015–17 treino, 2018 validação, 2019 teste, 2020–21 drift; rótulos só estarão disponíveis após maturação do horizonte.
