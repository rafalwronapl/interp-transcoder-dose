from pathlib import Path
import shutil,json,hashlib,difflib
root=Path(__file__).resolve().parent.parent
old=root/'B_v12_20261103'; new=root/'B_v13_20261103'
assert not new.exists(), 'Do not overwrite an existing revision'
new.mkdir()
skip={'review','main.aux','main.bbl','main.blg','main.log','main.out','main.pdf','editorial_snapshot.json','editorial_checks.json','editorial_diff.patch','CHANGELOG.md','extracted_text.txt','build_status.json','prepare_revision.py','edit_revision.py','seal_revision.py'}
for p in old.iterdir():
    if p.name in skip or p.name.startswith('build_'): continue
    if p.is_dir(): shutil.copytree(p,new/p.name)
    else: shutil.copy2(p,new/p.name)
s=(old/'main.tex').read_text(encoding='utf-8')
s=s.replace('twelfth private working draft','thirteenth private working draft')
s=s.replace('provide bounded posthoc diagnostics.','provide bounded posthoc oracle diagnostics.')
s=s.replace('A separate mask intervention tests FIT-selected switching groups.', 'A separate posthoc mask intervention tests FIT-selected switching groups.')
# Preserve detailed historical analyses in full, but move them out of the primary narrative.
start=s.index('\\section{Earlier secondary diagnosis of prediction-error geometry}')
end=s.index('\\section{A negative boundary:',start)
detail=s[start:end].replace('\\section{Earlier secondary diagnosis of prediction-error geometry}\\label{sec:mechanism}', '\\section{Earlier secondary prediction-error diagnostics}\\label{app:earlierdiagnostics}',1)
summary=r'''\section{Earlier diagnostics and their limits}\label{sec:mechanism}
The complete 270M cache and an earlier posthoc oracle experiment on the first 16 observed blocks supply secondary evidence (Appendix~\ref{app:earlierdiagnostics}). They are distinct from the new 32-block tests and do not add independent replications. Complete-cache endpoint alignment depends on whether centering occurs within or across frames; pooled cancellation is therefore not a sufficient explanation of readout accuracy.

The earlier experiment replaced a baseline endpoint error before crossing residual norm and direction. Its replacement satisfies $r_P(c)=r(c)+e_{0,i}-e_{0,\mathrm{partner}}$: a mismatch that need not vanish at small dose. Consequently, small-dose norm inflation is partly built into the construction. At full dose, the norm-matched direction contrast favored the original residual for full edits but not projected edits. The newer whole-residual substitution has different partners and blocks and adds no such baseline mismatch; its different projected-edit outcome is not a contradictory repeat of the same test.

Earlier gradient-parallel/perpendicular interventions used unequal norms, and the magnitude--direction experiment showed large interactions. Neither supports additive mechanism percentages. All constructions use native truth and remain bounded posthoc oracle diagnostics; full definitions, outcomes and negative strata are preserved in the appendix.
'''
s=s[:start]+summary+s[end:]
# Move technical Qwen acquisition details, keeping scope and reuse next to the claim.
start=s.index('A separately frozen extension evaluates');end=s.index('\\begin{table}[ht]',start)
qwen=s[start:end]
replacement=r'''A separately frozen extension evaluates the public Qwen3-0.6B-Base source-27--target-27 CLT component, not the whole CLT graph or historical E041's layer 21. Full donor edits use the same six doses, with predictions scored through the final native normalization/head for the is-minus-are readout. The 256 lexical blocks and two frames are shared with companion analyses; already exposed unit-dose native/ridge outputs are reused. Other-dose FIT comparators were fixed before new B outcomes. This is a descriptive shared-cohort boundary, not independent fresh confirmation. Native Taylor predicts the branch vector before exact downstream scoring; composed scalar linearization is a separate comparator. Implementation and adoption details are in Appendix~\ref{app:qwenimplementation}.

'''
s=s[:start]+replacement+s[end:]
# Retain detailed measurements and provenance rather than deleting them.
point=s.index('\\section{Operation accounting and review boundaries}')
s=s[:point]+detail+'\\section{Qwen acquisition and reuse details}\\label{app:qwenimplementation}\n'+qwen+s[point:]
s=s.replace('The companion manuscript, \\emph{When Oracle Low-Rank Error Repair Helps or Harms Intervention Predictions}, evaluates partial oracle repair and learned correction of vector predictions.', 'The companion manuscript, \\emph{When Oracle Low-Rank Error Repair Helps or Harms Intervention Predictions}, evaluates partial oracle repair and learned correction of vector predictions. Its separate layer-21 learned-correction study does not supply a new transcoder-dose result here.')
s=s.replace('The new same-dose, norm-matched whole-residual substitutions show favorable original orientation', 'The bounded posthoc oracle diagnostics using same-dose, norm-matched whole-residual substitutions show favorable original orientation')
s=s.replace('These results establish conditional importance of specified mask changes in the replacement prediction,', 'These bounded posthoc diagnostics establish conditional importance of specified mask changes in the replacement prediction,')
(new/'main.tex').write_text(s,encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preserved={p.relative_to(old).as_posix():sha(p) for p in old.rglob('*') if p.is_file() and ('evidence' in p.relative_to(old).parts[0] or p.relative_to(old).parts[0]=='figures')}
for rel,h in preserved.items(): assert sha(new/rel)==h,rel
(new/'evidence_preservation.json').write_text(json.dumps({'source':'B_v12_20261103','unchanged_files':preserved,'old_main_sha256':sha(old/'main.tex'),'old_pdf_sha256':sha(old/'main.pdf'),'new_model_calls':0,'new_resampling_calls':0},indent=2),encoding='utf-8')
(new/'editorial_diff.patch').write_text(''.join(difflib.unified_diff((old/'main.tex').read_text().splitlines(True),s.splitlines(True),fromfile='B12/main.tex',tofile='B13/main.tex')),encoding='utf-8')
(new/'CHANGELOG.md').write_text('''# B v13 — targeted editorial revision, 3 November 2026

No new scientific data, estimates, literature search, model calls or resampling.

- Moves the full older cache/16-block geometry analysis from the main narrative to an appendix, replacing it with a short scope-aware summary. All definitions, numerical outcomes and negative strata are retained.
- Moves detailed Qwen acquisition/adoption mechanics to an appendix; keeps shared-cohort reuse, fixed FIT, component-only scope and negative outcome beside the main claim.
- Uses bounded posthoc oracle diagnostic language consistently for residual/mask tests, preserving actual switch-count and unequal-strength caveats.
- Preserves the distinction between repeated ranking crossover and artifact-specific useful accuracy, including all second-artifact doses and negative conditions.
- Clarifies that the companion's separate layer-21 learned-correction study is not a new B transcoder-dose result.
- Existing operational accounting, hashes and review receipts were already mainly in appendices; no claim of a wholesale operational rewrite is made.
- Scientific evidence and figure files are copied byte-for-byte from independently reviewed B12; preservation hashes are recorded separately. Human authorship, public IDs and release formalities remain unresolved.
''',encoding='utf-8')
print('Prepared',new,'unchanged evidence/figure files',len(preserved))
