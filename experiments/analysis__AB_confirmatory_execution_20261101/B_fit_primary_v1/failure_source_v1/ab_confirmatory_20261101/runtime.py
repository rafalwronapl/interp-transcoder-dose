"""Identity-bound durable cache and explicit operation accounting."""
from pathlib import Path
import json,os,time
from datetime import datetime,timezone
from research_checks.persistence import cached,immutable,request_key
from research_checks.gate import digest


class Runtime:
    def __init__(self,folder,identity,schedule):
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
        self.identity=identity
        self.ops={x['id']:x['kind'] for x in schedule['operations']}
        if len(self.ops)!=len(schedule['operations']):raise ValueError('duplicate operation')
        immutable(self.folder/'identity.json',identity)
        immutable(self.folder/'schedule.json',schedule)
        self.ledger=self.folder/'ledger.jsonl'
        self.records=[]
        if self.ledger.exists():
            for line in self.ledger.read_text().splitlines():
                obj=json.loads(line)
                if obj['sha256']!=digest(obj['record']):raise ValueError('corrupt ledger')
                self.records.append(obj['record'])
        self.attempts={x['operation'] for x in self.records if x['event']=='attempt'}

    def record(self,value):
        value=dict(value,utc=datetime.now(timezone.utc).isoformat())
        raw=json.dumps(dict(record=value,sha256=digest(value)),sort_keys=True,allow_nan=False)+'\n'
        with self.ledger.open('a',encoding='utf-8',newline='\n') as f:
            f.write(raw);f.flush();os.fsync(f.fileno())
        self.records.append(value)

    def compute(self,operation,document,intervention,readout,function,extra_operations=()):
        operations=[operation,*extra_operations]
        if len(set(operations))!=len(operations):raise ValueError('duplicate coupled operation')
        if any(op not in self.ops for op in operations):raise ValueError('unscheduled coupled operation')
        request=dict(model_identity=self.identity['model'],code_identity=self.identity['code'],
                     document=document,intervention=intervention,readout=readout)
        key=request_key(request)
        def measured():
            # A crash after reservation consumes this scheduled attempt. Retry
            # requires an explicit predeclared retry slot; no hidden free calls.
            if any(op in self.attempts for op in operations):raise ValueError('consumed operation without durable result; use reviewed retry slot')
            for op in operations:
                self.record(dict(event='attempt',operation=op,kind=self.ops[op],request=key))
                self.attempts.add(op)
            start=time.perf_counter()
            result=function()
            self.record(dict(event='computed',operation=operation,coupled_operations=operations,request=key,seconds=time.perf_counter()-start))
            return result
        result=cached(self.folder/'cache',request,measured)
        # Immutable receipt is written only after durable cache publication.
        for op in operations:immutable(self.folder/'completed'/f'{op}.json',dict(operation=op,request=key))
        return result
