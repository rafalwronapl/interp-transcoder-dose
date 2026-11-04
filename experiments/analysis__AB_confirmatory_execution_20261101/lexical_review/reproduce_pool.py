"""Reviewer-only deterministic reproduction of v4 pool; no model imports.

Run from the laboratory root. Prints equality with the preserved v4 screen;
does not alter the screen, historical data, or any production corpus.
"""
from pathlib import Path
import collections
import json
import re
import nltk

HERE = Path(__file__).resolve().parent
nltk.data.path.insert(0, str(HERE.parent/'lexical_sources'))
from nltk.corpus import wordnet as wn


def reproduce(seen, old_artifact_candidates):
    candidates = {}
    synset_words = collections.defaultdict(list)
    for word in wn.all_lemma_names(pos='n'):
        if not re.fullmatch('[a-z]{4,16}', word):
            continue
        if word.endswith(('s','f','fe','o','y','x','ch','sh')) or word in seen or word+'s' in seen:
            continue
        if wn.morphy(word+'s', wn.NOUN) != word:
            continue
        senses = wn.synsets(word, wn.NOUN)
        first = senses[0]
        if first.lexname() not in {'noun.animal','noun.person'} and word not in old_artifact_candidates:
            continue
        if not first.definition().lower().startswith(('a ','an ','someone','one who')):
            continue
        aliases = {alias.lower() for sense in senses for alias in sense.lemma_names()
                   if re.fullmatch('[a-z]+',alias)}
        if aliases & seen:
            continue
        candidates[word] = dict(first_synset=first.name(),lexname=first.lexname(),
                                definition=first.definition(),synsets=[s.name() for s in senses])
        for sense in senses:
            synset_words[sense.name()].append(word)
    parent = {word:word for word in candidates}

    def find(word):
        while parent[word] != word:
            parent[word] = parent[parent[word]]
            word = parent[word]
        return word

    for words in synset_words.values():
        for word in words[1:]:
            parent[find(word)] = find(words[0])
    groups = collections.defaultdict(list)
    for word in candidates:
        groups[find(word)].append(word)
    roots = {wn.synset(s) for s in ('animal.n.01','person.n.01','instrumentality.n.03',
                                   'structure.n.01','container.n.01','covering.n.02')}
    mass_ancestors = {'toiletry.n.01','fabric.n.01','material.n.01','substance.n.01','substance.n.07'}
    irregular = {singular for plural,singulars in wn._exception_map['n'].items()
                 for singular in singulars if plural != singular+'s'}
    result = []
    for words in groups.values():
        word = min(words, key=lambda x:(x != candidates[x]['first_synset'].split('.')[0],len(x),x))
        first = wn.synset(candidates[word]['first_synset'])
        ancestors = set(first.closure(lambda s:s.hypernyms()))
        if not roots & (ancestors | {first}):
            continue
        if not any(lemma.name() == word for lemma in first.lemmas()):
            continue
        if word.endswith('ing') or {s.name() for s in ancestors} & mass_ancestors:
            continue
        if word in irregular or word.endswith(('man','woman','person','child')):
            continue
        result.append(dict(word=word,aliases=sorted(words),**candidates[word]))
    return sorted(result, key=lambda row:row['word'])


if __name__ == '__main__':
    seen = set(json.loads((HERE.parent/'corpus/observed_words.json').read_text()))
    artifacts = set(json.loads((HERE.parent/'corpus/candidate_pools.json').read_text())['nouns'])
    preserved = json.loads((HERE/'expanded_pool_audit_v4.json').read_text())['selected_representatives']
    result = reproduce(seen,artifacts)
    print(json.dumps({'reproduced':len(result),'preserved':len(preserved),'equal':result==preserved}))
    if result != preserved:
        raise SystemExit('Mismatch with preserved review screen')
