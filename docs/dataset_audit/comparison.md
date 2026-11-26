# Comparação provisória — Freddie Mac e LendingClub

## Escopo e estado

Este relatório consolida auditoria estrutural e uma primeira análise de seguimento. Não houve treinamento, benchmark FHE, seleção de features ou decisão de dataset principal. Resultados referem-se aos arquivos locais e não constituem validação de concessão real, causalidade ou rentabilidade.

## Evidência estrutural

As sete amostras Freddie Mac têm 50.000 empréstimos de originação cada. A performance contém entre 1.977.122 e 3.501.425 registros por safra; o pareamento interno por identificador não encontrou órfãos, duplicatas de ID de originação ou linhas malformadas. A cobertura mensal varia substancialmente por safra, portanto análises por horizonte não devem usar a simples ausência de evento como negativa.

O LendingClub contém 2.260.701 linhas, 151 campos e 2.260.701 IDs únicos não ausentes. O arquivo tem estados ativos, encerrados e outros: o target de resultado final usa apenas `Fully Paid` (1.076.751) e `Charged Off` (268.559). Essa seleção exclui observações não definitivas e não permite inferir default em horizonte uniforme.

## Targets e censura

Para Freddie Mac, foi avaliado o primeiro atraso de 90+ dias dentro de 6, 12, 24 e 36 meses a partir da primeira data de pagamento. No horizonte de 12 meses, a prevalência entre observações classificadas como evento/negativa foi de 0,160% (2015), 0,189% (2016), 0,440% (2017), 0,289% (2018), 3,494% (2019), 1,542% (2020) e 0,456% (2021). Zero balance foi tratado como evento concorrente agregado, não como negativo; o arquivo local não permite a separação automática entre pré-pagamento e encerramento adverso neste estágio.

O target Freddie é mais próximo de uma definição temporal, mas requer validação dos códigos e escolha explícita do estimando concorrente. O LendingClub tem um resultado final observável, mas não apresenta nesta auditoria uma data de default que permita construir com segurança os horizontes uniformes pretendidos.

## Leakage e finanças

Saldos atuais, status de atraso, pagamentos, recuperações, perdas, despesas e datas de pagamento são pós-originação e não podem integrar uma feature set de concessão. Valores financiados/originais, taxa contratual e indicadores de capacidade são candidatos, mas a disponibilidade exata antes da decisão precisa ser confirmada documentalmente. Perdas e recuperações são úteis para avaliação retrospectiva, não para uma política conhecida na originação.

## Políticas e FHE

P01–P05 são apenas parcialmente fundamentáveis nos dados observados e não validam o resultado de uma aprovação contrafactual. P06–P12 exigem premissas de preço, custo, capital e/ou capacidade; são simulações, não avaliação empírica de lucro. A adequação FHE continua pendente de profiling completo, pré-processamento congelado e smoke tests por dataset; nenhum benchmark FHE foi executado nesta auditoria.

## Recomendação

**Pendente.** Não é metodologicamente defensável pontuar ou escolher um dataset enquanto os termos de uso, a compatibilidade histórica do schema, a classificação documental de leakage e o estimando de target não estiverem confirmados. A matriz de decisão registra explicitamente notas `PENDING`, em vez de atribuir números arbitrários.
