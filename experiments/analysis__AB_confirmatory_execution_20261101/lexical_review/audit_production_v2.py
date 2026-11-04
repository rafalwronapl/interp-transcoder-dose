"""Independent source-bound lexical checks; writes only reviewer-owned evidence."""
from pathlib import Path
import sys
import collections
import hashlib
import json

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[1]
sys.path.insert(0,str(ROOT))


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    import ab_confirmatory_20261101.corpus as production
    captured = {}
    production.write = lambda name,obj: captured.__setitem__(name,obj)
    files = ['ab_confirmatory_20261101/'+p for p in ('__init__.py','prepare.py','extend_exposure.py','corpus.py','tokenize_corpus.py')]
    files += ['analysis/AB_confirmatory_execution_20261101/corpus/'+p for p in
              ('historical_input_manifest_v2.json','observed_words_v2.json','exposure_manifest_v2.json',
               'qualified_pools_v1.json','corpus_v1.json','tokens_v1.json','tokenization_v1.json')]
    files += [str(p.relative_to(ROOT)).replace('\\','/') for p in (OUT/'lexical_sources').rglob('*') if p.is_file()]
    before={f:sha(ROOT/f) for f in files}
    read=lambda p:json.loads((OUT/'corpus'/p).read_text())
    manifest=read('historical_input_manifest_v2.json')['files']
    bad=[p for p,h in manifest.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    seen=set(read('observed_words_v2.json'));pool=read('qualified_pools_v1.json');c=read('corpus_v1.json')
    t=read('tokens_v1.json');ts=read('tokenization_v1.json');docs={d['id']:d for d in c['documents']}
    aliases=[];senses={};collisions=[]
    for row in pool['nouns']:
        aliases.extend((row['word'],a) for a in row['all_noun_aliases'] if a in seen or a+'s' in seen)
        for s in row['synsets']:
            if s in senses:collisions.append((row['word'],senses[s],s))
            senses[s]=row['word']
    words=[w.casefold() for b in c['blocks'] for w in b['words']]
    donor_failures=[]
    for d in docs.values():
        p=docs[d['donor']]
        if (p['donor'],p['block'],p['frame'],p['q'],p['side'])!=(d['id'],d['block'],d['frame'],d['q'],1-d['side']):
            donor_failures.append(d['id'])
    tokenizer_failures=[]
    from transformers import AutoTokenizer
    for study,folder,answers in [('A','models/gemma-3-1b-pt',[' is',' are']),('B','models/gemma-3-270m',[' she',' he'])]:
        tok=AutoTokenizer.from_pretrained(ROOT/folder,local_files_only=True)
        answer_ids=[tok.encode(a,add_special_tokens=False) for a in answers]
        if any(len(a)!=1 for a in answer_ids):raise ValueError('Answer not one token')
        for d in docs.values():
            if d['study']!=study:continue
            ids=tok(d['text'])['input_ids']
            expected=dict(ids=ids,position=len(ids)-1,donor=d['donor'],answer_ids=[a[0] for a in answer_ids])
            if t[d['id']]!=expected:tokenizer_failures.append(d['id'])
    pool_equal=production.pools()==pool
    production.build()
    corpus_equal=captured['corpus/corpus_v1.json']==c
    result=dict(manifest_files=len(manifest),manifest_mismatches=bad,pool_reproduced_equal=pool_equal,
                corpus_reproduced_equal=corpus_equal,
                pool_sizes={k:len(v) for k,v in pool.items()},bassoonist_seen='bassoonist' in seen,
                bassoonist_qualified=any(z['word']=='bassoonist' for z in pool['nouns']),
                denylist_leak=sorted(set(production.DENYLIST)&{z['word'] for z in pool['nouns']}),
                alias_exposure_hits=aliases,shared_selected_synsets=collisions,blocks=len(c['blocks']),
                documents=len(docs),lexical_units=len(words),unique_lexical_units=len(set(words)),donor_failures=donor_failures,
                tokenizer_replay_failures=tokenizer_failures,token_doc_set_equal=set(t)==set(docs),
                token_summary_hashes_valid=ts['corpus_sha256']==sha(OUT/'corpus/corpus_v1.json') and ts['tokens_sha256']==sha(OUT/'corpus/tokens_v1.json'),
                block_counts={str(k):v for k,v in collections.Counter((b['study'],b.get('cohort','r0'),b['split']) for b in c['blocks']).items()},
                model_calls=0)
    after={f:sha(ROOT/f) for f in files}
    result['inputs_unchanged_during_review']=before==after
    (HERE/'production_checks_v2.json').write_text(json.dumps(result,indent=2))
    (HERE/'production_source_binding_v2.json').write_text(json.dumps(dict(files=before),indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='block_counts'},indent=2))


if __name__=='__main__':main()
