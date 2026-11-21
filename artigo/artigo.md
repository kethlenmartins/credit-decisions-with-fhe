# Estabilidade decisória e custos computacionais na inferência de risco de crédito com criptografia totalmente homomórfica

Autora: Kethlen Martins da Silva

## 1. Introdução

Modelos de aprendizado de máquina podem estimar risco de inadimplência a partir de históricos de pagamento e informações financeiras. Esses scores podem apoiar a concessão de crédito, a definição de limites e o acompanhamento de carteiras. O uso desses dados, porém, cria um problema de confidencialidade: o provedor que executa a inferência pode ter acesso a informações sensíveis dos clientes de instituições financeiras.

Criptografia convencional protege dados em repouso e em trânsito, mas não resolve esse problema durante o processamento. Em uma arquitetura usual, o dado precisa estar em texto claro no ambiente que executa o modelo. A criptografia totalmente homomórfica (*Fully Homomorphic Encryption*, FHE) permite avaliar operações sobre dados cifrados, e o resultado só é recuperado após a decifragem. Essa propriedade interessa quando a instituição pretende usar infraestrutura externa sem entregar os dados brutos ao provedor.

O ganho de confidencialidade tem custo. A inferência FHE é mais lenta que a inferência convencional e os circuitos aceitam representações numéricas restritas. Os modelos precisam, portanto, ser adaptados. Uma adaptação frequente é a quantização, que converte valores de maior precisão em valores discretos com número limitado de bits.

Em risco de crédito, não basta comparar métricas agregadas. Uma pequena alteração no score pode mudar a decisão de um cliente próximo ao limiar de aprovação. Duas configurações podem, assim, apresentar métricas semelhantes e aprovar conjuntos diferentes de clientes. Neste trabalho, estabilidade decisória é o grau de concordância entre decisões produzidas por configurações diferentes do mesmo pipeline.

Estudos anteriores já mostraram inferência criptografada com árvores e redes neurais. Este trabalho examina como a precisão numérica afeta previsões, decisões simuladas e custo computacional em modelos de risco de crédito compatíveis com FHE.

### 1.1. Problema e pergunta de pesquisa

O problema é escolher configurações de inferência criptografada que preservem a confidencialidade, mantenham decisões estáveis e tenham custo computacional viável.

A pergunta central da pesquisa é:

**Como a precisão de quantização de modelos de risco de crédito compatíveis com criptografia totalmente homomórfica afeta a estabilidade das decisões de concessão e o custo computacional da inferência criptografada?**

Para responder a essa pergunta, foram definidas quatro questões de pesquisa:

- **QP1:** Como diferentes precisões de quantização afetam o desempenho preditivo, a calibração e a consistência das previsões?
- **QP2:** Como diferentes políticas simuladas de aprovação de crédito influenciam a discordância decisória entre configurações do modelo?
- **QP3:** Qual é o custo computacional da inferência criptografada em comparação com a execução quantizada em claro?
- **QP4:** Quais configurações apresentam compromissos mais favoráveis entre precisão numérica, estabilidade decisória e custo computacional?

### 1.2. Hipóteses

A pesquisa foi organizada em torno de três hipóteses:

**H1: sensibilidade decisória à quantização.** A redução da precisão numérica pode modificar decisões simuladas de crédito mesmo quando as diferenças nas métricas agregadas de classificação são pequenas.

**H2: concentração das discordâncias nas fronteiras de decisão.** As divergências entre decisões produzidas por diferentes configurações tendem a se concentrar em observações cujas estimativas de risco estão próximas dos limiares estabelecidos pelas políticas de aprovação.

**H3: compromisso entre estabilidade e custo computacional.** Diferentes configurações de quantização apresentam compromissos entre fidelidade preditiva, estabilidade decisória e latência de inferência FHE, possibilitando a identificação de alternativas com características distintas de custo e desempenho.

Essas hipóteses serão avaliadas em etapas experimentais posteriores. A primeira etapa, apresentada neste artigo parcial, concentra-se na preparação da infraestrutura, na implementação do modelo de referência e na validação inicial da inferência criptografada.

### 1.3. Objetivos

