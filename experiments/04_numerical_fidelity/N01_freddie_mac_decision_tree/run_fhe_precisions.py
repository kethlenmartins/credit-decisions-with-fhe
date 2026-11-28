"""Run only FHE 9/10-bit checks from one completed N01 run; no data ingestion or training."""
import argparse, json, time
from pathlib import Path
import joblib, numpy as np
from concrete.ml.sklearn import DecisionTreeClassifier

def err(a,b):
 d=np.asarray(a)-np.asarray(b); return {'mae':float(np.mean(abs(d))),'rmse':float(np.sqrt(np.mean(d*d))),'max_absolute_error':float(np.max(abs(d))),'mean_signed_error':float(np.mean(d))}
def main():
 p=argparse.ArgumentParser(); p.add_argument('--run-directory',type=Path,required=True); p.add_argument('--output',type=Path,required=True); p.add_argument('--bits',type=int,nargs='+',default=[9,10]); a=p.parse_args()
 d=np.load(a.run_directory/'prepared_dataset.npz'); model=joblib.load(a.run_directory/'sklearn_model.joblib'); rng=np.random.default_rng(42); cal=d['X_train'][rng.choice(len(d['X_train']),1000,replace=False)]; x=d['X_test'][:5]; ref=model.predict_proba(x)[:,1]; out={'source_run_id':a.run_directory.name,'selection':'first five prepared test observations, identical strategy to N01','results':{}}
 for bits in a.bits:
  try:
   m=DecisionTreeClassifier.from_sklearn_model(model,X=cal,n_bits=bits); q=m.predict_proba(x,fhe='disable')[:,1]
   t=time.perf_counter(); circuit=m.compile(cal); compile_s=time.perf_counter()-t
   t=time.perf_counter(); sim=m.predict_proba(x,fhe='simulate')[:,1]; sim_s=time.perf_counter()-t
   t=time.perf_counter(); fhe=m.predict_proba(x,fhe='execute')[:,1]; fhe_s=time.perf_counter()-t
   out['results'][str(bits)]={'status':'COMPLETED','compilation_seconds':compile_s,'simulate_seconds':sim_s,'execute_total_seconds':fhe_s,'key_generation':'not isolated by high-level API','error_quant_minus_reference':err(q,ref),'error_sim_minus_quant':err(sim,q),'error_fhe_minus_quant':err(fhe,q),'error_fhe_minus_reference':err(fhe,ref),'class_agreement_fhe_quant':float(np.mean((fhe>=.5)==(q>=.5))),'circuit_statistics':str(getattr(circuit,'statistics',None))}
  except Exception as e: out['results'][str(bits)]={'status':'FAILED','error_type':type(e).__name__,'message':str(e)[:300]}
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2)+'\n'); print(a.output)
if __name__=='__main__': main()
