"""Independent crossed random-effects percentile-bootstrap stress screen."""
import json
from pathlib import Path
import numpy as np


def main():
    rng=np.random.default_rng(961104)
    rows=[];reps=500;draws=999;n=32
    for fits in (8,16):
        for distribution in ('normal','t3'):
            for structure in ('fit_dominant','additive','interaction'):
                cov95=cov99=0
                for i in range(reps):
                    def rv(shape):
                        return rng.normal(size=shape) if distribution=='normal' else rng.standard_t(3,size=shape)/np.sqrt(3)
                    r=rv((fits,));c=rv((n,));e=rv((fits,n))
                    if structure=='fit_dominant':c*=.01;e*=.01
                    if structure=='interaction':r*=.01;c*=.01
                    ir=rng.integers(fits,size=(draws,fits));ic=rng.integers(n,size=(draws,n))
                    z=r[ir].mean(1)+c[ic].mean(1)+e[ir[:,:,None],ic[:,None,:]].mean((1,2))
                    q=np.quantile(z,[.005,.025,.975,.995])
                    cov95+=q[1]<=0<=q[2];cov99+=q[0]<=0<=q[3]
                row=dict(fits=fits,test_blocks=n,distribution=distribution,structure=structure,reps=reps,draws=draws)
                for label,k in [('coverage95',cov95),('coverage99',cov99)]:
                    p=k/reps;row[label]=p;row[label+'_mc_se']=float(np.sqrt(p*(1-p)/reps))
                rows.append(row)
                (Path(__file__).parent/'crossed_stress_screen.json').write_text(json.dumps(dict(seed=961104,scope='Offline random-effects screen, not final size calibration. Crossed row/column resampling equivalent to production crossed_summary, with95/99percentile intervals.',rows=rows),indent=2))
                print(row,flush=True)


if __name__=='__main__':main()
