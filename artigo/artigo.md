# Estabilidade Decisória sob Perturbações Numéricas na Inferência Homomórfica de Risco de Crédito

Kethlen Martins da Silva

**Resumo.** A definir.

**Palavras-chave:** A definir.

## 1. Introdução

Modelos de aprendizado de máquina são utilizados na estimativa do risco de crédito e no suporte a decisões financeiras. Entretanto, o processamento de informações sensíveis em infraestruturas externas apresenta desafios relacionados à confidencialidade dos dados.

A criptografia totalmente homomórfica (FHE) permite realizar operações sobre dados cifrados sem exigir sua decifragem pela entidade responsável pela computação. Sua aplicação à inferência de modelos preditivos pode envolver adaptações na representação numérica dos dados e das operações realizadas pelo modelo.

No contexto de crédito, as previsões produzidas por um modelo podem ser utilizadas como entradas de políticas de decisão, determinando, por exemplo, a aprovação de uma operação ou suas condições financeiras. Dessa forma, diferenças numéricas entre as previsões de um modelo convencional e de sua versão adaptada à inferência homomórfica podem resultar em decisões distintas.

Este trabalho investiga como as propriedades das políticas de decisão de crédito influenciam os efeitos das perturbações numéricas associadas à inferência homomórfica, considerando os compromissos entre estabilidade decisória, impacto econômico e eficiência computacional.

A investigação restringe-se à inferência sobre dados cifrados, mantendo o treinamento dos modelos em texto claro. Nesta etapa, a avaliação experimental concentra-se em uma árvore de decisão adaptada à biblioteca Concrete ML e em políticas de decisão por limiar.

## 2. Trabalhos relacionados

Frery et al. (2023) investigam a inferência privada de modelos baseados em árvores utilizando TFHE. O trabalho utiliza representações quantizadas e mecanismos de bootstrapping programável para realizar a avaliação homomórfica desses modelos.

Cong et al. investigam a avaliação privada de árvores de decisão sobre entradas cifradas em lote, considerando a eficiência computacional e de comunicação.

No domínio financeiro, Yılmaz et al. (2026) investigam a aplicação de criptografia homomórfica em tarefas de classificação financeira utilizando Concrete ML. Allavarpu et al. (2025) apresentam uma abordagem baseada em redes neurais e criptografia homomórfica aplicada à análise de risco de crédito.

O presente trabalho concentra-se na avaliação das decisões derivadas das previsões produzidas por modelos adaptados à inferência homomórfica.

## 3. Fundamentação

### 3.1. Inferência homomórfica e representação numérica

A criptografia homomórfica permite realizar operações sobre dados cifrados de modo que, após a decifragem, seja possível recuperar o resultado correspondente à computação realizada, conforme as propriedades do esquema utilizado.

A adaptação de modelos de aprendizado de máquina à inferência homomórfica depende das operações e representações numéricas suportadas pela implementação criptográfica.

O Concrete ML utiliza representações quantizadas para adaptar modelos preditivos à computação homomórfica baseada em TFHE. A quantização representa valores numéricos por meio de um conjunto discreto de valores, cuja granularidade depende da configuração utilizada.

Essa adaptação pode produzir diferenças entre as previsões do modelo original e aquelas obtidas pelo modelo quantizado. A análise dessas diferenças deve distinguir os efeitos da adaptação numérica daqueles associados à execução criptográfica.

### 3.2. Políticas de decisão de crédito

Um modelo preditivo de risco de crédito produz estimativas que podem ser utilizadas como entradas de políticas de decisão.

Neste trabalho, uma política de decisão é compreendida como uma regra que transforma previsões e informações contextuais em decisões financeiras.

Seja $p_i$ a previsão de risco associada à observação $i$ e $z_i$ o conjunto de informações contextuais utilizadas pela política. A decisão correspondente pode ser representada por

$$
d_i=\pi(p_i,z_i),
$$

em que $\pi$ representa a política de decisão.

Nesta etapa, considera-se uma política binária de aprovação por limiar, definida como

$$
d_i(\tau)=\mathbb{1}[p_i\leq\tau],
$$

em que $\tau$ representa o limiar de aprovação, 1 representa aprovação e 0 representa rejeição.

A política é utilizada como instrumento de análise experimental, sem representar necessariamente uma regra operacional de concessão de crédito.

### 3.3. Perturbações numéricas e estabilidade decisória

