"""Test a proposed gate in memory; never modify/import it as the live gate."""
import json, tempfile, types, unittest, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE/'proposed_gate.py.txt').read_text()
gate=types.ModuleType('research_checks.proposed_offline_gate');gate.__package__='research_checks'
exec(compile(source,str(HERE/'proposed_gate.py.txt'),'exec'),gate.__dict__)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for name in ['AGENTS.md','plans/RESEARCH_REVIEW_POLICY.md','research_checks/__init__.py','worker.py']:
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('# fixture')
  self.obj=dict(schema_version=1,id='offline',kind='experiment',primary_agent='author',purpose='pure NumPy calibration; no model calls',tracked_files=['worker.py'],tracked_trees=[],input_manifests=[],gates=[dict(id=k,category=k,evidence='evidence.json',pointer='/ok',op='eq',expected=True,reason='fixture') for k in gate.REQUIRED_CATEGORIES],circuits=[],structural_scope='No model or reduced circuit; fixed simulation budget is separate evidence',entrypoint=dict(module='worker',args=[]),schedule='schedule.json',budget=dict(forward=0,backward=0))
  self.write('evidence.json',dict(ok=True));self.write('schedule.json',dict(operations=[]))
 def write(self,p,obj):(self.root/p).write_text(json.dumps(obj))
 def check(self):
  self.write('contract.json',self.obj);return gate.preflight(self.root,'contract.json')
 def test_empty_zero_accepted(self):self.assertTrue(self.check()['ok'])
 def test_empty_positive_rejected(self):
  for k in ['forward','backward']:
   self.obj['budget']=dict(forward=0,backward=0);self.obj['budget'][k]=1
   with self.assertRaises(ValueError):self.check()
 def test_malformed_empty_rejected(self):
  for value in [None,{},'',0]:
   self.write('schedule.json',dict(operations=value))
   with self.assertRaises(ValueError):self.check()
 def test_nonempty_zero_exceeds_budget(self):
  self.write('schedule.json',dict(operations=[dict(id='a',kind='forward')]))
  self.assertFalse(self.check()['ok'])
 def test_normal_model_schedule_unchanged(self):
  self.obj['budget']['forward']=1;self.write('schedule.json',dict(operations=[dict(id='a',kind='forward')]))
  self.assertTrue(self.check()['ok'])
 def test_evidence_still_required(self):
  self.write('evidence.json',dict(ok=False));self.assertFalse(self.check()['ok'])
  self.obj['gates'].pop()
  with self.assertRaises(ValueError):self.check()
 def test_maintenance_cannot_launch(self):
  self.obj['kind']='maintenance'
  with self.assertRaises(ValueError):self.check()
if __name__=='__main__':unittest.main(verbosity=2)
