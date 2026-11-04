"""Pure counterfactual constructions. No trained-model evaluation."""
import numpy as np

ARMS=('ONLY_top','EXCEPT_top','ONLY_random','EXCEPT_random','ON','OFF','BASE')

def residual_target(native,original,partner_native,partner_tc):
    n,t,p,q=map(lambda x:np.asarray(x,dtype=np.float64),(native,original,partner_native,partner_tc))
    r=t-n;s=q-p;nr=float(np.linalg.norm(r));ns=float(np.linalg.norm(s))
    if ns==0:return None,dict(norm=nr,partner_norm=ns,undefined=True)
    target=(n+nr*s/ns).astype(np.float32)
    return target,dict(norm=nr,partner_norm=ns,actual_norm=float(np.linalg.norm(target.astype(float)-n)),undefined=False)

def feature_arms(pre0,pre1,threshold,top,random):
    a,b,th=map(lambda x:np.asarray(x,dtype=np.float64),(pre0,pre1,threshold))
    m0=a>th;m1=b>th;positive=np.maximum(b,0);base=positive*m0
    switch=positive*(m1.astype(float)-m0.astype(float))
    t=np.zeros(len(a),bool);t[top]=True;r=np.zeros(len(a),bool);r[random]=True
    masks=dict(ONLY_top=t,EXCEPT_top=~t,ONLY_random=r,EXCEPT_random=~r,
               ON=(~m0)&m1,OFF=m0&(~m1),BASE=np.zeros(len(a),bool))
    return {k:(base+switch*v).astype(np.float32) for k,v in masks.items()},dict(
        switches=int(np.sum(m0!=m1)),on=int(np.sum((~m0)&m1)),off=int(np.sum(m0&(~m1))),
        top_switches=int(np.sum((m0!=m1)&t)),random_switches=int(np.sum((m0!=m1)&r)))
