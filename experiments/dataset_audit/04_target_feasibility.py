"""Avalia seguimento e censura de Freddie Mac sem treinar modelos."""
from src.fhe_credit.dataset_audit.targets import run_freddie_targets

if __name__ == "__main__":
    rows = run_freddie_targets(list(range(2015, 2022)))
    print(f"target rows: {len(rows)}")