Sejam $p_i$ e $\hat{p}_i$ as previsões correspondentes do modelo de referência e do modelo adaptado à inferência homomórfica, respectivamente.

A perturbação numérica é definida como

$$
\varepsilon_i=\hat{p}_i-p_i.
$$

A magnitude das diferenças entre as previsões é avaliada por meio do erro absoluto médio (MAE):

$$
\mathrm{MAE}=
\frac{1}{N}
\sum_{i=1}^{N}|p_i-\hat{p}_i|.
$$

Para avaliar os efeitos dessas diferenças sobre as decisões, utiliza-se a taxa de discordância decisória (DDR, do inglês Decision Disagreement Rate), definida como

$$
D(\tau)=
\frac{1}{N}
\sum_{i=1}^{N}
\mathbb{1}[d_i(\tau)\neq\hat{d}_i(\tau)],
$$

em que $d_i(\tau)$ e $\hat{d}_i(\tau)$ representam as decisões obtidas a partir das previsões de referência e perturbada, respectivamente.

Uma perturbação pode alterar a decisão quando desloca a previsão de uma região decisória para outra. Assim, a estabilidade depende tanto da magnitude do erro numérico quanto da posição das previsões em relação ao limiar.

Para previsões pertencentes ao intervalo $[0,1]$, a discordância individual ocorre em um intervalo de limiares cujo comprimento é igual a $|p_i-\hat{p}_i|$. Somando esses intervalos para todas as observações, obtém-se

$$
\int_0^1D(\tau)\,d\tau=\mathrm{MAE}.
$$

Essa relação permite interpretar o erro absoluto médio como uma medida integrada de discordância decisória. Entretanto, um erro absoluto médio reduzido não determina a magnitude da discordância em um limiar específico.

## 4. Metodologia

### 4.1. Conjunto de dados

Foram utilizadas amostras anuais do Freddie Mac Single-Family Loan-Level Dataset, que disponibiliza informações de originação e acompanhamento mensal de empréstimos imobiliários.

A variável-alvo corresponde à ocorrência observada de atraso igual ou superior a 90 dias nos primeiros 12 meses após a data programada do primeiro pagamento.

Observações com acompanhamento insuficiente ou desfecho indeterminado foram excluídas conforme os critérios de elegibilidade experimental.

As variáveis preditoras utilizadas correspondem a informações disponíveis na originação dos empréstimos:

- Escore de crédito;
- Razão entre dívida e renda;
- Razão entre financiamento e valor do imóvel;
- Razão combinada entre financiamento e valor do imóvel;
- Saldo principal original;
- Prazo contratual;
- Número de mutuários.

O conjunto de teste temporal de 2021 compreende 49.916 empréstimos elegíveis, com prevalência aproximada de 0,43% para o evento investigado.


### 4.2. Modelo preditivo

Foi utilizada uma árvore de decisão implementada com a biblioteca scikit-learn, com profundidade máxima igual a três e mínimo de 100 observações por folha.

O modelo foi treinado em texto claro e posteriormente adaptado à biblioteca Concrete ML, versão 1.9.0.

A utilização do mesmo modelo treinado como referência permite avaliar as diferenças associadas à adaptação numérica sem introduzir diferenças decorrentes do treinamento de modelos independentes.

### 4.3. Configuração experimental

A avaliação distingue quatro modalidades de inferência:

1. Inferência convencional em ponto flutuante;
2. Inferência quantizada em texto claro;
3. Simulação do circuito homomórfico;
4. Inferência homomórfica real.

Inicialmente, foram avaliadas configurações de quantização entre 3 e 12 bits sobre um subconjunto de 10.000 observações.

Posteriormente, as configurações de 3, 7, 8, 9, 10 e 12 bits foram avaliadas em texto claro quantizado sobre o conjunto de teste completo.

As configurações de 9 e 10 bits também foram avaliadas mediante simulação e execução homomórfica real sobre cinco observações selecionadas de maneira determinística.

<!--
Complementar com a descrição do ambiente computacional,
dos parâmetros criptográficos e dos procedimentos de
seleção das observações utilizadas nas execuções FHE.
-->

### 4.4. Métricas de avaliação

A avaliação experimental considera quatro dimensões:

| Dimensão | Métricas |
|---|---|
| Desempenho preditivo | ROC-AUC e precisão média (AP) |
| Fidelidade numérica | MAE e preservação da ordenação |
| Estabilidade decisória | DDR e DDR máxima |
| Custo computacional | Tempo de compilação, tempo total de execução homomórfica e tamanho reportado das chaves de bootstrapping |

