"""Artefatos de decisão que não atribuem pontuações sem evidência."""
from __future__ import annotations

import json
from .runner import RESULTS, write_csv


POLICIES = [
    ("P01", "Fixed PD threshold"), ("P02", "Segmented PD threshold"), ("P03", "Capacity-based approval"),
    ("P04", "Risk bands"), ("P05", "Manual review"), ("P06", "Expected profitability"),
    ("P07", "RAROC"), ("P08", "Discrete credit allocation"), ("P09", "Continuous credit allocation"),
    ("P10", "Risk-based pricing"), ("P11", "Expected loss budget"), ("P12", "Portfolio optimization"),
]


def write_decision_scaffolding() -> None:
    policy_rows=[]
    for dataset in ("freddie_mac", "lending_club"):
        for code, policy in POLICIES:
            financial = code in {"P06", "P07", "P10", "P11", "P12"}
            policy_rows.append({"dataset": dataset, "policy_id": code, "policy": policy,
                                "feasibility": "PARTIALLY_EMPIRICAL" if not financial else "SIMULATION_ONLY",
                                "evidence_status": "PARTIAL", "limitation": "Sem contrafactuais; custo de capital, preço alternativo e variáveis futuras não podem ser observados no momento da concessão."})
    write_csv(RESULTS / "comparison" / "policy_coverage.csv", policy_rows)
    criteria=[]
    for criterion, weight in [("Adequação às políticas de crédito", .20), ("Variáveis financeiras", .15), ("Qualidade do target", .15), ("Controle de leakage", .10), ("Validação temporal", .10), ("Reprodutibilidade", .10), ("Viabilidade FHE", .10), ("Esforço de preparação", .05), ("Acesso e licença", .05)]:
        for dataset in ("freddie_mac", "lending_club"):
            criteria.append({"dataset": dataset, "criterion": criterion, "weight": weight, "score": "PENDING", "confidence": "LOW", "reason": "Não pontuado sem evidência completa e licença confirmada."})
    write_csv(RESULTS / "comparison" / "decision_matrix.csv", criteria)
    (RESULTS / "dataset_comparison.json").write_text(json.dumps({"recommendation": "PENDING", "reason": "Matriz sem pontuação: licença, schema histórico, leakage e estimando ainda requerem verificação."}, indent=2), encoding="utf-8")
