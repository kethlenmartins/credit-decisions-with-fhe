# Padrão de notebooks científicos

Notebooks são `.ipynb` convencionais, versionados sem outputs e executados em kernel Python local. O padrão é **analyze**: cada notebook recebe Run ID explícito, verifica artefatos antes de carregá-los e não seleciona a execução mais recente.

O template cobre identificação, motivação, pergunta/hipótese quando aplicável, fundamentação, referências, protocolo, configuração, proveniência, resultados, discussão, limitações, conclusão e reprodução. Experimentos técnicos podem declarar ausência de hipótese.

A execução experimental permanece no terminal via executor. Resultados derivados persistentes, se futuramente necessários, devem ter identificação própria e referência ao Run ID de origem; esta etapa não cria esse segundo registro.
