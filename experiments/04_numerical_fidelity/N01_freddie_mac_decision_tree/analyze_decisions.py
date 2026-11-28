"""Exact exploratory cutoff stability from paired N01 score vectors."""
import argparse, json
from pathlib import Path
import joblib, numpy as np
from concrete.ml.sklearn import DecisionTreeClassifier

def summarize(ref, quant):
    values=np.unique(np.r_[0.,1.,ref,quant]); rows=[]; area=0.; max_ddr=-1.; max_intervals=[]
    def row(tau, kind):
        a=ref<=tau; b=quant<=tau; d=a!=b; margin=np.abs(ref-tau); err=np.abs(quant-ref)
        return {'tau':float(tau),'kind':kind,'ddr':float(d.mean()),'approval_reference':float(a.mean()),'approval_quantized':float(b.mean()),'approval_difference_signed':float(b.mean()-a.mean()),'approval_difference_absolute':float(abs(b.mean()-a.mean())),'approval_to_rejection':float((a&~b).mean()),'rejection_to_approval':float((~a&b).mean()),'margin_bound_empirical':float((margin<=err).mean()),'margin_bound_max_error':float((margin<=err.max()).mean())}
    for left,right in zip(values[:-1],values[1:]):
        if right>left:
            item=row((left+right)/2,'interval'); item['left']=float(left); item['right']=float(right); rows.append(item); area+=item['ddr']*(right-left)
            if item['ddr']>max_ddr+1e-15: max_ddr=item['ddr']; max_intervals=[item]
            elif abs(item['ddr']-max_ddr)<=1e-15: max_intervals.append(item)
    boundaries=[row(x,'boundary') for x in values]
    return {'n':len(ref),'mae':float(np.mean(abs(quant-ref))),'area_under_ddr':float(area),'identity_error':float(area-np.mean(abs(quant-ref))),'tolerance':1e-12,'maximum_ddr':float(max_ddr),'maximum_ddr_intervals':max_intervals,'positive_ddr_intervals':[x for x in rows if x['ddr']>0],'intervals':rows,'boundaries':boundaries}

def main():
 p=argparse.ArgumentParser(); p.add_argument('--run-directory',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
 d=np.load(a.run_directory/'prepared_dataset.npz'); model=joblib.load(a.run_directory/'sklearn_model.joblib'); x=d['X_test'][:10000]; cal=d['X_train'][np.random.default_rng(42).choice(len(d['X_train']),1000,False)]; ref=model.predict_proba(x)[:,1]
 out={'source_run_id':a.run_directory.name,'decision':'approve iff p <= tau','n':len(x),'results':{}}
 for bits in range(3,13):
  try: out['results'][str(bits)]=summarize(ref,DecisionTreeClassifier.from_sklearn_model(model,X=cal,n_bits=bits).predict_proba(x,fhe='disable')[:,1])
  except Exception as e: out['results'][str(bits)]={'status':'FAILED','error_type':type(e).__name__}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(a.output)
if __name__=='__main__': main()
