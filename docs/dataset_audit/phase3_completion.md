# Fase 3 — auditoria financeira e leakage

## Cenário A: concessão retrospectiva simulada

| Conjunto | Uso | Freddie Mac | LendingClub |
|---|---|---|---|
| X | features preditivas candidatas | FICO, LTV/CLTV/DTI originais, estado e tipo de imóvel; disponibilidade operacional ainda deve ser validada | renda, DTI, FICO, emprego, propósito e características de crédito; condições contratadas exigem cautela |
| Z | contexto de políticas | UPB, taxa e prazo originais são condições históricas, não necessariamente oferta conhecida antes da decisão | valor solicitado/financiado, taxa, prazo e prestação são históricos; não assumir que são contrafactuais |
| Y | alvo | atraso 30/60/90+ e encerramento adverso documentado | `Fully Paid` versus `Charged Off`; alvo temporal é `NOT_IDENTIFIABLE` |
| W | resultados observados | saldo, recuperações, despesas, venda e perda | pagamentos, recuperações, saldo, taxas e status |

No cenário A, W e performance/servicing são pós-originação e excluídos de X. Não há rejeitados, contrafactuais nem alternativas de preço observadas.

## Cenário B: operação já originada

Variáveis de performance podem descrever monitoramento e avaliação retrospectiva, mas continuam inadequadas para prever o próprio resultado no mesmo período. Saldo atual, atraso, zero balance, pagamentos e recuperações são permitidos somente como resultados/estado temporalmente anterior ao desfecho escolhido.

## Cobertura financeira

- **PD:** estimável somente após definição de target e população elegível; não é diretamente observada.
- **EAD:** saldo mensal Freddie e `out_prncp` LendingClub são observados, mas não devem ser chamados de EAD sem alinhamento à data de default.
- **LGD/perda:** componentes de perda e recuperações Freddie são observados em certos encerramentos; LendingClub tem recuperações, mas custos e horizonte precisam ser definidos.
- **EL:** `PD × LGD × EAD` é derivável com premissas e datas coerentes; permanece exploratório.
- **Rentabilidade/RAROC/capital:** `SIMULATION_ONLY`; custos, capital e preços alternativos não estão identificados.

## Políticas

P01–P05 permanecem `PARTIALLY_EMPIRICAL`: avaliam escores e decisões retrospectivamente, sem efeito causal de aprovar. P06–P12 são `SIMULATION_ONLY`, pois dependem de preço, capital, restrições coletivas ou parâmetros não observados. A matriz em `results/dataset_audit/comparison/policy_coverage.csv` não seleciona políticas nem favorece dataset.

## Encerramento

As matrizes A/B e X/Z/Y/W encerram a Fase 3. Qualquer campo com disponibilidade pré-concessão não confirmada permanece candidato, e não feature aprovada. Não há afirmação de rentabilidade real ou underwriting válido.
