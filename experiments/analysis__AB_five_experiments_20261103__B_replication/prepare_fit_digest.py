from pathlib import Path
import json
from research_checks.gate import read,sha
from concurrency_a270_q06_20261102 import process_table
H=Path(__file__).resolve().parent;R=H.parents[2];rel=lambda p:p.relative_to(R).as_posix()
def put(n,x):(H/n).write_text(json.dumps(x,indent=2)+'\n')
table=process_table();status=read(H/'run/STATUS.json');assert status['logical_attempts']==22129 and status['completed']<370
put('fit_digest_handoff.json',dict(child=14756,processes=[table[20808],table[14756]],ledger_sha256=sha(H/'run/ledger.jsonl'),lock_sha256=sha(R/'operations/research_worker.lock'),observed_status=status,scope='Stop only exact B child while at least13 cached contexts remain; no active inference interrupted. Same1B replacement beside alreadyrunning A, no third model.'))
c=read(H/'resume_contract.json');c['id']+='_FIT_DIGEST';c['primary_agent']='/root/b_second_artifact_five';c['purpose']='Exact immutableFIT digest memoization and safe cache-only handoff; unchanged numericalworker and cacheidentity, no repeated inference.'
c['tracked_files'] += [rel(H/n) for n in ['fit_digest_resume.py','test_fit_digest.py','fit_digest_test.json','launch_fit_digest.py','prepare_fit_digest.py','fit_digest_handoff.json']]
c['entrypoint']=dict(module='analysis.AB_five_experiments_20261103.B_replication.fit_digest_resume',args=[])
c['gates'].append(dict(id='exact_fit_memo',category='restart',evidence=rel(H/'fit_digest_test.json'),pointer='/passed',op='eq',expected=True,reason='Identical digest1536hits; only exactobjectmemoized, mutation rejected beforecompletionseal; original numericalworker unchanged.'))
put('fit_digest_contract.json',c)