A estabilidade decisória também é avaliada mediante uma versão ponderada da DDR:

$$
D_w(\tau)=
\frac{
\sum_{i=1}^{N}
w_i\mathbb{1}[d_i(\tau)\neq\hat{d}_i(\tau)]
}{
\sum_{i=1}^{N}w_i
},
$$

em que $w_i$ corresponde ao saldo principal original do empréstimo associado à observação $i$.

Essa métrica permite avaliar a proporção do valor original dos empréstimos associada às decisões discordantes, sem representar diretamente perdas financeiras.

## 5. Resultados e discussão

### 5.1. Desempenho preditivo e fidelidade numérica

A Tabela 1 apresenta os resultados da inferência quantizada em texto claro sobre o conjunto de teste completo.

**Tabela 1. Desempenho preditivo e fidelidade numérica (N = 49.916).**

| Bits | ROC-AUC | AP | MAE |
|---:|---:|---:|---:|
| Referência | 0,6759 | 0,01157 | — |
| 3 | 0,5000 | 0,00431 | 0,002252 |
| 7 | 0,6203 | 0,00987 | 0,001603 |
| 8 | 0,6688 | 0,01030 | 0,000834 |
| 9 | 0,6759 | 0,01157 | 0,000738 |
| 10 | 0,6759 | 0,01157 | 0,000070 |
| 12 | 0,6759 | 0,01157 | 0,000048 |

Na configuração de 3 bits, todas as previsões assumiram valor igual a zero, eliminando a capacidade discriminatória do modelo avaliado.

Com o aumento da precisão de quantização, observou-se recuperação das métricas preditivas e redução das diferenças numéricas em relação ao modelo de referência.

As configurações de 9, 10 e 12 bits preservaram a ordenação das previsões de referência e os valores observados de ROC-AUC e precisão média.

Entretanto, mesmo entre configurações com desempenho preditivo equivalente, foram observadas diferenças na fidelidade numérica. Entre 9 e 12 bits, o erro absoluto médio apresentou redução de aproximadamente 93,5%.

### 5.2. Estabilidade decisória

A Tabela 2 apresenta a discordância decisória máxima observada sobre o domínio dos limiares para cada configuração avaliada.

**Tabela 2. Discordância decisória máxima no conjunto de teste completo.**

| Bits | DDR máxima | DDR ponderada máxima |
|---:|---:|---:|
| 3 | 100,00% | 100,00% |
| 7 | 92,97% | 94,11% |
| 8 | 72,58% | 74,77% |
| 9 | 72,58% | 74,77% |
| 10 | 72,58% | 74,77% |
| 12 | 72,58% | 74,77% |

Apesar da redução do erro absoluto médio, a discordância decisória máxima permaneceu em 72,58% nas configurações de 9, 10 e 12 bits.

A análise da estrutura da árvore identificou uma folha contendo 36.228 observações, correspondentes a aproximadamente 72,58% do conjunto de teste.

A previsão de referência associada a essa folha foi de aproximadamente 0,00100668. Na configuração de 10 bits, a previsão correspondente foi de aproximadamente 0,00097653.

Embora a diferença entre esses valores seja pequena, todas as observações desse grupo apresentam decisões distintas quando o limiar de aprovação se encontra entre as duas previsões.

Esse comportamento está associado à concentração das previsões produzidas pela árvore avaliada. A redução da magnitude da perturbação diminui a extensão do intervalo de limiares em que ocorre discordância, mas não necessariamente a quantidade de observações afetadas dentro desse intervalo.

Os resultados ilustram que a preservação da ordenação das previsões e a redução do erro absoluto médio não garantem a preservação das decisões para todos os limiares.

### 5.3. Discordância ponderada pelo valor dos empréstimos

A utilização do saldo principal original como peso permitiu avaliar a distribuição dos valores dos empréstimos entre as observações com decisões discordantes.

Nas configurações de 8, 9, 10 e 12 bits, a discordância ponderada máxima atingiu aproximadamente 74,77%, enquanto a discordância não ponderada máxima foi de 72,58%.

A diferença indica que, nos respectivos intervalos de maior discordância, a proporção do valor original dos empréstimos associada às decisões alteradas foi superior à proporção de observações afetadas.

Esses resultados não representam perdas financeiras nem alterações observadas em decisões reais de concessão. A avaliação de consequências econômicas depende da definição de políticas operacionais e de funções financeiras adequadas.

