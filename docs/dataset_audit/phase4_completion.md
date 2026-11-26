# Fase 4 — auditoria computacional

## Divisão temporal exploratória

Freddie Mac: 2015–2017 é treino candidato, 2018 validação candidata, 2019 teste candidato, e 2020–2021 são monitoramento de drift. Para um horizonte de `h` meses, um rótulo de uma safra só estaria disponível após o fim de `h`; portanto, qualquer execução futura deve aplicar embargo de maturação e não usar resultados futuros para treinar uma data hipotética anterior.

LendingClub não recebe divisão confirmatória comparável nesta auditoria: o target temporal é `NOT_IDENTIFIABLE`; resultado final não é comparável a atraso 90+ em 12 meses.

## Diagnóstico FHE e quantização

Os perfis identificaram valores especiais/extremos que exigem tratamento anterior à quantização: Freddie Mac LTV/CLTV/DTI incluem `999`; LendingClub DTI chega a `999`, e renda apresenta amplitude extrema. Esses valores não foram imputados, recortados nem normalizados nesta auditoria.

O diagnóstico 3–8 bits permanece **PENDING** até que a matriz X seja revisada e os códigos especiais tenham regra documental. Quando executado, ranges, clipping, imputação e normalização devem ser ajustados exclusivamente em 2015–2017 e congelados para 2018–2021. O erro deve separar clipping de arredondamento e não será descrito como quantização Concrete ML ou CKKSML.

## Recursos e subconjuntos

A auditoria usou leitura streaming: LendingClub foi processado em blocos de 100.000 linhas; Freddie Mac, por ZIP/safra, com checkpoints. A integridade e targets percorreram dados descompactados sem alterar os arquivos brutos. Os tempos de preparação não são estimativas de latência FHE.

Subconjuntos futuros devem ser definidos por IDs e safras, sem reamostragem que cruze treino/validação/teste. Benchmarks FHE continuam bloqueados até congelar a seleção de features, pré-processamento e target.

## Encerramento

Fase 4 encerrada para evidências disponíveis: ambiente, estratégia de memória, restrições de pré-processamento e desenho temporal foram estabelecidos. Quantização e FHE não foram executados por dependerem de gates metodológicos; esse estado é `PENDING`, não resultado negativo.