O objetivo geral é medir como a precisão numérica afeta a estabilidade de decisões simuladas de crédito e o custo de modelos executados com FHE. Para isso, o estudo prepara um ambiente reproduzível, implementa modelos compatíveis com FHE e compara inferência convencional, quantizada e cifrada.

A contribuição pretendida é relacionar propriedades do pipeline de inferência às decisões derivadas dos scores. É importante notar que o estudo não pretende demonstrar uma política bancária real.

## 2. Trabalhos relacionados

A literatura sobre aprendizado de máquina com preservação de privacidade apresenta diferentes abordagens para a execução de modelos sobre informações sensíveis. Entre elas, a criptografia homomórfica destaca-se pela possibilidade de realizar operações diretamente sobre dados cifrados. Os trabalhos selecionados nesta revisão abordam fundamentos arquiteturais, inferência protegida com árvores de decisão, otimizações computacionais e aplicações financeiras.

Frery et al. (2023), em *Privacy-Preserving Tree-Based Inference with TFHE*, apresentam uma abordagem para inferência privada de modelos baseados em árvores utilizando o esquema criptográfico TFHE. O método explora representações inteiras quantizadas e o mecanismo de *programmable bootstrapping* para viabilizar a avaliação de árvores de decisão, florestas aleatórias e modelos de *gradient boosting* sobre dados cifrados. Os autores analisam a relação entre precisão numérica, desempenho preditivo e latência, demonstrando que a escolha da quantização constitui uma variável importante para a eficiência do processamento. O trabalho fornece a principal fundamentação técnica para a utilização de árvores no presente estudo, além de evidenciar a necessidade de avaliar conjuntamente fidelidade preditiva e custo criptográfico. Entretanto, seu foco está na implementação e no desempenho dos modelos, e não especificamente nas consequências das diferenças preditivas para políticas de concessão de crédito.

Yılmaz et al. (2026), em *Homomorphic Encryption in Finance: Training and Inference on Encrypted Data with Concrete ML*, investigam o emprego de Concrete ML em aplicações de análise financeira. Os autores utilizam modelos de Random Forest e XGBoost em tarefas relacionadas a indicadores de dificuldades financeiras, incluindo Altman Z-Score, L-Score e Zmijewski Score. Os experimentos comparam desempenho preditivo e tempos computacionais de implementações convencionais e protegidas, identificando custos elevados de inferência criptografada e diferenças de desempenho associadas às configurações utilizadas. Apesar de o título mencionar treinamento sobre dados cifrados, a descrição metodológica apresenta modelos treinados sobre dados abertos e inferência criptografada, distinção importante para delimitar o escopo técnico da abordagem. O estudo demonstra a relevância de FHE no domínio financeiro, mas não investiga diretamente a estabilidade de decisões individuais produzidas a partir de limiares de risco.

Cong et al., em *Faster Private Decision Tree Evaluation for Batched Input from Homomorphic Encryption*, propõem protocolos para avaliação privada e não interativa de árvores de decisão sobre lotes de entradas cifradas. O trabalho introduz estratégias de comparação entre valores cifrados e limiares em texto claro, incluindo comparadores baseados em *range cover* e representações de peso constante. Os autores também propõem uma adaptação do procedimento de percurso da árvore, buscando reduzir custos de comunicação e processamento. Seus resultados demonstram ganhos de eficiência em cenários de avaliação em lote, evidenciando que a organização do circuito e das operações criptográficas influencia significativamente a escalabilidade. Embora a implementação não constitua uma comparação direta com o pipeline Concrete ML adotado nesta pesquisa, o trabalho contribui para compreender possíveis estratégias futuras de otimização e os limites de extrapolar resultados de uma única inferência para cenários de produção.

Allavarpu, Naresh e Mohan (2025), em *Neural Network-Driven Privacy-Preserving Credit Risk Analysis: A Homomorphic Encryption Approach*, investigam uma arquitetura de análise de risco de crédito com preservação de privacidade baseada em redes neurais e criptografia homomórfica. A implementação utiliza bibliotecas como TenSEAL e PyTorch para realizar processamento protegido de informações financeiras. O estudo apresenta experimentos com conjuntos de dados de crédito de diferentes origens e discute o desempenho dos modelos em condições convencionais e criptografadas. Sua principal contribuição para esta pesquisa é demonstrar que a aplicação de criptografia homomórfica à análise de risco de crédito já constitui uma linha de investigação existente. Dessa forma, a contribuição pretendida pelo presente trabalho deve ser delimitada não como a introdução inédita de FHE no domínio de crédito, mas como uma análise específica da relação entre quantização, estabilidade das decisões simuladas e custo computacional.

