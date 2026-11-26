# Análise inicial de data leakage

Variáveis de performance Freddie Mac e de servicing/resultado LendingClub são `POST_ORIGINATION`: não são candidatas para o modelo ou política de concessão. Exemplos: saldo atual, atraso, zero balance, pagamento, status, recuperações, despesas e perdas.

Taxa original, UPB/origination amount, LTV/DTI original e atributos de crédito podem ser candidatos somente após confirmar sua disponibilidade no instante operacional definido. Grade, subgrade, taxa e valor financiado LendingClub podem refletir processos de precificação/underwriting já executados e devem ser tratados como risco de leakage para uma simulação de solicitação anterior à aprovação.

O arquivo `results/dataset_audit/comparison/leakage_matrix.csv` é uma classificação inicial por nome e deve ser revisado contra documentação antes de uso experimental.
