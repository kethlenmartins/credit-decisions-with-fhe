"""Executa a auditoria local sem treinamento ou inferência FHE."""
import argparse

from src.fhe_credit.dataset_audit import run_audit

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--freddie-year", type=int, action="append", dest="years")
    parser.add_argument("--skip-lending", action="store_true")
    parser.add_argument("--lending-only", action="store_true")
    args = parser.parse_args()
    result = run_audit(
        years=[] if args.lending_only else args.years,
        include_lending=not args.skip_lending,
    )
    print(result)
