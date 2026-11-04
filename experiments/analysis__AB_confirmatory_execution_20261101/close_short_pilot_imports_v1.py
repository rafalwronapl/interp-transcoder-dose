"""Execution metadata only: bind static local imports before PILOT snapshot."""
from pathlib import Path
import ast,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
def sha(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def local(name):
 parts=name.split('.') if name else [];found=[]
 for i in range(1,len(parts)+1):
  init=ROOT.joinpath(*parts[:i],'__init__.py')
  if init.is_file():found.append(init)
 if parts:
  module=ROOT.joinpath(*parts).with_suffix('.py')
  if module.is_file():found.append(module)
 return found
def closure(seeds):
 pending=[ROOT/n for n in seeds if n.endswith('.py')];seen=set()
 while pending:
  path=pending.pop().resolve()
  if path in seen or not path.is_file():continue
  path.relative_to(ROOT);seen.add(path)
  parts=path.relative_to(ROOT).with_suffix('').parts
  package=list(parts[:-1])
  for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path))):
   names=[]
   if isinstance(node,ast.Import):names=[a.name for a in node.names]
   elif isinstance(node,ast.ImportFrom):
    base=package[:len(package)-(node.level-1)] if node.level else []
    if node.module:base+=node.module.split('.')
    name='.'.join(base);names=[name]+[name+'.'+a.name for a in node.names if a.name!='*' and name]
   for name in names:
    pending.extend(local(name))
 return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(seen)}
def main():
 for model in ['qwen','llama']:
  folder=ROOT/f'analysis/A_short_replication_{model}_20261101/PILOT_ready_v1';contract=folder/'contract.json'
  old=contract.read_bytes();obj=json.loads(old);original=list(obj['tracked_files']);bound=closure(original)
  additions=sorted(set(bound)-set(original))
  backup=folder/'contract_builder_v1.json';receipt=folder/'source_closure_addition_v1.json'
  if backup.exists() or receipt.exists():raise ValueError('Existing closure evidence; do not repeat')
  backup.write_bytes(old);obj['tracked_files']+=additions
  assert contract.read_bytes()==old,'Concurrent contract mutation'
  contract.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
  record=dict(kind='metadata_only_static_local_import_closure',original_contract_sha256=hashlib.sha256(old).hexdigest(),updated_contract_sha256=sha(contract),added_files={n:bound[n] for n in additions},bound_local_python_files=len(bound),scientific_source_edits=0,config_or_corpus_or_schedule_edits=0,new_tests=0,new_model_calls=0,limitation='AST imports only; selected dynamic worker already seeded by original contract; external packages bound by reviewed runtime versions.')
  receipt.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
  print(json.dumps(dict(model=model,added=len(additions),paths=additions)))
if __name__=='__main__':main()