Shukla, Pandya e Samanth (2026), em *Fully Homomorphic Encryption and Artificial Intelligence: A Review of Architectures, Optimizations, and Distributed Privacy*, apresentam uma revisão das arquiteturas e técnicas de otimização utilizadas na integração entre FHE e inteligência artificial. Os autores discutem limitações relacionadas à latência, expansão dos dados cifrados e utilização de recursos computacionais, além de examinar estratégias de aceleração por hardware, processamento em lote e integração com sistemas distribuídos. A revisão também distingue a inferência sobre dados cifrados do treinamento homomórfico, ressaltando que essas tarefas apresentam requisitos computacionais diferentes. O trabalho contribui para a fundamentação conceitual e para a delimitação do escopo desta pesquisa, que se concentra na inferência criptografada de modelos previamente treinados, sem propor treinamento integralmente homomórfico.

### 2.1. Síntese dos trabalhos relacionados

Os estudos analisados demonstram avanços relevantes na viabilização da inferência criptografada e na redução de seus custos computacionais. Frery et al. (2023) e Cong et al. contribuem diretamente para a compreensão de mecanismos de avaliação privada de árvores, enquanto Yılmaz et al. (2026) e Allavarpu et al. (2025) evidenciam aplicações financeiras de modelos protegidos por criptografia homomórfica. Shukla et al. (2026), por sua vez, sistematizam desafios arquiteturais e oportunidades de otimização.

Em conjunto, esses trabalhos sustentam a viabilidade técnica da abordagem proposta, mas apresentam ênfases distintas. Parte da literatura concentra-se em fidelidade preditiva, tempo de execução ou eficiência criptográfica; outra parte demonstra aplicações de aprendizado de máquina protegido em problemas financeiros. A presente pesquisa propõe integrar essas perspectivas por meio de uma avaliação que considere também as decisões derivadas das previsões. A lacuna investigada é, portanto, a relação entre escolhas de precisão numérica, discordância em políticas simuladas de crédito e custo computacional da inferência FHE, sem pressupor que essa relação esteja inteiramente ausente da literatura.

### 2.2. Quadro comparativo

| Trabalho | Abordagem | Contexto experimental | Principal contribuição | Relação com a presente pesquisa |
|---|---|---|---|---|
| Frery et al. (2023) | TFHE e árvores quantizadas | Classificação com árvores, florestas e boosting | Inferência privada baseada em árvores e análise de precisão/latência | Fundamenta o modelo e a variação de `n_bits` |
| Yılmaz et al. (2026) | Concrete ML, Random Forest e XGBoost | Indicadores de dificuldades financeiras | Avaliação de desempenho e custo da inferência protegida em finanças | Referência de aplicação financeira e comparação computacional |
| Cong et al. | HE e avaliação de árvores em lote | Inferência privada não interativa | Otimizações de comparação, percurso e comunicação | Fundamenta discussões de escalabilidade |
| Allavarpu et al. (2025) | Redes neurais, TenSEAL e PyTorch | Análise de risco de crédito | Aplicação de inferência protegida ao domínio de crédito | Delimita a contribuição específica do estudo |
| Shukla et al. (2026) | Revisão de arquiteturas FHE e IA | Diferentes aplicações e técnicas | Sistematização de limitações e otimizações | Fundamenta escolhas arquiteturais e limitações |

## 3. Metodologia

A pesquisa é experimental e quantitativa. A primeira etapa preparou o ambiente, selecionou o conjunto de dados, implementou o modelo de referência e verificou a inferência FHE com Concrete ML. O projeto usa Python, código modular, scripts experimentais e testes automatizados; dados brutos e resultados gerados ficam fora do versionamento.

### 3.1. Ambiente computacional e dependências

A implementação foi realizada em um computador com sistema operacional Linux, arquitetura x86_64 e processador Intel Core i5-1335U, utilizando Python 3.12.3.

