# Instruções para agentes — FHE Credit Decision

## Contexto e objetivo
Este repositório contém uma pesquisa experimental de criptografia totalmente homomórfica (FHE) aplicada à inferência de risco de crédito e a decisões **simuladas**. Pergunta principal: como a precisão de quantização de modelos compatíveis com FHE afeta a estabilidade das decisões simuladas e o custo computacional da inferência cifrada?

## Idioma e comunicação
- Escrever README, documentação, artigo, comentários explicativos de pesquisa e mensagens de entrega em **português brasileiro**.
- Manter código, identificadores, nomes de funções/classes, variáveis e nomes de testes em **inglês**. Nomes de arquivos existentes não devem ser alterados sem necessidade.
- Preferir documentação em Markdown; referências tabulares em CSV. Não criar PDFs automaticamente.

## Regras de integridade científica
- **Nunca inventar** resultados, métricas, citações, DOI, versões, tempos de execução ou status de testes. Distinguir: planejado, implementado, executado e validado.
- Não afirmar que FHE melhora acurácia ou que o experimento comprova eficácia de concessão real.
- Distinguir rigorosamente: (1) modelo float em claro, (2) modelo quantizado em claro e (3) execução FHE do mesmo modelo quantizado.
- Não confundir treinamento cifrado com inferência cifrada. A menos que seja implementado, o treinamento ocorre em claro e a decisão de política é aplicada ao escore decifrado.
- O dataset UCI 350 contém portadores de cartão existentes, não solicitações novas; políticas de aprovação são contrafactuais simulados, sem validação causal ou de rentabilidade bancária real.
- Preservar partições estratificadas treino/validação/teste (60/20/20). Ajustar pré-processamento, calibração, limiares e hiperparâmetros somente em treino/validação; teste final não deve guiar escolhas.
- Documentar sementes, versões de pacotes, hardware, quantização, tamanhos de amostra, duração e métodos de medição.
- Para cada referência, registrar fonte e status de leitura/verificação. Não completar metadados bibliográficos com suposições.

## Estrutura e responsabilidades
- `README.md`: apresentação e navegação, pré-requisitos e início rápido.
- `artigo/README.md`: índice científico.
- `artigo/protocolo-experimental.md`: questão, hipóteses, políticas, desenho experimental e limitações.
- `artigo/trabalhos-relacionados.md`: revisão crítica e diferenciação.
- `artigo/matriz-bibliografica.csv`: referências e estado de verificação.
- `artigo/manuscrito.md`: artigo em elaboração; não escrever resultados antes da execução.
- `docs/ambiente.md`: instalação e solução de problemas em computadores diferentes.
- `docs/dados.md`: proveniência e obtenção reproduzível do dataset.
- `src/fhe_credit/`: implementação reutilizável.
- `experiments/`: experimentos executáveis e numerados.
- `tests/`: testes automatizados.

## Fluxo de trabalho obrigatório
1. Inspecionar `git status`, arquivos existentes e comandos atuais antes de alterar qualquer coisa.
2. Explicar resumidamente o plano quando a mudança for ampla; fazer alterações pequenas e reversíveis.
3. Não sobrescrever mudanças locais nem mover/remover código sem autorização explícita.
4. Priorizar solução simples, testável e reproduzível; não adicionar dependências sem justificativa.
5. Rodar `PYTHONPATH=. python -m pytest -q` após mudanças de código, quando dependências estiverem disponíveis. Informar resultados reais e erros, sem alegar sucesso quando não executou.
6. Ao mudar comportamento experimental, atualizar `artigo/protocolo-experimental.md` e a documentação relevante.
7. Ao concluir, listar arquivos modificados, comandos de validação, limitações e próximos passos.
8. Não criar commits, fazer push, abrir PRs nem alterar configurações remotas sem solicitação explícita.

## Dados, segurança e Git
- Não versionar `data/raw/`, `data/processed/`, ambientes virtuais, segredos, credenciais, chaves privadas ou resultados volumosos.
- O download do dataset deve continuar reproduzível por `python -m src.fhe_credit.download_data`; preservar manifesto de proveniência e hashes localmente.
- Antes de publicar, inspecionar `git diff --cached` e `git status` para evitar vazamento de dados.
- Não adicionar arquivos PDF de terceiros à pasta `artigo/` sem confirmar permissões; preferir referências bibliográficas e links.

## Implementação FHE
- Usar Concrete ML somente com versões de Python, sistema e arquitetura compatíveis, verificadas na máquina de execução.
- Registrar separadamente tempo de compilação, cifragem, inferência e decifragem, se disponíveis.
- Testar equivalência de predição entre modo quantizado em claro e execução FHE com tolerâncias e formato de saída adequados; não assumir equivalência de probabilidades sem verificar.
- Evitar prometer execução FHE em macOS/Apple Silicon sem checagem de compatibilidade.