### 5.4. Execução homomórfica

Foram realizadas execuções homomórficas reais sobre cinco observações nas configurações de 9 e 10 bits.

**Tabela 3. Resultados das execuções homomórficas.**

| Bits | Compilação (s) | FHE total (s) | MAE frente à referência | MAE frente ao quantizado |
|---:|---:|---:|---:|---:|
| 9 | 3,32 | 13,82 | 0,000631 | 0 |
| 10 | 2,33 | 16,56 | 0,000078 | 0 |

Para as observações avaliadas, as previsões obtidas por simulação e execução homomórfica coincidiram com as previsões quantizadas em texto claro.

Portanto, nessas execuções, as diferenças em relação ao modelo de referência já estavam presentes nas previsões do modelo quantizado. Não foram observadas diferenças adicionais associadas à execução homomórfica.

Entre as configurações de 9 e 10 bits, observou-se redução do erro absoluto médio e aumento de aproximadamente 19,8% no tempo total da chamada de inferência homomórfica.

O tamanho reportado das chaves de bootstrapping aumentou de aproximadamente 1,00 GB para 1,90 GB.

Essas medições caracterizam as configurações e execuções realizadas. A determinação de uma relação geral entre precisão numérica e custo computacional requer experimentos adicionais.

## 6. Limitações

A avaliação experimental considera uma única árvore de decisão, uma população de teste temporal e uma implementação de inferência homomórfica.

A baixa prevalência do evento investigado limita a interpretação das métricas preditivas. Adicionalmente, o número reduzido de execuções homomórficas reais não permite caracterizar a variabilidade dos custos computacionais ou generalizar a equivalência observada entre as modalidades de inferência.

As diferenças numéricas observadas representam o efeito conjunto da adaptação do modelo ao Concrete ML. Não foram isoladas as contribuições individuais da quantização das entradas, dos parâmetros e das saídas.

Os tempos de execução homomórfica foram obtidos por meio da interface de alto nível da biblioteca, sem isolamento sistemático dos custos de geração de chaves, cifragem, avaliação homomórfica e decifragem.

A análise decisória considera políticas por limiar, sem estabelecer limiares operacionais de concessão de crédito. Os valores máximos de discordância correspondem a intervalos específicos de limiares e não representam taxas de alteração de decisões em uma operação financeira real.

Por fim, o conjunto de dados representa empréstimos historicamente originados. A avaliação não permite estabelecer efeitos causais sobre novas concessões, e o saldo principal original não corresponde necessariamente à exposição no momento da inadimplência ou à perda financeira realizada.

## 7. Conclusão e trabalhos futuros

Este trabalho investigou a relação entre perturbações numéricas e estabilidade de decisões por limiar no contexto da inferência homomórfica de risco de crédito.

Na árvore de decisão avaliada, configurações de quantização que preservaram a ordenação das previsões e as métricas preditivas apresentaram diferenças numéricas capazes de alterar decisões em intervalos específicos de limiares.

As execuções homomórficas realizadas apresentaram resultados equivalentes aos da inferência quantizada em texto claro para as observações avaliadas.

Os resultados indicam, para o modelo investigado, a importância de avaliar a estabilidade das decisões em conjunto com a fidelidade numérica, o desempenho preditivo e os custos computacionais.

Como trabalhos futuros, pretende-se ampliar a avaliação para outros modelos preditivos, implementações baseadas em CKKS e políticas de decisão de crédito, investigando os compromissos entre estabilidade decisória, impacto econômico e eficiência computacional.

## Referências

Allavarpu et al. (2025). Neural Network-Driven Privacy-Preserving Credit Risk Analysis: A Homomorphic Encryption Approach. Contemporary Mathematics. Disponível em: https://doi.org/10.37256/cm.6120255949.

Cong, K., Kang, J., Nicolas, G. e Park, J. Faster Private Decision Tree Evaluation for Batched Input from Homomorphic Encryption. [Dados bibliográficos a confirmar.]

Frery, J. et al. (2023). Privacy-Preserving Tree-Based Inference with TFHE. arXiv:2303.01254. Disponível em: https://arxiv.org/abs/2303.01254.

Freddie Mac. Single-Family Loan-Level Dataset. Disponível em: https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset.

Yılmaz et al. (2026). Homomorphic Encryption in Finance: Training and Inference on Encrypted Data with Concrete ML. Disponível em: https://doi.org/10.35414/akufemubid.1686923.