Foram utilizadas bibliotecas de manipulação de dados e aprendizado de máquina, incluindo NumPy, pandas e scikit-learn. A obtenção dos dados foi realizada com `ucimlrepo`, enquanto a implementação de inferência criptografada utilizou Concrete ML 1.9.0.

A configuração registrada para a primeira execução FHE incluiu NumPy 1.26.4 e scikit-learn 1.5.0. As dependências foram organizadas em arquivos de requisitos, com um ambiente virtual específico para a execução dos experimentos criptográficos.

Durante a preparação, foi identificado um aviso de compatibilidade relacionado ao pacote XGBoost 1.6.2 na verificação de dependências. Apesar desse aviso, a importação das bibliotecas e as execuções iniciais com Concrete ML foram concluídas. A ocorrência foi documentada como uma limitação do ambiente, sem assumir que o aviso não possa afetar outras configurações experimentais.

### 3.2. Seleção e preparação do conjunto de dados

Foi selecionado o conjunto de dados *Default of Credit Card Clients*, disponibilizado pelo UCI Machine Learning Repository sob o identificador 350. O conjunto contém 30.000 observações e 23 variáveis preditoras, relacionadas a características e ao histórico financeiro de clientes de cartão de crédito.

A variável-alvo indica a ocorrência de inadimplência no mês seguinte, caracterizando uma tarefa de classificação binária.

A escolha se deve ao uso recorrente do conjunto em previsão de inadimplência, às variáveis tabulares e ao download reproduzível a partir de fonte pública.

O script de download registra proveniência e hashes SHA-256. Esses metadados identificam os arquivos usados em cada execução.

As observações foram divididas de maneira estratificada em três subconjuntos, utilizando semente aleatória 42:

| Subconjunto | Proporção | Observações |
|---|---:|---:|
| Treinamento | 60% | 18.000 |
| Validação | 20% | 6.000 |
| Teste | 20% | 6.000 |
| **Total** | **100%** | **30.000** |

O conjunto de treinamento foi destinado ao ajuste dos modelos, enquanto a validação foi reservada para escolhas metodológicas e de configuração. O conjunto de teste foi utilizado nas verificações exploratórias iniciais, fato que será considerado nas etapas posteriores para evitar seleção de parâmetros orientada pelos resultados de teste.

É importante observar que o conjunto representa clientes que já possuem cartão de crédito. Consequentemente, futuras regras de aprovação implementadas nesta pesquisa deverão ser interpretadas como políticas simuladas sobre uma população histórica, e não como avaliações causais de concessão de crédito a novos solicitantes.

### 3.3. Modelo de referência

Como referência inicial, foi implementado um classificador baseado em árvore de decisão, utilizando `DecisionTreeClassifier` da biblioteca scikit-learn.

A configuração exploratória adotou profundidade máxima igual a três e número mínimo de 100 observações por folha. A escolha de uma árvore rasa buscou estabelecer um modelo de complexidade controlada, adequado à etapa inicial de desenvolvimento e à posterior comparação com implementações compatíveis com FHE.

O modelo foi avaliado utilizando métricas de classificação binária: área sob a curva ROC (*ROC-AUC*), precisão média (*Average Precision*) e Brier Score. Também foi calculada, de maneira exploratória, a proporção de observações aprovadas por uma política hipotética baseada em limiar de probabilidade de inadimplência de 0,20.

A avaliação inicial teve caráter exploratório e não foi utilizada como evidência de superioridade do modelo ou de adequação financeira da política simulada.

### 3.4. Implementação da inferência homomórfica

Para validar a viabilidade da inferência criptografada, foi utilizada a biblioteca Concrete ML, que permite construir modelos de aprendizado de máquina compatíveis com operações homomórficas.

O procedimento inicial foi organizado em duas verificações.

A primeira consistiu em um *smoke test* com dados sintéticos, utilizando uma árvore de decisão pequena. O objetivo foi verificar o funcionamento do pipeline de treinamento, compilação e inferência, sem depender inicialmente da complexidade do conjunto de dados financeiro.

A segunda verificação utilizou o UCI 350, mantendo a divisão previamente definida e adotando uma configuração Concrete ML com `n_bits=3`. O experimento selecionou uma observação de teste predefinida para verificar a execução do modelo em três modalidades:

