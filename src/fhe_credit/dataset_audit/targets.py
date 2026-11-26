"""Construção exploratória e documentada de indicadores de seguimento."""

from __future__ import annotations

import zipfile
from pathlib import Path

from .runner import DATASETS, RESULTS, schema_from_layout, write_csv


def _month(value: str) -> int | None:
    if len(value) != 6 or not value.isdigit():
        return None
    year, month = int(value[:4]), int(value[4:])
    return year * 12 + month - 1 if 1 <= month <= 12 else None


def freddie_target_feasibility(year: int) -> list[dict]:
    """Classifica o seguimento por empréstimo sem tratar censura como negativa."""
    layout = DATASETS / "file_layout_july_2026.xlsx"
    orig_width = len(schema_from_layout(layout, "xl/worksheets/sheet1.xml", "origination"))
    perf_width = len(schema_from_layout(layout, "xl/worksheets/sheet2.xml", "performance"))
    archive_path = DATASETS / f"sample_{year}.zip"
    with zipfile.ZipFile(archive_path) as archive:
        orig_name = next(name for name in archive.namelist() if "orig" in name.lower())
        perf_name = next(name for name in archive.namelist() if "perf" in name.lower())
        loans: dict[str, dict[str, int | None]] = {}
        with archive.open(orig_name) as stream:
            for raw in stream:
                fields = raw.decode("latin-1").rstrip("\r\n").split("|")
                if len(fields) == orig_width:
                    loans[fields[19]] = {"reference": _month(fields[1]), "last": None, "event": None, "zero": None, "zero_code": None}
        with archive.open(perf_name) as stream:
            for raw in stream:
                fields = raw.decode("latin-1").rstrip("\r\n").split("|")
                if len(fields) != perf_width or fields[0] not in loans:
                    continue
                row = loans[fields[0]]; period = _month(fields[1])
                if period is None:
                    continue
                row["last"] = period if row["last"] is None or period > row["last"] else row["last"]
                status = fields[3].strip()
                if status.isdigit() and int(status) >= 3 and (row["event"] is None or period < row["event"]):
                    row["event"] = period
                if fields[8].strip() and (row["zero"] is None or period < row["zero"]):
                    row["zero"] = period
                    row["zero_code"] = fields[8].strip()
    rows = []
    for horizon in (6, 12, 24, 36):
        counts = {key: 0 for key in ("event", "negative", "competing", "censored", "indeterminate", "adverse")}
        for loan in loans.values():
            reference, last, event, zero, zero_code = loan.values()
            if reference is None or last is None:
                counts["indeterminate"] += 1; continue
            end = reference + horizon
            if event is not None and event <= end and (zero is None or event <= zero):
                counts["event"] += 1
            elif zero is not None and zero <= end:
                if zero_code == "01": counts["competing"] += 1
                elif zero_code in {"02", "03", "09"}: counts["adverse"] += 1
                elif zero_code == "96": counts["censored"] += 1
                else: counts["indeterminate"] += 1
            elif last >= end:
                counts["negative"] += 1
            else:
                counts["censored"] += 1
        eligible = counts["event"] + counts["negative"] + counts["competing"]
        rows.append({"dataset": "freddie_mac", "vintage": year, "scenario": "S01", "event": "delinquency_90_plus", "horizon_months": horizon,
                     "population_original": len(loans), "population_eligible": eligible, "events_positive": counts["event"],
                     "observations_negative": counts["negative"] + counts["competing"], "prepayment_negative": counts["competing"], "adverse_termination": counts["adverse"], "censored": counts["censored"], "indeterminate": counts["indeterminate"],
                     "prevalence_eligible": counts["event"] / eligible if eligible else None,
                     "definition_note": "S01: 01 é negativo; adversos e indeterminados ficam separados."})
        s02_eligible=counts["event"]+counts["negative"]
        rows.append({"dataset":"freddie_mac","vintage":year,"scenario":"S02","event":"delinquency_90_plus","horizon_months":horizon,"population_original":len(loans),"population_eligible":s02_eligible,"events_positive":counts["event"],"observations_negative":counts["negative"],"prepayment_negative":0,"adverse_termination":counts["adverse"],"censored":counts["censored"],"indeterminate":counts["indeterminate"]+counts["competing"],"prevalence_eligible":counts["event"]/s02_eligible if s02_eligible else None,"definition_note":"S02: pré-pagamentos anteriores ao horizonte excluídos."})
        rows.append({"dataset":"freddie_mac","vintage":year,"scenario":"S03_COUNTS","event":"delinquency_90_plus","horizon_months":horizon,"population_original":len(loans),"population_eligible":len(loans),"events_positive":counts["event"],"observations_negative":counts["negative"],"prepayment_negative":0,"adverse_termination":counts["adverse"],"censored":counts["censored"],"indeterminate":counts["indeterminate"],"competing_events":counts["competing"],"definition_note":"Contagens para riscos concorrentes; incidência Aalen-Johansen pendente."})
    return rows


def run_freddie_targets(years: list[int]) -> list[dict]:
    output = []
    for year in years:
        rows = freddie_target_feasibility(year)
        output.extend(rows)
        write_csv(RESULTS / "freddie_mac" / "checkpoints" / f"{year}_target_horizons.csv", rows)
    write_csv(RESULTS / "freddie_mac" / "target_horizon_feasibility.csv", output)
    return output
