# Trabalhos relacionados — revisão crítica inicial

> Material de revisão científica, não versão final de uma revisão sistemática. Os resumos abaixo distinguem **contribuições reportadas pelos autores** de oportunidades para o presente projeto. As referências completas e seu status estão em `matriz-bibliografica.csv`.

## 1. Inferência de árvores com TFHE — Frery et al. (2023)

**Referência:** Jordan Frery et al., *Privacy-Preserving Tree-Based Inference with TFHE*, arXiv:2303.01254, 2023. [Texto](https://arxiv.org/abs/2303.01254).

**Contribuição reportada:** representação de inteiros em TFHE, quantização de entradas e saídas de árvores, avaliação de comparações com programmable bootstrapping e automação da parametrização criptográfica. O trabalho apresenta a técnica para árvores, Random Forest e boosting, com experimentos de precisão e latência.

**Relevância:** base de implementação para Concrete ML e justificativa do experimento com bits e custo computacional. No artigo, os autores discutem resultados de 5–6 bits e crescimento expressivo da latência em bitwidths maiores **nas configurações que testaram**; não transferir esses valores diretamente para nosso dataset.

**Distinção proposta:** avaliar consequências em **políticas de crédito** e discordâncias de decisão, não melhorar o protocolo TFHE.

## 2. Inferência homomórfica em finanças — Yılmaz et al. (2026)

**Referência:** Ensar Yılmaz et al., *Homomorphic Encryption in Finance: Training and Inference on Encrypted Data with Concrete ML*, *Afyon Kocatepe University Journal of Science and Engineering*, v. 26, 2026. [DOI](https://doi.org/10.35414/akufemubid.1686923).

**Contribuição reportada:** aplicações financeiras com Concrete ML e modelos XGBoost/Random Forest associados a métricas de distress de empresas. A avaliação inclui erros de previsão, efeitos de quantização e latência cifrada.

**Cuidado de leitura:** embora o título mencione treinamento em dados cifrados, o **resumo descreve inferência cifrada sobre modelos treinados em datasets abertos**. Antes de afirmar treinamento inteiramente homomórfico, verificar os passos da seção de métodos.

**Distinção proposta:** sair de regressão de indicadores financeiros para **mudança de decisões discretas** e políticas simuladas de crédito individual.

## 3. Avaliação em lote de árvores com BFV — Cong et al.

**Referência:** *Faster Private Decision Tree Evaluation for Batched Input from Homomorphic Encryption*, autores Cong et al. Metadados completos, ano de publicação e versão final: **pendentes de confirmação** no registro bibliográfico.

**Contribuição reportada:** protocolo não interativo para avaliação privada de árvores em lote, com comparações e processamento de múltiplas consultas sob criptografia homomórfica; o desempenho é estudado como custo de computação e comunicação.

**Relevância:** explica por que tamanho de lote e primitivas de comparação influenciam latência. O nosso benchmark usa Concrete ML/TFHE, **não implementa a proposta BFV dos autores** e não deve comparar tempos absolutos sem normalizar hardware e carga.

## 4. Panorama de FHE e IA — Shukla, Pandya e Samanth (2026)

**Referência:** *Fully Homomorphic Encryption and Artificial Intelligence: A Review of Architectures, Optimizations, and Distributed Privacy*, *IEEE Access*, 2026. [DOI](https://doi.org/10.1109/ACCESS.2026.3746630).

**Contribuição reportada:** revisão de esquemas, aceleração de hardware, batching, inferência privada e aprendizado federado. Distingue a inferência com **pesos previamente treinados** do treinamento cifrado completo.

**Relevância:** embasamento da escolha por inferência cifrada, trade-offs e ameaça operacional. **Não é uma contribuição experimental diretamente comparável**.

## 5. Trabalho correlato indispensável — Allavarpu, Naresh e Mohan (2025)

**Referência:** *Neural Network-Driven Privacy-Preserving Credit Risk Analysis: A Homomorphic Encryption Approach*, *Contemporary Mathematics*, v. 6(1), 2025. [DOI](https://doi.org/10.37256/cm.6120255949).

**Contribuição reportada:** modelo de rede neural com TenSEAL/PyTorch voltado a análise de risco de crédito preservando privacidade, com avaliação em diferentes datasets financeiros.

**Por que incluir:** este estudo já aproxima **HE e credit risk**, portanto impede afirmar como novidade apenas 'aplicar homomorphic encryption ao crédito'. Nossa distinção a testar é **estabilidade de decisões sob políticas econômicas e quantização**, não a mera criptografia de dados financeiros. Uma leitura integral dos detalhes de custo, modelo de ameaça e quantização ainda é necessária.

## 6. Artefato de implementação — Zama Concrete ML

**Referência:** [Exemplo público de credit scoring com Concrete ML](https://github.com/zama-ai/concrete-ml/tree/main/use_case_examples/credit_scoring).

**Relevância:** referência operacional de modelos e métodos de inferência cifrada; **não contar como artigo revisado por pares**. Investigar particionamento e pré-processamento do exemplo antes de reutilizar resultados ou práticas.

## Síntese da lacuna científica (a confirmar)

Os estudos examinados abordam **inferência privada, quantização, predição financeira ou custo computacional**, mas não estabelecem conjuntamente, nesta seleção inicial, a relação entre **número de bits → mudança de escores → inversões de decisão por política → custo de FHE** em uma configuração reproduzível de credit scoring. Isso é uma **lacuna candidata**, não prova de ineditismo. A revisão deve ser ampliada para *profit-driven credit scoring*, *cost-sensitive decision making*, *decision-focused learning*, model quantization, e estudos HE em crédito.

## Próximas leituras e extrações

- Extrair dos cinco artigos: modelo de ameaça; quais dados ficam cifrados; família HE; operação no servidor; versão de software; CPU/GPU; número de amostras; desenho de validação; como o score é recuperado; efeito de quantização; limitações reconhecidas.
- Buscar trabalhos sobre **inversões de decisão perto de cutoffs** e sobre **calibração de PD**; adicionar as referências com identificadores verificáveis.
- Preservar evidências em notas com páginas exatas, em vez de usar interpretações gerais como citações diretas.