- **Execução quantizada em claro (`fhe="disable"`):** inferência do modelo Concrete ML sem criptografia.
- **Simulação FHE (`fhe="simulate"`):** execução simulada do circuito compilado.
- **Execução FHE real (`fhe="execute"`):** inferência com operações efetivamente realizadas sobre dados cifrados.

A comparação das saídas teve como objetivo verificar se as modalidades produziam a mesma classe para as observações selecionadas.

A implementação também contemplou a persistência de resultados experimentais em arquivos JSON e CSV, contendo informações sobre a configuração, as saídas comparadas e os tempos de execução.

### 3.5. Medição de desempenho computacional

Foram instrumentadas medições de tempo para treinamento, compilação, inferência quantizada em claro, simulação FHE e inferência FHE real.

As medições de inferência foram obtidas por meio da API de alto nível do Concrete ML. Dessa forma, o tempo associado à execução FHE representa o tempo total observado para a chamada de predição criptografada, não sendo possível, nessa implementação inicial, separar os custos de geração de chaves, cifragem, avaliação homomórfica e decifragem.

Os tempos foram registrados em segundos. Como os resultados iniciais correspondem a execuções isoladas, não foram calculados intervalos de confiança ou medidas de dispersão.

### 3.6. Validação e testes

Foram implementados testes automatizados para verificar o funcionamento das políticas simuladas de crédito e das funções auxiliares de comparação e persistência de resultados.

A validação também incluiu verificações de sintaxe e consistência dos arquivos de código. Ao final da primeira etapa, sete testes automatizados foram executados com sucesso.

A validação do pipeline criptográfico foi realizada adicionalmente por meio das execuções reais dos scripts experimentais, distinguindo testes unitários de evidências de funcionamento da inferência FHE.

## 4. Resultados iniciais

Esta seção apresenta os resultados obtidos durante a primeira etapa de desenvolvimento. Os experimentos realizados tiveram como objetivo verificar a viabilidade técnica da abordagem e estabelecer valores de referência para as etapas seguintes.

Os resultados ainda não constituem uma avaliação sistemática dos efeitos da quantização sobre o comportamento decisório.

### 4.1. Desempenho do modelo convencional

A primeira execução do modelo de referência sobre o UCI 350 produziu os resultados apresentados na Tabela 3.

**Tabela 3 — Resultados exploratórios do modelo de referência**

| Métrica | Resultado |
|---|---:|
| ROC-AUC | 0,7382 |
| Average Precision | 0,4799 |
| Brier Score | 0,1379 |
| Taxa de aprovação simulada com limiar 0,20 | 82,12% |

A ROC-AUC de 0,7382 indica discriminação acima do acaso. A Average Precision de 0,4799 complementa essa leitura para a classe positiva.

O Brier Score foi 0,1379. Isoladamente, ele não descreve toda a calibração do modelo.

A taxa de aprovação simulada foi 82,12% para o limiar 0,20. Não é uma recomendação de política: o estudo não avaliou custos, regulação ou resultados econômicos reais.

### 4.2. Validação da inferência FHE com dados sintéticos

O primeiro experimento criptográfico utilizou uma árvore de decisão treinada sobre dados sintéticos e avaliou duas observações.

As três modalidades de execução — quantizada em claro, simulação FHE e inferência FHE real — produziram classes idênticas para as duas observações avaliadas.

O teste confirma o funcionamento inicial de compilação e inferência FHE no ambiente usado. Duas entradas não demonstram equivalência geral nem estimam divergências em conjuntos maiores.

### 4.3. Validação da inferência FHE no UCI 350

Após a validação sintética, foi executado um experimento com o conjunto de dados financeiro, utilizando uma árvore Concrete ML com precisão `n_bits=3`.

O experimento considerou uma observação predefinida do conjunto de teste. Para essa entrada, o modelo convencional de referência e o modelo Concrete ML produziram a classe 1. Adicionalmente, as execuções do modelo Concrete ML nas modalidades quantizada em claro, simulada e criptografada apresentaram a mesma classificação.

**Tabela 4 — Concordância das classificações na primeira execução UCI**

