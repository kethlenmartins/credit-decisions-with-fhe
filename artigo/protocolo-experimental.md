# Protocolo experimental — versão 0.2 (proposta)

## Problema

A inferência criptografada com FHE demanda representações numéricas e implementações compatíveis com o criptossistema. Em modelos de risco, a degradação da previsão não é a única preocupação: pequenas variações nos escores podem mudar decisões discretas, especialmente perto de um limite de aprovação.

## Pergunta principal

**Como a precisão de quantização de modelos de risco de crédito compatíveis com FHE afeta a estabilidade de decisões de crédito simuladas e o custo computacional da inferência criptografada?**

## Perguntas secundárias

- **RQ1:** Como a precisão de quantização altera discriminação, calibração e os escores obtidos?
- **RQ2:** Qual a sensibilidade de diferentes políticas de crédito às divergências de escores?
- **RQ3:** Em que medida as discordâncias se concentram perto dos limites de decisão?
- **RQ4:** Qual o compromisso entre estabilidade da decisão e latência de execução FHE?

## Hipóteses a testar, sem pressupor confirmação

- **H1:** Reduções da precisão podem modificar decisões mesmo com variações pequenas de AUC.
- **H2:** Ocorrem maiores taxas de discordância para observações próximas ao cutoff escolhido.
- **H3:** Existe uma relação mensurável entre bits, custo de inferência FHE e estabilidade das decisões, que pode gerar configurações não dominadas.

## Dados e população observável

- **Fonte:** [UCI Default of Credit Card Clients, id 350](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients).
- **Unidade de observação:** clientes que já possuíam cartão de crédito; a variável resposta é inadimplência no período definido no dataset.
- **Tamanho inicial observado:** 30.000 registros, 23 variáveis preditoras.
- **Limites:** dados históricos de clientes existentes, sem rejeitados e sem contrafactuais; valores monetários e limite são específicos da população de origem; **não há identificação de lucro real de novas concessões**.

## Desenho

- Divisão estratificada: 60% treino, 20% validação e 20% teste; semente 42 inicialmente.
- Controle de vazamento: transformações e imputação ajustadas **somente** no treino; thresholds e calibração escolhidos **somente** na validação.
- Modelo de referência: `DecisionTreeClassifier` raso (baseline atual: `max_depth=3`, `min_samples_leaf=100`, `random_state=42`).
- Precisões candidatas: 3, 4, 5, 6 e 7 bits, sujeitas ao compilador e a limites de execução.
- Três estágios: **FP32 referência → quantizado claro → mesmo quantizado com FHE**.
- Se o framework treinar árvores diferentes em cada bitwidth, essa variação compõe o **efeito do pipeline de quantização + treinamento**; não será tratada como erro produzido somente pelo ato de cifrar.
- Verificar existência, formato e calibração de escores antes de tratá-los como PD.
- Medir FHE em amostra pequena predefinida, estratificada por risco e proximidade dos cutoffs, sem alegar latência para todo o dataset.

## Políticas de crédito simuladas

### A — Cutoff de escore

Aprovar se `score_i <= tau`. Valores candidatos: `tau=0.10`, `0.20` e `0.30`; seleção final ou inclusão de outros valores definida **na validação**. Não tratar cutoff como regra bancária observada.

### B — Fração fixa de aprovação

Aprovar os 20%, 40% e 60% com menores escores. Definir regra determinística de desempate. Trata-se de uma política **offline de carteira**, que depende de ordenar a população; não é decisão isolada por cliente sob FHE.

### C — Utilidade financeira hipotética

Para exposição `EAD_i`, taxa de receita condicional `r`, LGD e custo operacional `c_i`:

`U_i = EAD_i * ((1 - score_i) * r - score_i * LGD) - c_i`

Aprovar quando `U_i > 0`, com parâmetros econômicos ilustrativos **declarados previamente** e sensibilidade a cenários. `LIMIT_BAL` é um limite histórico, não o principal de um novo empréstimo; não se pode interpretar `U_i` como lucro efetivo. Distinguir avaliação com escores preditos de avaliação retrospectiva que utiliza o desfecho observado.

## Métricas

- **Predição:** ROC-AUC, PR-AUC/AP, Brier score e avaliação de calibração.
- **Decisão:** discordância FP32 versus quantizado, aprovação, taxa de default observada entre aprovados, divergência por faixas de distância a `tau`.
- **Criptografia:** equivalência quantizado claro versus FHE (dentro das garantias escolhidas), latência, tempo de compilação, cifragem, decifragem e uso de memória quando disponível.
- **Incerteza:** intervalos de confiança via bootstrap sobre a amostra de teste, respeitando o pareamento das predições por cliente.

## Gates de execução

1. Download reproduzível e baseline com testes — **realizado localmente em execução anterior**.
2. Ambiente Concrete ML compatível — **executado localmente**: Linux x86-64, Python 3.12.3 e Concrete ML 1.9.0.
3. Uma inferência FHE real de árvore rasa que corresponde ao resultado quantizado — **executado localmente no smoke test sintético**: duas classes previstas em `n_bits=3` coincidiram entre claro, simulação e `fhe="execute"`.
4. Comparação clara em 3–7 bits — **dependente do gate 3**.
5. Estudo de políticas e síntese — **dependente dos anteriores**.

## Implementação do smoke test FHE

O experimento `experiments/02_fhe_smoke.py` foi estruturado para usar uma árvore sintética rasa com `n_bits=3` e semente 42. Após compilação, ele compara as mesmas observações nas modalidades quantizada clara (`fhe="disable"`), simulada (`fhe="simulate"`) e cifrada (`fhe="execute"`). A saída registrada é a classe de `predict`; ela não é probabilidade nem PD calibrada.

Os tempos são medidos com `time.perf_counter()` para treinamento, compilação, predição clara, simulação e a chamada FHE completa. A API de alto nível usada não separa, neste script, geração de chaves, cifragem, avaliação e decifragem; esses campos devem permanecer como não mensurados até uma instrumentação de API de baixo nível validada.

Os arquivos JSON/CSV locais só são persistidos após retorno bem-sucedido de `fhe="execute"`. O primeiro registro local foi produzido para duas observações sintéticas; ele valida apenas a equivalência de classes desse smoke test e não substitui a avaliação no UCI 350 nem estabelece equivalência de probabilidades.

Após o smoke test sintético, `experiments/03_fhe_uci_smoke.py` executou uma única observação de teste predefinida do UCI 350, com divisão 18.000/6.000/6.000 e `n_bits=3`. As classes do modelo Concrete ML em claro, simulação e FHE coincidiram nessa observação. A classe do baseline float também coincidiu nesse caso, mas isso não demonstra equivalência entre os modelos nem deve ser usado para escolher configurações. Os tempos desse único caso são artefatos locais; não representam benchmark de lote ou do conjunto de teste.

## Riscos de validade

- O conjunto de teste já foi consultado no baseline exploratório; **não ajustar** hipóteses/limiares com base em seus resultados. Se as decisões metodológicas forem alteradas após ver o teste, rotular explicitamente como análise exploratória.
- A saída de uma árvore `predict_proba` pode ser frequência de folha e **não** PD calibrada.
- A quantização pode mudar o modelo treinado, não apenas seus parâmetros representados.
- Custo FHE varia com compilação, hardware e versão do Concrete ML; não generalizar benchmarks sem relatá-los.
- O estudo avalia **inferência cifrada**, não treinamento cifrado, confidencialidade de pesos, conformidade regulatória ou política real de underwriting.
