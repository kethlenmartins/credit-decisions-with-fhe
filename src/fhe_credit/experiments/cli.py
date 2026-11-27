"""Command-line interface. All output is JSON for notebook and shell reuse."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ..experiment_registry import load_experiment_registry
from .errors import ExperimentError
from .executor import analyze_run, execute_config, locate_run_results_root, plan_config, resume_config, status_run, verify_run


def _print(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fhe-credit-experiments")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--results-root", default=None)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    describe = commands.add_parser("describe"); describe.add_argument("--experiment-id", required=True)
    validate = commands.add_parser("validate"); validate.add_argument("--config", required=True)
    plan = commands.add_parser("plan"); plan.add_argument("--config", required=True)
    run = commands.add_parser("run"); run.add_argument("--config", required=True); run.add_argument("--execute", action="store_true")
    analyze = commands.add_parser("analyze"); analyze.add_argument("--run-id", required=True)
    status = commands.add_parser("status"); status.add_argument("--run-id", required=True)
    verify = commands.add_parser("verify"); verify.add_argument("--run-id", required=True)
    resume = commands.add_parser("resume"); resume.add_argument("--run-id", required=True); resume.add_argument("--execute", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.project_root).resolve()
    registry_path = root / "experiments" / "registry.yaml"
    if not registry_path.is_file():
        registry_path = root / "configs" / "registry" / "experiments.yaml"
    results = args.results_root
    try:
        if args.command == "list":
            _print({"experiments": load_experiment_registry(registry_path)}); return 0
        if args.command == "describe":
            entry = load_experiment_registry(registry_path).get(args.experiment_id)
            if entry is None: raise ExperimentError("experiment_id is absent from the registry")
            _print(entry); return 0
        if args.command == "validate":
            plan = plan_config(args.config, root)
            _print({"valid": True, "experiment_id": plan["experiment_id"], "configuration_id": plan["configuration_id"], "config_hash": plan["config_hash"]})
            return 0
        if args.command == "plan": _print(plan_config(args.config, root)); return 0
        if args.command == "run":
            _print(execute_config(args.config, project_root=root, results_root=results, authorized=args.execute)); return 0
        if args.command in {"analyze", "status", "verify", "resume"}:
            resolved_results = results or str(locate_run_results_root(args.run_id, root))
        if args.command == "analyze": _print(analyze_run(args.run_id, results_root=resolved_results)); return 0
        if args.command == "status": _print(status_run(args.run_id, results_root=resolved_results)); return 0
        if args.command == "verify": _print(verify_run(args.run_id, results_root=resolved_results)); return 0
        if args.command == "resume": _print(resume_config(args.run_id, project_root=root, results_root=resolved_results, authorized=args.execute)); return 0
    except (ExperimentError, ValueError, FileNotFoundError) as error:
        _print({"error": type(error).__name__, "message": str(error)})
        return 2
    raise AssertionError("unreachable command")