| Modalidade | Classe prevista |
|---|---:|
| Modelo convencional scikit-learn | 1 |
| Concrete ML — `fhe="disable"` | 1 |
| Concrete ML — `fhe="simulate"` | 1 |
| Concrete ML — `fhe="execute"` | 1 |

Foi possível executar inferência FHE sobre uma entrada do UCI 350 e preservar a classe da execução quantizada em claro nessa entrada.

A coincidência de classes não prova que as árvores sejam equivalentes. Também não estabelece igualdade de probabilidades nem preservação de decisões em todo o conjunto.

### 4.4. Desempenho computacional inicial

A execução com o UCI 350 também permitiu registrar os tempos apresentados na Tabela 5.

**Tabela 5 — Tempos observados na primeira execução Concrete ML com `n_bits=3`**

| Operação | Tempo observado |
|---|---:|
| Treinamento | 0,296 s |
| Compilação | 18,478 s |
| Predição quantizada em claro | 0,00144 s |
| Simulação FHE | 0,360 s |
| Predição FHE total | 2,385 s |

Nesta execução, a chamada FHE total foi aproximadamente 1.656 vezes mais lenta que a predição quantizada em claro.

Esse valor não estima o overhead médio. Ainda faltam repetições, medida de variabilidade e controle de aquecimento e cache.

A compilação apresentou duração de 18,478 segundos, superior ao tempo de treinamento observado. Esse custo constitui uma etapa distinta da inferência e não deve ser incorporado automaticamente ao tempo por predição em cenários nos quais o circuito compilado pode ser reutilizado.

O tempo de 2,385 segundos corresponde à predição FHE agregada medida pela API de alto nível. Como não foram obtidas medições separadas de cifragem, avaliação homomórfica e decifragem, não é possível atribuir o custo total a uma operação criptográfica específica.

### 4.5. Validação da infraestrutura experimental

A infraestrutura desenvolvida foi validada por meio de sete testes automatizados, todos concluídos com sucesso.

Além da execução dos testes, foram implementados mecanismos de persistência de resultados, registro de dependências e documentação do ambiente. Esses componentes constituem a base necessária para a repetição dos experimentos e para a comparação futura de diferentes configurações de precisão.

A obtenção reproduzível do UCI 350, o registro de hashes dos arquivos e a separação entre código, documentação e resultados locais também contribuem para a rastreabilidade do procedimento experimental.

### 4.6. Discussão dos resultados iniciais e limitações

Os experimentos realizados demonstram a viabilidade técnica inicial da inferência criptografada com árvores de decisão no ambiente investigado. Foi possível treinar e compilar um modelo compatível com Concrete ML, executar inferência FHE real e obter concordância de classificação entre as modalidades de execução para as entradas selecionadas.

Também foram observados custos computacionais substancialmente superiores aos da inferência quantizada em claro, indicando a importância de avaliar latência e eficiência nas próximas etapas.

Contudo, os resultados apresentados ainda são insuficientes para confirmar as hipóteses centrais da pesquisa. Não foi realizada uma comparação sistemática entre diferentes valores de `n_bits`, tampouco foram avaliadas discordâncias decisórias associadas a políticas de aprovação de crédito.

A concordância das classificações observadas nos testes iniciais não demonstra estabilidade de probabilidades, preservação de ordenação de risco ou equivalência de decisões em diferentes limiares. Além disso, as medições computacionais disponíveis correspondem a execuções isoladas e dependem das características específicas do hardware, das versões de software e das configurações utilizadas.

A primeira etapa demonstra viabilidade operacional do pipeline. Ela não valida as hipóteses sobre estabilidade decisória.

As próximas etapas devem comparar diferentes precisões, medir previsões pareadas e avaliar efeitos em políticas simuladas. Também precisam repetir as medições de latência.

## 5. Próximos passos e planejamento experimental

A primeira etapa preparou a infraestrutura e confirmou a viabilidade inicial da inferência FHE sobre dados sintéticos e uma observação do UCI 350. Esses testes são exploratórios. Eles não medem, de forma sistemática, o efeito da quantização sobre previsões ou decisões simuladas.

