"""Fixed B normalized-input edits and forecasts, separated from truth labels.

No finite native endpoint is accepted by the forecast API. Taylor uses the
native derivative, as explicitly declared by this baseline, not finite TESTD.
"""
import numpy as np
import torch
from .baselines_b import predict as baseline_predict

DOSES=(.05,.1,.25,.5,1.,2.)


def edits(z,donor_z,direction):
    z=torch.as_tensor(z,dtype=torch.float32);donor_z=torch.as_tensor(donor_z,dtype=torch.float32)
    w=torch.as_tensor(direction,dtype=torch.float32)
    if z.ndim!=1 or z.shape!=donor_z.shape or z.shape!=w.shape:raise ValueError('incompatibleBcoordinates')
    if not all(torch.isfinite(x).all() for x in [z,donor_z,w]):raise ValueError('nonfiniteBcoordinates')
    if not torch.isclose(w.norm(),torch.tensor(1.),atol=1e-6,rtol=0):raise ValueError('projectiondirectionnotunit')
    full=donor_z-z;projected=(full@w)*w
    return dict(full=full,projected=projected)


def forecasts(tc,z,delta,taylor_direction,c,learned_cell=None,recipient_class=None,tc_base=None):
    """One condition; caller may cache/reuse TCbase across all12conditions."""
    z=torch.as_tensor(z,dtype=torch.float32);dx=c*torch.as_tensor(delta,dtype=torch.float32)
    t0,pre0,m0=tc.forward(z) if tc_base is None else tc_base
    t1,_,_=tc.forward(z+dx)
    frozen=((dx@tc.wenc)*m0)@tc.wdec
    if tc.skip is not None:frozen=frozen+dx@tc.skip
    pred=dict(TC=t1-t0,FROZEN=frozen,TAYLOR=c*torch.as_tensor(taylor_direction,dtype=torch.float32),ZERO=torch.zeros_like(z))
    if learned_cell is not None:
        for k,v in baseline_predict(learned_cell,dx.double().numpy(),recipient_class).items():
            pred[k.upper()]=torch.as_tensor(v,dtype=torch.float32)
    if any(v.shape!=z.shape or not torch.isfinite(v).all() for v in pred.values()):raise ValueError('invalidBforecast')
    return pred,dict(tc0=t0,tc1=t1,input_delta=dx,tc_base=(t0,pre0,m0))


def endpoint_decomposition(tc0,tc1,native0,native1):
    t0,t1,n0,n1=[torch.as_tensor(x,dtype=torch.float64) for x in [tc0,tc1,native0,native1]]
    e0,e1=t0-n0,t1-n1;de=(t1-t0)-(n1-n0)
    return dict(e0=e0,e1=e1,energy0=float(e0@e0),energy1=float(e1@e1),mixed=float(-2*(e1@e0)),
                error_energy=float(de@de),identity_max=float((de-(e1-e0)).abs().max()))


def readout_metrics(predicted_changes,native_change,gradient,vector_truth):
    """Finite margin predictions are supplied from the same native suffix."""
    g=np.asarray(gradient,np.float64);d=np.asarray(vector_truth,np.float64)
    return {name:dict(finite_margin_loss=float((float(row['finite'])-native_change)**2),
         vector_error=float(np.sum((np.asarray(row['vector'],np.float64)-d)**2)),
         linear_vs_native_linear=float((g@np.asarray(row['vector'],np.float64)-g@d)**2),
         linear_vs_native_finite=float((g@np.asarray(row['vector'],np.float64)-native_change)**2))
         for name,row in predicted_changes.items()}
