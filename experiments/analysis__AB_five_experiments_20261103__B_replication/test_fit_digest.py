import tempfile,json
from pathlib import Path
from .fit_digest_resume import ExactFitMemo
from research_checks.gate import digest
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'fit.json';p.write_text('{"cells":{"x":[1,2,3]},"fit_ids":[1]}')
    calls=[]
    def real(v):calls.append(1);return digest(v)
    m=ExactFitMemo(lambda p:json.loads(Path(p).read_text()),real,p)
    v=m.unwrap(p);expected=digest(v)
    for _ in range(1536):assert m.digest(v)==expected
    assert len(calls)==1 and m.hits==1536
    assert m.digest(dict(v))==expected and len(calls)==2
    m.verify();v['cells']['x'][0]=99
    try:m.verify()
    except ValueError:pass
    else:raise AssertionError('Mutated FIT not rejected')
result=dict(passed=True,trained_calls=0,exact_cached_hash=True,identity_only=True,mutated_fit_rejected=True,metadata_serializations_saved=1535)
(Path(__file__).parent/'fit_digest_test.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