As próximas etapas investigarão três dimensões: desempenho preditivo, estabilidade decisória e custo computacional. Os experimentos compararão configurações de precisão numérica, políticas simuladas de aprovação e modalidades de execução. Hiperparâmetros, limiares e demais escolhas serão definidos com treino e validação antes da avaliação no teste.

### 5.1. Experimento 1: influência da quantização no desempenho preditivo

O primeiro experimento avaliará como a precisão numérica altera as previsões de modelos compatíveis com FHE. Serão consideradas inicialmente cinco configurações:

```text
B = {3, 4, 5, 6, 7}
```

Para cada valor de `n_bits`, será treinado um modelo Concrete ML com os demais hiperparâmetros fixados. Suas previsões serão comparadas às do modelo de referência em scikit-learn. A análise incluirá ROC-AUC, Average Precision, Brier Score, calibração e concordância entre previsões.

A alteração de `n_bits` pode mudar não apenas a representação numérica, mas também o modelo obtido no treinamento. Por isso, diferenças entre configurações serão tratadas como efeito do pipeline de modelagem e quantização. Não serão atribuídas exclusivamente à precisão numérica.

**Objetivo:** identificar a sensibilidade do desempenho preditivo às configurações de quantização.

**Questão relacionada:** QP1.

### 5.2. Experimento 2: estabilidade das decisões simuladas

O segundo experimento examinará como diferenças entre previsões alteram decisões simuladas de concessão. Serão avaliadas três políticas.

Na política por limiar, uma observação será aprovada quando o escore usado como PD estiver abaixo ou igual ao limiar definido na validação:

```text
a_i = 1, se p_hat_i <= tau; caso contrário, 0
```

Nessa expressão, `p_hat_i` representa o escore, `tau` o limiar e `a_i` a decisão binária. Esse uso como PD dependerá de uma verificação prévia de semântica e calibração. Caso o escore não possa ser interpretado como probabilidade, ele será tratado apenas como escore de risco.

Na política por capacidade fixa, serão aprovadas as observações com menores escores até atingir uma fração definida da carteira. O desempate será determinístico. Essa política permite observar se alterações na ordenação mudam a composição do grupo aprovado.

Na política de utilidade simulada, será usada uma função ilustrativa de retorno esperado:

```text
U_i = EAD_i * ((1 - p_hat_i) * r - p_hat_i * LGD) - c_i
```

`EAD_i` representa a exposição estimada, `r` uma taxa hipotética de receita, `LGD` a perda dado o inadimplemento e `c_i` um custo da operação. Esses parâmetros serão premissas experimentais. Eles não representam condições observadas de uma instituição financeira.

A principal medida será a discordância entre duas configurações:

```text
D(A, B) = (número de casos em que a_i^A != a_i^B) / N
```

Também serão examinadas a taxa de aprovação, a composição dos grupos aprovados e a concentração das discordâncias perto dos limiares. Capacidades, limiares e parâmetros financeiros serão definidos na validação.

**Objetivo:** verificar se diferenças associadas à quantização alteram decisões simuladas.

**Questão relacionada:** QP2.

**Hipóteses relacionadas:** H1 e H2.

### 5.3. Experimento 3: custo computacional da inferência FHE

O terceiro experimento medirá o custo das configurações selecionadas. A comparação incluirá inferência quantizada em claro, simulação FHE e inferência FHE real do mesmo modelo compilado.

Serão registrados tempo de compilação e tempo de inferência. Quando a API permitir, o protocolo também separará geração de chaves, cifragem, avaliação homomórfica e decifragem. Caso essa separação não esteja disponível, o relatório identificará a medida como tempo total da chamada FHE.

As medições serão repetidas. Serão reportadas mediana e dispersão, em vez de um único tempo. Como a execução FHE é custosa, o benchmark poderá usar uma amostra reduzida e reprodutível, estratificada por faixa de risco e proximidade dos limiares.

Tempo de compilação e tempo de inferência serão apresentados separadamente. As interpretações também informarão hardware, versões das bibliotecas, parâmetros criptográficos e tamanho da amostra.

**Objetivo:** caracterizar o custo das configurações e seus limites práticos para inferência protegida.

**Questão relacionada:** QP3.

**Hipótese relacionada:** H3.

### 5.4. Experimento 4: análise integrada dos compromissos

