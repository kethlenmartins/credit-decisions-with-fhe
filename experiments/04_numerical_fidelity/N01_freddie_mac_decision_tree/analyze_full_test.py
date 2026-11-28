"""Private N01-G/H/I derived analysis over the persisted full test matrix."""
import argparse,json
from pathlib import Path
import joblib,numpy as np
from scipy.stats import kendalltau,spearmanr
from sklearn.metrics import roc_auc_score,average_precision_score,brier_score_loss,log_loss

def main():
 p=argparse.ArgumentParser();p.add_argument('--run-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 from concrete.ml.sklearn import DecisionTreeClassifier
 d=np.load(a.run_directory/'prepared_dataset.npz');m=joblib.load(a.run_directory/'sklearn_model.joblib');X,y=d['X_test'],d['y_test']; ref=m.predict_proba(X)[:,1]; leaves=m.apply(X); cal=d['X_train'][np.random.default_rng(42).choice(len(d['X_train']),1000,False)]; w=X[:,4]
 out={'source_run_id':a.run_directory.name,'n':len(y),'reference_leaf_distribution':{str(k):int(v) for k,v in zip(*np.unique(leaves,return_counts=True))},'results':{}}
 for b in (3,7,8,9,10,12):
  q=DecisionTreeClassifier.from_sklearn_model(m,X=cal,n_bits=b).predict_proba(X,fhe='disable')[:,1]; vals=np.unique(np.r_[0,1,ref,q]); area=area_w=0;mx=mxw=0;ints=[]
  for l,r in zip(vals[:-1],vals[1:]):
   t=(l+r)/2;dd=(ref<=t)!=(q<=t); z=float(dd.mean());zw=float(np.average(dd,weights=w));area+=z*(r-l);area_w+=zw*(r-l)
   if z>=mx: mx=z;ints=[float(l),float(r)]
   mxw=max(mxw,zw)
  matrix={}
  for leaf in np.unique(leaves):
   z=q[leaves==leaf];u,c=np.unique(z,return_counts=True);matrix[str(leaf)]={'reference_probability':float(ref[leaves==leaf][0]),'n':int(len(z)),'adapted_probabilities':[{'value':float(x),'count':int(n)} for x,n in zip(u,c)]}
  e=q-ref;out['results'][str(b)]={'metrics':{'roc_auc':float(roc_auc_score(y,q)),'average_precision':float(average_precision_score(y,q)),'brier':float(brier_score_loss(y,q)),'log_loss':float(log_loss(y,q,labels=[0,1])),'mae':float(np.mean(abs(e))),'rmse':float(np.sqrt(np.mean(e*e))),'max_absolute_error':float(np.max(abs(e))),'distinct':int(len(np.unique(q))),'spearman':None if len(np.unique(q))<2 else float(spearmanr(ref,q).statistic),'kendall':None if len(np.unique(q))<2 else float(kendalltau(ref,q).statistic)},'ddr':{'max':mx,'max_interval':ints,'area':area,'identity_error':float(area-np.mean(abs(e)))},'weighted':{'mae':float(np.average(abs(e),weights=w)),'ddr_max':mxw,'area':area_w,'identity_error':float(area_w-np.average(abs(e),weights=w))},'leaf_probability_matrix':matrix}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(a.output)
if __name__=='__main__':main()
