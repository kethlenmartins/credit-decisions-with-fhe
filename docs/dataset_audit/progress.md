# Progresso da auditoria

## Fase 1 — fundamentos

- **Executado:** inventário de arquivos, hashes SHA-256, inspeção de membros ZIP e teste de integridade dos ZIPs; as saídas estão em `results/dataset_audit/inventory/`.
- **Executado:** reconstrução inicial dos schemas de originação e performance a partir das duas abas do `file_layout_july_2026.xlsx`; saídas em `results/dataset_audit/freddie_mac/`.
- **Executado:** leitura do guia local Freddie Mac. Ele identifica a Release 48 (outubro de 2026), descreve os arquivos como um dataset vivo e remete o uso aos termos do dataset e do site.
- **Executado:** auditoria estrutural das sete amostras Freddie Mac, com checkpoint por safra. Cada safra possui 50.000 empréstimos de originação e 50.000 identificadores na performance; não foram observadas linhas malformadas, identificadores duplicados ou falhas de referência dentro de cada amostra. Os registros mensais variam de 1.977.122 (2019) a 3.501.425 (2015). Esses números descrevem as amostras locais, não o dataset completo.
- **Executado:** auditoria estrutural do LendingClub em blocos. Foram lidos 2.260.701 registros, 151 colunas e 2.260.701 IDs não ausentes e únicos. O leitor não reportou linhas inválidas; isso não substitui uma validação de conteúdo por campo.
- **Executado (triagem de target):** no LendingClub, a definição de resultado final `Fully Paid` versus `Charged Off` tem 1.345.310 observações elegíveis: 1.076.751 e 268.559, respectivamente. Estados ativos e outros não foram classificados como negativos. Para Freddie Mac, a incidência de registros empréstimo-mês com atraso de 90+ dias varia de 0,309% (2021) a 1,333% (2018); não é prevalência de um target por empréstimo nem por horizonte.

## Fase 2 — auditoria de dados

- **Executado:** feasibility de alvo Freddie Mac por empréstimo para 6, 12, 24 e 36 meses, usando o primeiro pagamento como referência. Zero balance foi classificado como evento concorrente agregado e não como negativo.
- **Pendente/bloqueado:** decomposição de zero balance em pré-pagamento e encerramento adverso, pois a regra documental e o estimando não foram congelados.
- **Pendente:** profiling completo de todas as variáveis, drift, outliers e visualizações. A sua execução antes de confirmar o schema histórico de 2015–2021 poderia misturar campos incompatíveis com o layout de 2026.

**Encerramento:** ver `phase2_completion.md`. Componentes não identificáveis foram marcados como tal; não serão preenchidos por inferência.

## Fase 3 — auditoria financeira

- **Executado:** matriz inicial de leakage e cobertura financeira, além da classificação de viabilidade para as 12 políticas em `results/dataset_audit/comparison/`.
- **Limite:** P01–P05 são parcialmente empíricas; P06–P12 dependem de parâmetros financeiros e devem ser tratadas como simulação. Nenhuma conclusão sobre lucro ou política real foi produzida.

**Encerramento:** ver `phase3_completion.md`; as matrizes A/B e X/Z/Y/W foram consolidadas sem converter condições contratadas em informação pré-concessão.

## Fases 4 e 5 — computação e consolidação

- **Executado:** ambiente registrado, matriz decisória sem notas arbitrárias e relatório comparativo.
- **Pendente/bloqueado:** diagnóstico de quantização, pré-processamento e benchmark FHE dependem do conjunto de features permitido após revisão de leakage e de uma divisão temporal/estimando congelados. Não foram iniciados para não ajustar transformações usando dados de teste ou variáveis pós-originação.
- **Executado:** relatório em `docs/dataset_audit/comparison.md`; recomendação mantida explicitamente pendente.

**Fase 4 encerrada:** ver `phase4_completion.md`; quantização e FHE permanecem `PENDING` por gates explicitamente documentados.

**Fase 5 encerrada:** ver `phase5_completion.md`; a matriz e a recomendação permanecem preliminares, sem pontuações arbitrárias.

## Decisões e bloqueios

- Usar o layout de julho/2026 como referência operacional provisória: a contagem de campos coincide nas amostras, mas a compatibilidade semântica histórica permanece não verificada.
- Não usar `loan_status`, pagamentos, recuperações, saldo atual ou variáveis de performance como features de concessão.
- Não há termos de uso do LendingClub disponíveis localmente; a licença permanece pendente.
- A reexecução deve ocorrer em sessão persistente ou com checkpoints por safra, pois a auditoria completa é I/O-intensiva.
