import json,unittest,tempfile,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from research_checks.gate import digest,sha
import a_short_qwen_20261101.prepare as qp
import a_short_qwen_20261101.worker as qw
import a_short_qwen_20261101.complete_fit as cf
import a_short_qwen_20261101.assemble as qa
import a_short_llama_20261101.analysis as la
import a_short_llama_20261101.prepare_offline as off
CORPUS=ROOT/'analysis/A_short_replication_qwen_20261101/shared_corpus_v1.json'
def put(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x),encoding='utf-8')
def receipt(p,x):put(p,dict(payload=x,payload_sha256=digest(x)))
class Checks(unittest.TestCase):
 def test_qwen_corpus_guard_before_load(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);put(r/'cfg.json',dict(source_files=qp.SOURCE_FILES,phase='PILOT',corpus='docs.json',tokens='tokens.json',shared_corpus='shared.json'))
   put(r/'docs.json',dict(documents=[]));put(r/'tokens.json',{});put(r/'shared.json',dict(documents=[]))
   with patch.object(qw,'ROOT',r),patch.object(qw,'admission'),patch.object(qw,'Runtime',side_effect=AssertionError('runtime/model must not start')):
    with self.assertRaisesRegex(ValueError,'fixed shared corpus changed'):qw.main('cfg.json')
 def fit_fixture(self,r):
  (r/'shared.json').write_bytes(CORPUS.read_bytes());docs=[d for d in json.loads(CORPUS.read_text())['documents'] if d['split'] in ['FIT_MAP','FIT_U']]
  controls=[d['id'] for d in docs if d['split']=='FIT_MAP' and d['index']==0 and d['frame']=='F0']
  cfg=dict(study='A_SHORT_QWEN',phase='FIT',output='packet/run',corpus='docs.json',shared_corpus='shared.json',source_files=[],model_identity='model.json',control_documents=controls)
  put(r/'packet/config.json',cfg);put(r/'docs.json',dict(documents=docs));put(r/'model.json',{})
  learned=dict(P=dict(regularization=.01,n=128),U0=[[1]*8],qualified=True,model_sha256=sha(r/'model.json'),identity=dict(config='packet/config.json'))
  receipt(r/'packet/run/FIT.json',learned);receipt(r/'packet/run/controls.json',[dict(document=i,passed=True) for i in controls]);self.reseal_fit(r,cfg)
  return cfg,learned
 def reseal_fit(self,r,cfg):
  ident=dict(model=sha(r/'model.json'),code=digest(dict(sources={},config=sha(r/'packet/config.json'))))
  receipt(r/'packet/run/stage_completed.json',dict(phase=cfg['phase'],identity=ident,files={n:sha(r/'packet/run'/n) for n in ['FIT.json','controls.json']}))
 def test_qwen_fit_summary_actual_bindings(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);cfg,learned=self.fit_fixture(r)
   with patch.object(cf,'ROOT',r),patch.object(qp,'SOURCE_FILES',[]):
    self.assertTrue(cf.summarize('packet','summary.json')['technical_passed'])
    put(r/'packet/config.json',dict(cfg,phase='PILOT'))
    with self.assertRaisesRegex(ValueError,'Wrong FIT'):cf.summarize('packet','x.json')
    put(r/'packet/config.json',dict(cfg,extra='changed'))
    with self.assertRaisesRegex(ValueError,'identity mismatch'):cf.summarize('packet','x.json')
    put(r/'packet/config.json',cfg)
    receipt(r/'packet/run/FIT.json',dict(learned,P=dict(regularization=.02,n=128)));self.reseal_fit(r,cfg)
    with self.assertRaisesRegex(ValueError,'recipe mismatch'):cf.summarize('packet','x.json')
    receipt(r/'packet/run/FIT.json',learned);receipt(r/'packet/run/controls.json',[dict(document='wrong'+str(i),passed=True) for i in range(4)]);self.reseal_fit(r,cfg)
    with self.assertRaisesRegex(ValueError,'Control identities'):cf.summarize('packet','x.json')
    put(r/'shared.json',{})
    with self.assertRaisesRegex(ValueError,'shared corpus changed'):cf.summarize('packet','x.json')
 def test_assembler_scope_and_corpus_guards(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);cfg,_=self.fit_fixture(r);cfg.update(phase='PILOT');put(r/'packet/config.json',cfg)
   ident=dict(model=sha(r/'model.json'),code=digest(dict(sources={},config=sha(r/'packet/config.json'))))
   receipt(r/'packet/run/stage_completed.json',dict(phase='TEST',identity=ident,files={}))
   with patch.object(qa,'ROOT',r),patch.object(qp,'SOURCE_FILES',[]):
    with self.assertRaisesRegex(ValueError,'scope/config changed'):qa.assemble('packet','out')
   cfg=dict(model='llama',phase='PILOT',output='packet/run',corpus='docs.json');put(r/'packet/config.json',cfg)
   receipt(r/'packet/run/stage_completed.json',dict(scope='TEST',identity=dict(corpus=sha(r/'docs.json')),files={}))
   with patch.object(la,'ROOT',r):
    with self.assertRaisesRegex(ValueError,'scope/corpus changed'):la.assemble('packet','out')
    receipt(r/'packet/run/stage_completed.json',dict(scope='PILOT',identity=dict(corpus='wrong'),files={}))
    with self.assertRaisesRegex(ValueError,'scope/corpus changed'):la.assemble('packet','out')
 def test_offline_requires_accepted_original_metadata(self):
  with tempfile.TemporaryDirectory() as t:
   r=Path(t);cfg=dict(study='A',model='llama',phase='PILOT',corpus='docs.json');put(r/'packet/config.json',cfg);put(r/'docs.json',dict(documents=[]))
   source=dict(model='llama',split='PILOT',raw_packet=str(r/'packet'),arrays='arrays.npz')
   files={str(p.resolve()):sha(p) for p in [r/'packet/config.json',r/'docs.json']}
   inputs=dict(files=files,manifest_path=str(r/'arrays_manifest.json'))
   elig=dict(study='A',eligibility={'128':{},'256':{}});accepted=dict(payload=dict(files={'packet/config.json':sha(r/'packet/config.json'),'docs.json':sha(r/'docs.json')}))
   def manifests(p):return (source,inputs) if str(p).endswith('arrays_manifest.json') else (elig,dict(files={}))
   with patch.object(off,'ROOT',r),patch.object(off,'manifested_json',side_effect=manifests),patch.object(off,'validate_eligibility',return_value=True),patch.object(off,'verify_at_root',return_value=accepted):
    # Valid metadata clears new checks and reaches the next pre-existing raw-closure gate.
    with self.assertRaisesRegex(ValueError,'No source raw closure'):off.build('selector','arrays_manifest.json','elig.json','snap','review','out')
    put(r/'packet/config.json',dict(cfg,extra='modified'))
    with self.assertRaisesRegex(ValueError,'outside accepted closure'):off.build('selector','arrays_manifest.json','elig.json','snap','review','out')
    put(r/'packet/config.json',cfg);put(r/'docs.json',dict(documents=['modified']))
    with self.assertRaisesRegex(ValueError,'outside accepted closure'):off.build('selector','arrays_manifest.json','elig.json','snap','review','out')
    put(r/'docs.json',dict(documents=[]));source['model']='qwen'
    with self.assertRaisesRegex(ValueError,'relabelled'):off.build('selector','arrays_manifest.json','elig.json','snap','review','out')
if __name__=='__main__':unittest.main(verbosity=2)

