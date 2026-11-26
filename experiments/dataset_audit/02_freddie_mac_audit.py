"""Audita lacunas de períodos mensais nas amostras Freddie Mac."""
import zipfile
from collections import defaultdict
from src.fhe_credit.dataset_audit.runner import DATASETS, RESULTS, write_csv

def month(v):
    return int(v[:4])*12+int(v[4:]) if len(v)==6 and v.isdigit() else None

rows=[]
for year in range(2015,2022):
    periods=defaultdict(list)
    with zipfile.ZipFile(DATASETS/f'sample_{year}.zip') as z:
        n=next(x for x in z.namelist() if 'perf' in x.lower())
        for raw in z.open(n):
            f=raw.decode('latin-1').rstrip('\r\n').split('|'); p=month(f[1])
            if p is not None: periods[f[0]].append(p)
    gaps=[]
    for values in periods.values():
        s=sorted(set(values)); gaps += [b-a-1 for a,b in zip(s,s[1:]) if b-a>1]
    rows.append({'dataset':'freddie_mac','vintage':year,'loans':len(periods),'loans_with_gap':sum(1 for v in periods.values() if any(b-a>1 for a,b in zip(sorted(set(v)),sorted(set(v))[1:]))),'gap_intervals':len(gaps),'missing_months_within_gaps':sum(gaps),'max_gap_months':max(gaps,default=0),'note':'Lacuna entre períodos reportados; não infere ausência de evento.'})
write_csv(RESULTS/'freddie_mac'/'monthly_gaps.csv',rows)
print(rows)
