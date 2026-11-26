# Fase 2 — auditoria de dados: encerramento

## Executado

- Inventário, schema estrutural, integridade e vínculo originação–performance das sete amostras Freddie Mac.
- Integridade LendingClub: 2.260.701 registros, 151 campos e IDs não ausentes únicos.
- Perfis numéricos exploratórios de features candidatas; códigos/extremos como `999` foram preservados.
- Cobertura mensal e lacunas Freddie Mac: somente 2015 (2 empréstimos; 3 meses) e 2017 (1 empréstimo; 2 meses) apresentaram lacunas internas.
- Targets Freddie 30/60/90+ estão documentados como candidatos; 90+ em 6/12/24/36 meses foi calculado nos cenários S01, S02 e S03_COUNTS. O arquivo não contém estimador Aalen–Johansen executado.
- LendingClub: target de resultado final `Fully Paid` versus `Charged Off` executado. Targets temporais 6/12/24/36 são `NOT_IDENTIFIABLE`: não há data documental de default e `last_pymnt_d` não foi usado como substituto.

## Não identificável ou bloqueado

- Compatibilidade semântica histórica do layout 2026: `PENDING`; a coincidência de campos é apenas estrutural.
- Separação de todos os encerramentos em pré-pagamento versus perda observada: parcialmente identificável pelos códigos; não se imputa data ou severidade ausente.
- Drift e profiling integral de variáveis textuais de alta cardinalidade: `PENDING`; exigem uma política de amostragem/privacidade e schema histórico validado. Não foram aproximados silenciosamente.
- Figuras que dependeriam dessas variáveis ou de targets não identificáveis: `BLOCKED`.

## Conclusão

A Fase 2 está encerrada para os componentes identificáveis nos arquivos locais. Os itens restantes foram classificados explicitamente, e não substituídos por suposições. A continuação nas fases seguintes deve usar apenas targets, campos e cenários com status executado.
