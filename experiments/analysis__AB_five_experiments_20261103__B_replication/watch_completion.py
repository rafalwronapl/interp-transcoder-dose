"""Bounded passive watcher; prepare offline completion packet after durable finish."""
import json,time,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
start=time.monotonic()
while time.monotonic()-start<8*3600:
 if (HERE/'run/completed.json').exists():
  result=subprocess.run([sys.executable,'-m','analysis.AB_five_experiments_20261103.B_replication.complete'],cwd=ROOT,capture_output=True,text=True)
  (HERE/'completion_prepare.log').write_text(result.stdout+result.stderr)
  if result.returncode==0:
   rel=HERE.relative_to(ROOT).as_posix()
   result=subprocess.run([sys.executable,'-m','research_checks','snapshot',rel+'/completion_contract.json','--phase','completion','--out',rel+'/completion_snapshot.json'],cwd=ROOT,capture_output=True,text=True)
   (HERE/'completion_snapshot.log').write_text(result.stdout+result.stderr)
  (HERE/'completion_watcher_exit.json').write_text(json.dumps(dict(returncode=result.returncode,elapsed=time.monotonic()-start)))
  sys.exit(result.returncode)
 time.sleep(30)
(HERE/'completion_watcher_exit.json').write_text(json.dumps(dict(returncode=2,reason='Bounded8hour timeout; worker untouched')))