O último experimento reunirá os resultados anteriores. Cada configuração será descrita por indicadores de desempenho preditivo, discordância decisória e latência FHE.

Visualizações comparativas mostrarão os compromissos entre essas dimensões. Quando os dados permitirem, será usada análise de dominância de Pareto para identificar configurações não dominadas, isto é, alternativas que não melhoram uma dimensão sem piorar outra.

Não se pressupõe uma configuração universalmente ótima. A escolha pode depender da política simulada e da restrição de latência considerada.

**Objetivo:** identificar configurações com compromissos favoráveis entre desempenho, estabilidade e custo.

**Questão relacionada:** QP4.

**Hipótese relacionada:** H3.

### 5.5. Organização dos experimentos

| Experimento | Variável principal | Indicadores | Foco da etapa |
|---|---|---|---|
| 1. Quantização | `n_bits` de 3 a 7 | ROC-AUC, AP, Brier, calibração e consistência | Sensibilidade preditiva à precisão |
| 2. Estabilidade decisória | Política e configuração do modelo | Discordância, aprovação e distância ao limiar | Efeito das diferenças preditivas nas decisões |
| 3. Custo computacional | Configuração FHE e modalidade de execução | Compilação, latência e dispersão | Caracterização do custo computacional |
| 4. Análise integrada | Combinação das configurações | Desempenho, discordância e latência | Compromissos e alternativas não dominadas |

### 5.6. Critérios de avaliação das hipóteses

H1 será avaliada pela comparação entre desempenho agregado e discordância decisória. Configurações com métricas preditivas semelhantes, mas decisões diferentes, constituirão evidência compatível com a hipótese.

H2 será avaliada pela distância entre os escores e os limiares de aprovação. A análise verificará se decisões divergentes se concentram mais perto dessas fronteiras do que decisões concordantes.

H3 será avaliada pela relação entre precisão, estabilidade e custo. A existência de configurações com perfis distintos nessas dimensões caracterizará o compromisso investigado.

Quando possível, serão usados intervalos de confiança por reamostragem. Eles evitam conclusões baseadas apenas em diferenças pontuais.

### 5.7. Limitações previstas

O UCI 350 representa clientes que já possuíam cartão. Ele não permite estimar o efeito causal de uma política para novos solicitantes nem a rentabilidade real de uma carteira.

Os escores dos modelos só serão usados como probabilidades de inadimplência após verificação de semântica e calibração. As políticas são instrumentos experimentais, não recomendações de concessão de crédito.

Por fim, tempos medidos em um computador não se generalizam diretamente para ambientes de produção. Arquitetura, versão de software, tamanho do lote e parâmetros criptográficos podem alterar a latência observada.

## Referências

ALLAVARPU, V. V. L. D.; NARESH, V. S.; MOHAN, A. K. Neural Network-Driven Privacy-Preserving Credit Risk Analysis: A Homomorphic Encryption Approach. *Contemporary Mathematics*, v. 6, n. 1, 2025. DOI: https://doi.org/10.37256/cm.6120255949.

CONG, K.; KANG, J.; NICOLAS, G.; PARK, J. *Faster Private Decision Tree Evaluation for Batched Input from Homomorphic Encryption*. [Dados bibliográficos de publicação a confirmar].

FRERY, J. et al. *Privacy-Preserving Tree-Based Inference with TFHE*. arXiv:2303.01254, 2023. Disponível em: https://arxiv.org/abs/2303.01254.

SHUKLA, N.; PANDYA, M. A.; SAMANTH, S. Fully Homomorphic Encryption and Artificial Intelligence: A Review of Architectures, Optimizations, and Distributed Privacy. *IEEE Access*, 2026. DOI: https://doi.org/10.1109/ACCESS.2026.3746630.

YILMAZ, E. et al. Homomorphic Encryption in Finance: Training and Inference on Encrypted Data with Concrete ML. *Afyon Kocatepe University Journal of Science and Engineering*, v. 26, p. 64–77, 2026. DOI: https://doi.org/10.35414/akufemubid.1686923.

UCI MACHINE LEARNING REPOSITORY. *Default of Credit Card Clients*. Dataset ID 350. Disponível em: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients.
