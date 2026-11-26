# Síntese da auditoria comparativa de datasets

## Escopo executado

A auditoria foi conduzida sem treinamento de modelos, sem compilação/inferência FHE e sem alterar arquivos brutos. Os resultados são locais em `results/dataset_audit/` e os dados permanecem fora do Git.

Foram auditados:

- Freddie Mac Single-Family Loan-Level Dataset: amostras 2015–2021, File Layout julho/2026, File Headers e General User Guide Release 48 (outubro/2026).
- LendingClub Accepted Loans: `accepted_2007_to_2018Q4.csv.gz`.

O layout Freddie de julho/2026 foi usado somente como referência operacional provisória. A contagem de campos coincidiu com as amostras históricas, mas a equivalência semântica histórica não foi confirmada.

## Inventário e integridade

- Foram calculados hashes SHA-256, tamanhos, membros ZIP e integridade de arquivos compactados.
- As sete amostras Freddie possuem 50.000 empréstimos de originação cada.
- Não foram observados IDs duplicados, linhas malformadas ou falhas referenciais internas entre originação e performance nas amostras Freddie.
- Registros mensais Freddie por safra variaram de 1.977.122 (2019) a 3.501.425 (2015).
- LendingClub: 2.260.701 registros, 151 colunas e 2.260.701 IDs não ausentes únicos; a leitura em chunks não reportou linhas inválidas.
- Lacunas internas de acompanhamento Freddie: 2015 teve 2 empréstimos com 3 meses ausentes; 2017 teve 1 empréstimo com 2 meses ausentes; demais safras não tiveram lacunas internas observadas. Lacuna não foi interpretada como ausência de evento.

## Targets, censura e eventos concorrentes

O candidato principal explorado foi a primeira ocorrência de atraso de pelo menos 90 dias em 12 meses, com `First Payment Date` como referência exploratória.

- Foram calculados cenários S01, S02 e S03_COUNTS para 6, 12, 24 e 36 meses em 2015–2021.
- S01 trata Zero Balance `01` como pré-pagamento negativo se não houve atraso grave anterior; encerramentos adversos são separados.
- S02 exclui pré-pagamentos anteriores ao horizonte para sensibilidade.
- S03_COUNTS produz contagens para riscos concorrentes; Aalen–Johansen não foi estimado.
- A prevalência S01 de atraso 90+ em 12 meses entre observações elegíveis variou de 0,160% (2015) a 3,494% (2019). Não comparar diretamente essa métrica a charge-off ao longo da vida.

Classificação documental de Zero Balance Code, com fonte no guia local Release 48:

| Código | Categoria |
|---|---|
| 01 | PREPAYMENT |
| 02, 03, 09 | ADVERSE_TERMINATION |
| 15, 16 | REPURCHASE_OR_TRANSFER |
| 96 | ADMINISTRATIVE_CENSORING |

LendingClub: o resultado final `Fully Paid` versus `Charged Off` tem 1.345.310 observações elegíveis, com 1.076.751 `Fully Paid` e 268.559 `Charged Off`. Alvos temporais em 6/12/24/36 meses foram marcados `NOT_IDENTIFIABLE`: não foi inferida data de default e `last_pymnt_d` não foi usado como substituto.

## Leakage, finanças e políticas

- Foi adotado o cenário A: simulação retrospectiva de concessão sobre operações originadas; não há rejeitados nem resultados contrafactuais.
- Também foi preservado cenário B: avaliação de operação já originada.
- Matrizes A/B separam X (features candidatas), Z (contexto de política), Y (target) e W (resultados observados).
- Saldos atuais, atraso, pagamentos, status, perdas, recuperações e despesas foram classificados como pós-originação para concessão.
- PD é estimável após congelar target; EAD/LGD/EL exigem alinhamento temporal e premissas. Lucro, RAROC e capital são `SIMULATION_ONLY`.
- P01–P05 foram classificadas como `PARTIALLY_EMPIRICAL`; P06–P12 como `SIMULATION_ONLY`.

## Computação, profiling e temporalidade

- Freddie foi processado por ZIP/safra com checkpoints; LendingClub em chunks de 100.000 linhas.
- Foram perfiladas features numéricas selecionadas: FICO, UPB, LTV, CLTV, DTI e taxa Freddie; valor, taxa, renda, DTI e FICO LendingClub.
- Foram preservados valores especiais/extremos: Freddie LTV/CLTV/DTI até `999`; LendingClub DTI até `999` e renda até 110.000.000.
- A divisão Freddie exploratória é 2015–2017 treino, 2018 validação, 2019 teste e 2020–2021 drift, com embargo igual ao horizonte do alvo.
- Quantização 3–8 bits não foi executada: requer feature set congelada, regras documentadas para códigos especiais e transforms ajustadas somente no treino. O artefato registra esse estado como pendente, sem alegar equivalência Concrete ML/CKKSML.

## Consolidação e visualizações

Foram produzidas figuras PNG/SVG de volume de performance Freddie, cobertura mensal, missingness de features perfiladas, target S01 de 12 meses e status LendingClub.

A matriz decisória é preliminar: critérios sem evidência suficiente ficaram `PENDING`; não foram atribuídas notas ou scores ponderados arbitrários. A recomendação é não selecionar dataset principal ainda.

## Pendências/bloqueios importantes

- Compatibilidade semântica histórica do schema Freddie: pendente.
- Target temporal LendingClub: `NOT_IDENTIFIABLE` com os campos/documentação disponíveis.
- Estimativa Aalen–Johansen: pendente de estimando concorrente final.
- Profiling integral de alta cardinalidade, métricas completas de quantização e benchmarks FHE: pendentes de gates metodológicos; FHE não foi executado.
- Licença/termos dos dois datasets: pendentes de confirmação local/documental.
- A auditoria Freddie local cobre somente samples oficiais anuais de 50.000 empréstimos; não usar seus eventos absolutos para penalizar a viabilidade estatística do Full Dataset. Ver `freddie_mac_sample_vs_full.md`.

## Validação

Última validação registrada:

```bash
PYTHONPATH=. venv/bin/python -m pytest -q
```

Resultado: `8 passed`.

## Artefatos de entrada recomendados

- `results/dataset_audit/artifact_index.json`
- `results/dataset_audit/freddie_mac/target_horizon_feasibility.csv`
- `results/dataset_audit/comparison/availability_matrix_ab.csv`
- `results/dataset_audit/comparison/decision_matrix.csv`
- `results/dataset_audit/lending_club/missingness_complete.csv`
