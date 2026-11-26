"""Streaming, inspection-only dataset audit.  It never alters raw input files."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATASETS = ROOT / "datasets"
RESULTS = ROOT / "results" / "dataset_audit"
SPECIAL_VALUES = {"", "999", "9999", "99999", "XX", "X", "NA", "N/A"}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = sorted({key for row in rows for key in row}) if rows else []
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def xlsx_rows(path: Path, member: str) -> list[list[str]]:
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        strings = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        shared = ["".join(item.itertext()) for item in strings.findall("x:si", ns)]
        tree = ET.fromstring(archive.read(member))
    rows = []
    for row in tree.findall(".//x:sheetData/x:row", ns):
        values = []
        for cell in row.findall("x:c", ns):
            raw = cell.find("x:v", ns)
            value = "" if raw is None else raw.text or ""
            values.append(shared[int(value)] if cell.get("t") == "s" and value else value)
        rows.append(values)
    return rows


def schema_from_layout(layout: Path, sheet: str, source_table: str) -> list[dict]:
    rows = xlsx_rows(layout, sheet)
    header = rows[1]
    result = []
    for values in rows[2:]:
        if not values or not values[0].strip():
            continue
        row = dict(zip(header, values))
        name = row.get("Attribute Name", "")
        result.append({
            "position": row.get("Field Position", ""), "official_name": name,
            "code_name": slug(name), "data_type_format": row.get("Data Type & Format", ""),
            "max_length": row.get("Max Length", ""), "source_table": source_table,
            "documentation_source": "file_layout_july_2026.xlsx / " + source_table,
            "availability_temporal": "A confirmar por variável e contexto",
            "experimental_role": "A classificar na matriz de leakage",
        })
    return result


def inventory() -> list[dict]:
    rows = []
    for path in sorted(DATASETS.iterdir()):
        record = {"dataset": "freddie_mac" if "sample" in path.name or "file_" in path.name or "user_guide" in path.name else "lending_club",
                  "name": path.name, "relative_path": str(path.relative_to(ROOT)), "format": path.suffix.lstrip("."),
                  "size_bytes": path.stat().st_size, "sha256": sha256(path),
                  "local_modified_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                  "terms_status": "Pendente de confirmação"}
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive:
                record["members"] = "|".join(info.filename for info in archive.infolist())
                record["uncompressed_bytes"] = sum(info.file_size for info in archive.infolist())
                record["archive_test"] = "ok" if archive.testzip() is None else "corrupt"
        rows.append(record)
    return rows


def freddie_audit(year: int, path: Path, orig_schema: list[dict], perf_schema: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        orig_name = next(name for name in names if "orig" in name.lower())
        perf_name = next(name for name in names if "perf" in name.lower())
        def scan(name: str, width: int, identifier_at: int, period_at: int | None = None):
            ids, duplicate_ids, counts, malformed, records = set(), 0, Counter(), 0, 0
            periods, delinquent_90, zero_balance = [], 0, 0
            with archive.open(name) as binary:
                stream = (line.decode("latin-1").rstrip("\r\n") for line in binary)
                for line in stream:
                    records += 1; fields = line.split("|")
                    if len(fields) != width: malformed += 1; continue
                    ident = fields[identifier_at]
                    if ident in ids and period_at is None: duplicate_ids += 1
                    ids.add(ident); counts[ident] += 1
                    if period_at is not None:
                        if fields[period_at]: periods.append(fields[period_at])
                        status = fields[3].strip()
                        if status.isdigit() and int(status) >= 3: delinquent_90 += 1
                        if fields[8].strip(): zero_balance += 1
            return {"records": records, "unique_ids": len(ids), "ids": ids, "duplicate_ids": duplicate_ids, "malformed_rows": malformed,
                    "period_min": min(periods) if periods else "", "period_max": max(periods) if periods else "",
                    "delinquency_90_records": delinquent_90, "zero_balance_records": zero_balance,
                    "monthly_counts": counts}
        orig = scan(orig_name, len(orig_schema), 19)
        perf = scan(perf_name, len(perf_schema), 0, 1)
    coverage = [perf["monthly_counts"][loan] for loan in perf["monthly_counts"]]
    structural = {"dataset": "freddie_mac", "vintage": year, "origination_records": orig["records"], "origination_unique_loans": orig["unique_ids"], "origination_duplicate_ids": orig["duplicate_ids"], "performance_records": perf["records"], "performance_unique_loans": perf["unique_ids"], "origination_malformed_rows": orig["malformed_rows"], "performance_malformed_rows": perf["malformed_rows"], "performance_period_min": perf["period_min"], "performance_period_max": perf["period_max"], "loans_without_performance": len(orig["ids"] - perf["ids"]), "performance_loans_without_origination": len(perf["ids"] - orig["ids"])}
    monthly = {"dataset": "freddie_mac", "vintage": year, "loans_with_performance": len(coverage), "monthly_records_min": min(coverage) if coverage else 0, "monthly_records_mean": statistics.mean(coverage) if coverage else 0, "monthly_records_median": statistics.median(coverage) if coverage else 0, "monthly_records_max": max(coverage) if coverage else 0}
    targets = {"dataset": "freddie_mac", "vintage": year, "unit": "loan_month (não é target por empréstimo)", "candidate": "registro com atraso >= 90 dias", "positive_records": perf["delinquency_90_records"], "denominator_records": perf["records"], "prevalence": perf["delinquency_90_records"] / perf["records"] if perf["records"] else None, "zero_balance_records": perf["zero_balance_records"], "status": "Pendente: classificação por empréstimo e horizontes requer pareamento temporal"}
    return [structural], [monthly], [targets]


def lending_audit(path: Path) -> tuple[dict, list[dict], list[dict], list[dict]]:
    total = valid = malformed = 0; ids = set(); duplicates = 0; statuses = Counter(); vintages = Counter(); terms = Counter(); missing = Counter(); columns = []
    for chunk in pd.read_csv(path, compression="gzip", chunksize=100_000, dtype=str, on_bad_lines="warn", low_memory=False):
        if not columns: columns = list(chunk.columns)
        total += len(chunk); valid += len(chunk); missing.update(chunk.isna().sum().to_dict())
        for value in chunk["id"].fillna(""):
            if not value: continue
            if value in ids: duplicates += 1
            ids.add(value)
        statuses.update(chunk["loan_status"].fillna("<missing>")); terms.update(chunk["term"].fillna("<missing>"))
        dates = pd.to_datetime(chunk["issue_d"], format="%b-%Y", errors="coerce")
        vintages.update(dates.dt.strftime("%Y-%m").fillna("<invalid>"))
    structural = {"dataset": "lending_club", "records": total, "valid_records": valid, "columns": len(columns), "unique_nonmissing_ids": len(ids), "duplicate_ids": duplicates, "malformed_rows": malformed, "status": "Leitura em chunks; pandas não reportou linhas inválidas"}
    schema = [{"dataset": "lending_club", "feature_name": name, "inferred_type": "string (leitura conservadora)", "missing_count": missing[name], "missing_percent": missing[name] / total if total else None} for name in columns]
    target_rows = [{"dataset": "lending_club", "candidate": "T01 final: Fully Paid vs Charged Off", "fully_paid": statuses["Fully Paid"], "charged_off": statuses["Charged Off"], "eligible": statuses["Fully Paid"] + statuses["Charged Off"], "status": "Estados ativos e outros não foram tratados como negativos; horizonte uniforme pendente"}]
    return structural, schema, [{"dataset": "lending_club", "vintage": key, "loans": value} for key, value in sorted(vintages.items())], [{"dataset": "lending_club", "loan_status": key, "loans": value} for key, value in statuses.most_common()] + [{"dataset": "lending_club", "term": key, "loans": value} for key, value in terms.items()] + target_rows


def leakage_and_finance(orig_schema: list[dict], perf_schema: list[dict], lending_schema: list[dict]) -> tuple[list[dict], list[dict]]:
    future = ("current", "delinquency", "zero balance", "recover", "loss", "expense", "payment", "status", "last_")
    rows = []
    for dataset, schema in [("freddie_mac", orig_schema + perf_schema), ("lending_club", lending_schema)]:
        for item in schema:
            name = item.get("official_name", item.get("feature_name", "")); key = name.lower()
            stage = "POST_ORIGINATION" if any(x in key for x in future) else "ORIGINATION_DECISION"
            rows.append({"dataset": dataset, "feature_name": name, "source_table": item.get("source_table", "accepted_loans"), "availability_stage": stage, "eligible_for_model": stage == "ORIGINATION_DECISION", "eligible_for_policy": stage == "ORIGINATION_DECISION", "eligible_for_outcome_evaluation": stage == "POST_ORIGINATION", "leakage_risk": "HIGH" if stage == "POST_ORIGINATION" else "MEDIUM", "justification": "Classificação inicial por nome; confirmar disponibilidade operacional/documental.", "documentation_source": item.get("documentation_source", "cabeçalho local"), "confidence_level": "LOW"})
    finance = []
    for dataset, fields in {"freddie_mac": ["Original UPB", "Current Actual UPB", "Original Interest Rate", "Actual Loss", "MI Recoveries", "Net Sales Proceeds"], "lending_club": ["loan_amnt", "funded_amnt", "int_rate", "recoveries", "total_rec_prncp", "out_prncp"]}.items():
        for field in fields:
            state = "DIRECTLY_OBSERVED" if field else "UNAVAILABLE"
            finance.append({"dataset": dataset, "indicator_or_variable": field, "classification": state, "limitation": "Disponibilidade temporal deve ser respeitada; variáveis pós-originação não são features de concessão."})
    return rows, finance


def environment() -> dict:
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(), "architecture": platform.machine(), "python": sys.version, "cpu_count": os.cpu_count(), "disk_free_bytes": os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize, "dependencies": {"pandas": pd.__version__, "numpy": np.__version__}}


def run_audit(years: list[int] | None = None, include_lending: bool = True) -> dict:
    started = time.perf_counter(); RESULTS.mkdir(parents=True, exist_ok=True)
    inv = inventory(); write_csv(RESULTS / "inventory" / "inventory.csv", inv); (RESULTS / "inventory" / "inventory.json").write_text(json.dumps(inv, indent=2, ensure_ascii=False), encoding="utf-8")
    orig = schema_from_layout(DATASETS / "file_layout_july_2026.xlsx", "xl/worksheets/sheet1.xml", "origination")
    perf = schema_from_layout(DATASETS / "file_layout_july_2026.xlsx", "xl/worksheets/sheet2.xml", "performance")
    write_csv(RESULTS / "freddie_mac" / "origination_schema.csv", orig); write_csv(RESULTS / "freddie_mac" / "performance_schema.csv", perf)
    structural=[]; monthly=[]; targets=[]
    for year in list(range(2015, 2022)) if years is None else years:
        a,b,c = freddie_audit(year, DATASETS / f"sample_{year}.zip", orig, perf)
        structural += a; monthly += b; targets += c
        # Persist each vintage before reading the next archive.
        write_csv(RESULTS / "freddie_mac" / "checkpoints" / f"{year}_structural_integrity.csv", a)
        write_csv(RESULTS / "freddie_mac" / "checkpoints" / f"{year}_monthly_coverage.csv", b)
        write_csv(RESULTS / "freddie_mac" / "checkpoints" / f"{year}_target_feasibility.csv", c)
    if structural:
        write_csv(RESULTS / "freddie_mac" / "structural_integrity.csv", structural)
        write_csv(RESULTS / "freddie_mac" / "monthly_coverage.csv", monthly)
        write_csv(RESULTS / "freddie_mac" / "target_feasibility.csv", targets)
    if not include_lending:
        return {"freddie_mac": structural, "elapsed_seconds": time.perf_counter()-started, "scope": "Checkpoint Freddie Mac concluído; LendingClub não solicitado nesta execução."}
    lc, lc_schema, vintages, lc_status = lending_audit(DATASETS / "accepted_2007_to_2018Q4.csv.gz")
    (RESULTS / "lending_club" / "structural_integrity.json").parent.mkdir(parents=True, exist_ok=True); (RESULTS / "lending_club" / "structural_integrity.json").write_text(json.dumps(lc, indent=2), encoding="utf-8")
    write_csv(RESULTS / "lending_club" / "schema.csv", lc_schema); write_csv(RESULTS / "lending_club" / "vintages.csv", vintages); write_csv(RESULTS / "lending_club" / "loan_status_distribution.csv", lc_status)
    leakage, finance = leakage_and_finance(orig, perf, lc_schema); write_csv(RESULTS / "comparison" / "leakage_matrix.csv", leakage); write_csv(RESULTS / "comparison" / "financial_variable_coverage.csv", finance)
    env=environment(); (RESULTS / "environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    summary={"freddie_mac": structural, "lending_club": lc, "elapsed_seconds": time.perf_counter()-started, "scope": "A01/A02/A03/A04 inicial; demais análises requerem definição documental e implementação incremental."}
    (RESULTS / "dataset_comparison.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary
