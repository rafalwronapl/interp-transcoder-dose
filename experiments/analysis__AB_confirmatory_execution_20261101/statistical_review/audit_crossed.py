"""Independent inexpensive audit of current crossed percentile interval.

No model calls. Degenerate in TEST dimension, valid random FIT effects:
x_ij=a_i; all population uncertainty comes from drawing new FIT cohorts.
"""
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from ab_confirmatory_20261101.statistics import crossed_summary


def main():
    rng=np.random.default_rng(761104)
    rows=[]
    for distribution in ('normal','t3'):
        covers=0;reps=500;draws=999
        for i in range(reps):
            a=rng.normal(size=8) if distribution=='normal' else rng.standard_t(3,size=8)/np.sqrt(3)
            x=np.repeat(a[:,None],4,axis=1)
            z=crossed_summary(x,draws=draws,seed=791000+i)
            covers+=z['ci'][0]<=0<=z['ci'][1]
        p=covers/reps
        rows.append(dict(distribution=distribution,fit_cohorts=8,test_blocks=4,
                         reps=reps,draws=draws,coverage=p,
                         mc_se=float(np.sqrt(p*(1-p)/reps))))
    (Path(__file__).parent/'crossed_coverage.json').write_text(json.dumps(dict(
        seed=761104,scope='Independent stress test of current percentile crossed bootstrap; all variation from iid FIT effects, TEST columns identical.',rows=rows),indent=2))
    print(rows)


if __name__=='__main__':main()
