"""Cheap synthetic end-to-end and actual generic adapter tests, no pretrained model."""
import json,tempfile,unittest,subprocess,sys
from pathlib import Path
import numpy as np
from analysis.AB_five_experiments_20261103.B_replication.worker import operations,measure,unwrap,HERE
from analysis.Qwen06_ABC_extension_20261102.bundle_runtime import BundleRuntime
from research_checks.gate import digest

class Fake:
 def __init__(self):self.calls=0
 def capture(self,ids):
  self.calls+=1;x=np.array([ids[0],ids[0]*.3+1,2.,-.2]);y=x+x*x*.1
  return dict(states=dict(x=x.tolist(),y=y.tolist(),margin=float(y@np.array([.2,-.4,.1,.3]))))
 def controls(self,*a):self.calls+=9;return dict(passed=True)
 def branch(self,x):self.calls+=1;return np.asarray(x)+np.asarray(x)**2*.1
 def jvp(self,x,v):self.calls+=1;return np.asarray(x)+np.asarray(x)**2*.1,(1+np.asarray(x)*.2)*v
 def tc(self,x):self.calls+=1;return np.asarray(x)+np.asarray(x)**2*.09
 def frozen(self,x,v):self.calls+=1;return (1+np.asarray(x)*.18)*v
 def margin(self,r,y):self.calls+=1;return float(np.asarray(y)@np.array([.2,-.4,.1,.3]))

class Tests(unittest.TestCase):
 def test_end_to_end(self):
  docs=[];tokens={}
  for split,n in [('FIT',2),('TEST',2)]:
   for b in range(n):
    for frame in (['so','when'] if split=='FIT' else ['so','when','transfer']):
     for side in [0,1]:
      i=f'{split}{b}{frame}{side}';docs.append(dict(id=i,donor=f'{split}{b}{frame}{1-side}',block=f'{split}{b}',split=split,frame=frame,side=side));tokens[i]=[b+side+1]
  cfg=dict(answer_ids=[1,2],controls=[docs[0]['id']],gates=dict(branch_relative=1e-4));ops=operations(docs,cfg['controls'])
  with tempfile.TemporaryDirectory() as td:
   out=Path(td);identity=dict(model='fake',code='fixture');runtime=BundleRuntime(out,identity,ops);eng=Fake()
   result=measure(cfg,eng,runtime,docs,tokens,out)
   self.assertEqual(eng.calls,len(ops['operations']));self.assertEqual(result['logical_forward'],len(ops['operations']));self.assertEqual(result['cells'],144)
   original={str(p.relative_to(out)):p.read_bytes() for p in out.rglob('*') if p.is_file() and p.name!='STATUS.json'}
   eng2=Fake();measure(cfg,eng2,BundleRuntime(out,identity,ops),docs,tokens,out);self.assertEqual(eng2.calls,0)
   self.assertTrue(all((out/p).read_bytes()==v for p,v in original.items()))
   # Lost bundle receipt reconstructs from durable cache without measurement.
   receipt=next((out/'bundles').glob('*.json'));receipt.unlink()
   eng3=Fake();measure(cfg,eng3,BundleRuntime(out,identity,ops),docs,tokens,out);self.assertEqual(eng3.calls,0)
   cache=next((out/'cache').glob('*.json'));cache.write_text('{}')
   with self.assertRaises((KeyError,ValueError)):measure(cfg,Fake(),BundleRuntime(out,identity,ops),docs,tokens,out)
 def test_uncertain_attempt(self):
  with tempfile.TemporaryDirectory() as td:
   ops=dict(operations=[dict(id='x',kind='forward')]);ident=dict(model='m',code='c');r=BundleRuntime(Path(td),ident,ops)
   def crash():raise RuntimeError('simulated')
   with self.assertRaises(RuntimeError):r.compute('x',{},dict(mode='x'),{},crash)
   with self.assertRaises(ValueError):BundleRuntime(Path(td),ident,ops).compute('x',{},dict(mode='x'),{},lambda:1)

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
 if not result.wasSuccessful():sys.exit(1)
 # Existing synthetic torch fixtures instantiate random tiny native models,
 # exercising actual hook boundaries, dynamic tail and TC formula.
 p=subprocess.run([sys.executable,'-m','unittest','ab_confirmatory_20261101.test_native_tail_b','ab_confirmatory_20261101.test_transcoder'],capture_output=True,text=True)
 print(p.stdout,p.stderr)
 if p.returncode:sys.exit(p.returncode)
 corpus=json.loads((HERE/'corpus.json').read_text());cfg=json.loads((HERE/'config.json').read_text());docs=corpus['documents']
 assert len(docs)==1664 and len([d for d in docs if d['split']=='TEST'])==1536
 assert set(d['donor'] for d in docs)==set(d['id'] for d in docs)
 fit={w for b in corpus['blocks'] if b['split']=='FIT' for w in b['words']};test={w for b in corpus['blocks'] if b['split']=='TEST' for w in b['words']};assert not fit&test
 (HERE/'test_evidence.json').write_text(json.dumps(dict(hooks=True,data=True,pilot=True,accounting=True,restart=True,
  synthetic_end_to_end_cases=result.testsRun,actual_adapter_fixtures_exit=p.returncode,model_calls=0,
  note='Pilot field certifies planned ordered FIT technicalchecks in testedrunner, not completed pretrained pilot.'),indent=2)+'\n')
