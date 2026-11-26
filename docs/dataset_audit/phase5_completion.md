# Fase 5 — consolidação

## Figuras produzidas

As figuras de volume e cobertura mensal Freddie Mac são produzidas exclusivamente das contagens auditadas. Não foram geradas figuras para targets LendingClub temporais, perdas comparáveis ou drift integral, pois esses elementos não são identificáveis ou permanecem pendentes.

## Matriz multicritério preliminar

A matriz em `results/dataset_audit/comparison/decision_matrix.csv` mantém `PENDING` para todos os critérios sem evidência suficiente. Em particular, a pontuação depende de licença, target final/eventos concorrentes, política selecionada e validação de pré-processamento/FHE. Tratar pendente como zero ou cinco distorceria a decisão; portanto, não há pontuação ponderada nem recomendação numérica.

## Sensibilidade

Análise de sensibilidade quantitativa é `PENDING`: sem notas defensáveis, alterar pesos apenas produziria precisão espúria. A sensibilidade qualitativa é clara: aumentar peso de definição temporal de target favorece investigar Freddie Mac; aumentar peso de simplicidade de resultado final torna LendingClub candidato, mas sem torná-lo comparável ao target Freddie.

## Recomendação

Não escolher dataset principal. Freddie Mac possui seguimento mensal e target temporal explorável, mas eventos concorrentes e schema histórico ainda requerem validação. LendingClub possui resultado final e variáveis de empréstimo, mas não target temporal identificável nesta auditoria. A escolha deve ocorrer após resolver os gates documentados, não por contagem de políticas possíveis.
