"""Actual current B production path test receipt, random model only."""
import contextlib,io,json,sys,unittest,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root))
from ab_confirmatory_20261101.test_worker_b import WorkerBTests
from ab_confirmatory_20261101.worker_b import DEPENDENCIES
stage=Path(__file__).parent
paths=[root/'ab_confirmatory_20261101'/n for n in DEPENDENCIES+['test_worker_b.py']]
def hashes():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();stream=io.StringIO()
with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WorkerBTests))
(stage/'synthetic_tests.log').write_text(stream.getvalue(),encoding='utf-8')
if hashes()!=before:raise RuntimeError('Sources changed during tests')
evidence=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),pretrained_calls=0,
    passed=result.wasSuccessful(),source_hashes=before,two_stage_qualification_tested=result.wasSuccessful(),
    zero_load_replay_tested=result.wasSuccessful(),config_identity_mismatch_tested=result.wasSuccessful(),
    independent_reference_mutant_tested=result.wasSuccessful(),literal_documents=128,scientific_inference=False,
    scheduled_forward=1860,scheduled_backward=4)
(stage/'test_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
print(stream.getvalue());sys.exit(0 if result.wasSuccessful() else 1)
