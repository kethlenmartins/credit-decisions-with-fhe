# Freddie Mac: Sample Dataset versus Full Dataset

## Evidência oficial e escopo

Os arquivos locais `sample_2015.zip` a `sample_2021.zip` são exclusivamente o **Sample Dataset** do Standard Dataset; não são arquivos anuais completos. O FAQ e o General User Guide oficiais informam que, para cada safra anual completa, a sample é uma **amostra aleatória simples de 50.000 empréstimos** do Standard Dataset: cada empréstimo elegível possui a mesma probabilidade de seleção. Para safras parciais, a quantidade é proporcional. As amostras têm os mesmos campos dos arquivos completos. [FAQ oficial](https://www.freddiemac.com/fmac-resources/research/pdf/faq.pdf), [General User Guide](https://www.freddiemac.com/fmac-resources/research/pdf/user_guide.pdf).

Portanto, as contagens locais de 50.000 por safra e os eventos observados nesta auditoria não representam o tamanho populacional anual, nem permitem afirmar que prevalências amostrais sejam exatamente iguais às populacionais. A amostragem aleatória simples é uma base para inferência descritiva sob suas condições, mas não elimina incerteza amostral, viés de cobertura do próprio Standard Dataset ou diferenças temporais.

## Cobertura e acesso ao Full Dataset

Freddie Mac informa que Standard e Non-Standard juntos abrangem aproximadamente 56 milhões de hipotecas originadas de 1999 até junho de 2026; esse total não fornece contagem por safra 2015–2021. O Full Standard Dataset pode ser baixado integralmente ou por safra pelo Clarity Data Intelligence, após registro e login. As contagens completas anuais devem ser obtidas dos arquivos/estatísticas do Clarity antes de qualquer cálculo definitivo. [Página do dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset), [atualização Clarity](https://capitalmarkets.freddiemac.com/clarity/whats-new/december-2025-clarity-updates).

O uso não comercial, acadêmico/de pesquisa e limitado é descrito como gratuito, sujeito aos termos aplicáveis. Redistribuição/comercialização requer acordo ou licença; acesso local não autoriza publicar os dados. [Página do dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset), [termos de dados](https://www.freddiemac.com/terms).

## Estimativas de recursos — antes do download

Não foi feito download do Full Dataset. A projeção deve ser calculada após obter `N_y`, o número oficial de empréstimos completos da safra `y`:

- fator de expansão da sample: `f_y = N_y / 50.000`;
- armazenamento descompactado por tabela: `f_y × tamanho descompactado da sample da tabela`;
- eventos projetados de uma definição: `f_y × eventos observados na sample`;
- intervalo de projeção: reportar a incerteza de amostragem e não tratar a multiplicação como contagem populacional.

Como exemplo metodológico, a sample 2015 ocupa cerca de 397 MB descompactada para 50.000 empréstimos. O volume anual completo deve ser estimado após obter `N_2015`; não se deve declarar um número de GB/TB sem esse denominador. Performance mensal tende a dominar disco, leitura e memória temporária. Planejar espaço adicional para descompressão, índices/checkpoints e resultados agregados; processamento por trimestre/ano e formatos colunares locais são preferíveis a carregar tudo em memória.

## Estratégia científica candidata

1. Usar Full Standard Dataset, quando autorizado, para treino temporal e estimativa de eventos, processando por safra/trimestre com checkpoints.
2. Congelar divisões temporais e pré-processamento somente no treino completo ou em amostra de treino reproduzível.
3. Criar subamostras controladas para desenvolvimento e FHE, preservando safra, target, distância ao limiar e grupos de risco; documentar seed e regra de seleção.
4. Criar amostra de estresse estratificada por proximidade de fronteiras decisórias **após** congelar modelo/limiar na validação. Ela mede estabilidade local, não prevalência populacional nem desempenho global.
5. Avaliar métricas globais no conjunto temporal apropriado; não extrapolar resultados FHE de uma subamostra de estresse para a carteira inteira.

## Comparação atualizada

| Alternativa | Escala analisada | Target temporal | Benefício | Limitação principal |
|---|---|---|---|---|
| Freddie Mac Sample Dataset | 50.000 empréstimos por safra local | Explorável com performance mensal | Leve, campos completos, checkpoints executados | Incerteza amostral; não equivale ao Full Dataset |
| Freddie Mac Full Dataset | Não baixado; `N_y` pendente no Clarity | Explorável com performance mensal | Mais eventos e treino temporal em escala | Acesso, armazenamento e processamento ainda precisam ser dimensionados por safra |
| LendingClub Accepted Loans | 2.260.701 registros locais | Resultado final; horizonte temporal não identificável | Variáveis de empréstimo e resultado final | Seleção de originados e ausência de data defensável de default |

## Decisão de acesso

Antes de solicitar/download do Full Dataset: obter contagens anuais no Clarity, aplicar a fórmula de capacidade acima, verificar os termos/click-through aplicáveis e confirmar espaço, processamento e controles de acesso. A amostra não deve penalizar a viabilidade estatística potencial do Full Dataset apenas pelo número absoluto de eventos observados em 50.000 empréstimos.
