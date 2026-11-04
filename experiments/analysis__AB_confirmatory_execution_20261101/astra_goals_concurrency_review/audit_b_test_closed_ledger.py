import hashlib,json
from pathlib import Path
from collections import Counter
from research_checks.gate import digest
R=Path.cwd();P=R/'analysis/AB_confirmatory_execution_20261101/B_descriptive_TEST_v8';O=Path(__file__).parent/'b_test_descriptive_closed_recipients'
c=json.loads((P/'run/stage_completed.json').read_text());assert digest(c['payload'])==c['payload_sha256'] and c['payload']['phase']=='TEST'
planned=json.loads((P/'operations.json').read_text())['operations'];kinds={x['id']:x['kind'] for x in planned};assert len(kinds)==159744
attempts={};computed={};coupled=set();h=hashlib.sha256();events=Counter()
with (P/'run/ledger.jsonl').open('rb') as f:
 for line in f:
  h.update(line);q=json.loads(line);r=q['record'];assert digest(r)==q['sha256'];events[r['event']]+=1
  if r['event']=='attempt':
   assert r['operation'] not in attempts and r['kind']==kinds[r['operation']];attempts[r['operation']]=r['request']
  elif r['event']=='computed':
   assert r['operation'] not in computed;computed[r['operation']]=r['request']
   for op in r['coupled_operations']:
    assert op not in coupled and op in kinds;coupled.add(op)
  else:raise AssertionError('Unexpected ledger event '+r['event'])
assert set(attempts)==set(kinds)==coupled and len(computed)==158208
assert all(attempts[o]==request for o,request in computed.items())
assert h.hexdigest()==c['payload']['files']['ledger.jsonl']
q=dict(passed=True,stage_completed_sha256=hashlib.sha256((P/'run/stage_completed.json').read_bytes()).hexdigest(),ledger_sha256=h.hexdigest(),events=dict(events),logical_operations=len(attempts),computed_callbacks=len(computed),coupled_accounted_operations=len(coupled),operation_kinds=dict(Counter(kinds.values())),duplicate_attempts=0,duplicate_callbacks=0,unknown_events=0,scope='Actual closed ledger only; all eventdigests/operationids/requests/kinds/coupling checked againstoriginalschedule andproducersseal. No liveledger/model/bootstrap.')
(O/'closed_ledger_review.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
