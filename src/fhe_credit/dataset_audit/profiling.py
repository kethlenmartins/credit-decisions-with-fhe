"""Perfis descritivos em streaming; não executa modelagem."""
from __future__ import annotations
import zipfile
from collections import Counter
import numpy as np
import pandas as pd
from .runner import DATASETS, RESULTS, schema_from_layout, write_csv

FREDDIE_FIELDS = ("Classic FICO®", "Original UPB", "Original Loan-to-Value (LTV)", "Original Combined Loan-to-Value (CLTV)", "Original Debt-to-Income (DTI) Ratio", "Original Interest Rate")
LENDING_FIELDS = ("loan_amnt", "funded_amnt", "int_rate", "annual_inc", "dti", "fico_range_low")

def _stats(values, dataset, field, vintage):
    a=np.asarray(values, dtype=float); valid=a[~np.isnan(a)]
    return {"dataset":dataset,"feature_name":field,"vintage":vintage,"observations":len(a),"valid":len(valid),"missing":int(np.isnan(a).sum()),"minimum":float(np.min(valid)) if len(valid) else None,"maximum":float(np.max(valid)) if len(valid) else None,"mean":float(np.mean(valid)) if len(valid) else None,"median":float(np.median(valid)) if len(valid) else None,"p01":float(np.quantile(valid,.01)) if len(valid) else None,"p99":float(np.quantile(valid,.99)) if len(valid) else None}

def run_profiles():
    schema=schema_from_layout(DATASETS/'file_layout_july_2026.xlsx','xl/worksheets/sheet1.xml','origination'); positions={x['official_name']:int(x['position'])-1 for x in schema}
    rows=[]
    for year in range(2015,2022):
        values={field:[] for field in FREDDIE_FIELDS}
        with zipfile.ZipFile(DATASETS/f'sample_{year}.zip') as z:
            name=next(n for n in z.namelist() if 'orig' in n.lower())
            for raw in z.open(name):
                f=raw.decode('latin-1').rstrip('\r\n').split('|')
                for field in FREDDIE_FIELDS:
                    try: values[field].append(float(f[positions[field]]))
                    except (ValueError,IndexError): values[field].append(np.nan)
        rows += [_stats(v,'freddie_mac',k,year) for k,v in values.items()]
    write_csv(RESULTS/'freddie_mac'/'feature_profile_selected.csv',rows)
    vals={f:[] for f in LENDING_FIELDS}
    for chunk in pd.read_csv(DATASETS/'accepted_2007_to_2018Q4.csv.gz',compression='gzip',usecols=LENDING_FIELDS,chunksize=100000):
        for f in LENDING_FIELDS: vals[f].extend(pd.to_numeric(chunk[f].astype(str).str.replace('%','',regex=False),errors='coerce').tolist())
    rows=[_stats(v,'lending_club',k,'2007_2018Q4') for k,v in vals.items()]
    write_csv(RESULTS/'lending_club'/'feature_profile_selected.csv',rows)
