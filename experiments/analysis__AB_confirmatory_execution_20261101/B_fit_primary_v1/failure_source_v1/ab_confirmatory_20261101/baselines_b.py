"""Secondary B vector-only FIT baselines; no TEST deltas/readout labels."""
import numpy as np


def compact_ridge(dx,delta,regularization=.01):
    x,y=np.asarray(dx,np.float64),np.asarray(delta,np.float64)
    if x.ndim!=2 or y.ndim!=2 or min(x.shape)<=0 or min(y.shape)<=0 or len(x)!=len(y):
        raise ValueError('empty/incompatible baselineFIT')
    if not np.isfinite(x).all() or not np.isfinite(y).all() or not np.isfinite(regularization) or regularization<=0:
        raise ValueError('invalid baselineFIT')
    scale=float(np.sqrt(np.mean(x*x)))
    if not np.isfinite(scale) or scale<=0:raise ValueError('zero/nonfinite baseline inputRMS')
    z=x/scale;zm=z.mean(0);ym=y.mean(0);a=z-zm
    dual=np.linalg.solve(a@a.T+len(a)*regularization*np.eye(len(a)),y-ym)
    if not np.isfinite(dual).all():raise ValueError('nonfinite baselinefit')
    return dict(a=a,dual=dual,zm=zm,ym=ym,scale=scale,regularization=regularization,n=len(x))


def predict_ridge(fit,dx):
    a,dual,zm,ym=[np.asarray(fit[k],np.float64) for k in ['a','dual','zm','ym']]
    return (np.asarray(dx,np.float64)/fit['scale']-zm)@a.T@dual+ym


def fit_cell(dx,delta,classes):
    x,y,c=np.asarray(dx,np.float64),np.asarray(delta,np.float64),np.asarray(classes)
    if len(x)!=len(y) or len(x)!=len(c) or set(c)!={0,1}:raise ValueError('missingFITrecipientclass')
    if np.sum(c==0)!=np.sum(c==1):raise ValueError('unequalFITsideweights')
    return dict(ridge=compact_ridge(x,y),means={str(i):y[c==i].mean(0) for i in [0,1]},n=len(x),
                label_scope='native vector delta only; no margin labels; class-cell mean has additional known recipient-class feature')


def predict(cell,dx,recipient_class):
    if str(recipient_class) not in cell['means']:raise ValueError('unknownrecipientclass')
    return dict(mean=np.asarray(cell['means'][str(recipient_class)],np.float64),ridge=predict_ridge(cell['ridge'],dx))
