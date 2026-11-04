from pathlib import Path
from analysis.B_norm_control_20261103.common import read,sha,digest,unwrap,put,source,group_vector,normalize_targets
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ARMS=['top32']+['control_'+str(s) for s in range(20261103,20261108)]
def verify():
    for name,h in read(HERE/'input_manifest.json')['files'].items():
        assert sha(ROOT/name)==h,'Changed input '+name
