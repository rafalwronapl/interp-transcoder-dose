from pathlib import Path
import shutil,json,hashlib,re
R=Path('C:/Users/rafal/interpretability-lab'); H=R/'papers/B_v14_20261103'; O=R/'papers/B_v13_20261103'
shutil.copytree(O,H,ignore=shutil.ignore_patterns('review','__pycache__','editorial_snapshot.json'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
D=H/'latest_evidence';D.mkdir(); sources={}
for key,src in [('switch',R/'analysis/AB_fast_followups_20261103/B_switch'),('norm',R/'analysis/B_norm_control_20261103'),('fresh',R/'analysis/B_fresh_transfer_20261103')]:
 out=D/key;out.mkdir()
 for p in src.rglob('*'):
  rel=p.relative_to(src)
  if not p.is_file() or any(x in rel.parts for x in ['cache','results','targets','aliases','completed','__pycache__','model_load_attempts','skips']):continue
  if p.suffix not in ['.txt','.json','.py'] or p.stat().st_size>2500000:continue
  if p.name in ['corpus.json','schedule.json','stage2_schedule.json','worker.py','prepare.py']:continue
  # Compact evidence retains reports, summaries, plans, review and canonical receipts and manifests.
  dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  sources[dest.relative_to(H).as_posix()]={'source':p.relative_to(R).as_posix(),'sha256':sha(p)}
(D/'sources.json').write_text(json.dumps(sources,indent=2))
s=(H/'main.tex').read_text(encoding='utf-8').replace('thirteenth private','fourteenth private')
s=s.replace('10.1\\% at a full donor patch, versus 130.0\\%', '10.11\\% at a full donor patch, versus 129.96\\%')
a='Random groups almost never switch and do not supply an equal-strength control.'
s=s.replace(a,a+' A subsequent equal-vector-norm TC-direction diagnostic gives top-minus-control MSE increments of .16581 on 32 exposed blocks and .19835 on 32 fresh lexical blocks (128/128 eligible contexts). Changed-context and object-readout subsets have restricted coverage. This perturbs TC predictions around TC\\_FULL, rather than native feature circuits.')
needle='The complete-cache diagnosis and earlier experiment remain separately reported secondary evidence.'
s=s.replace(needle,needle+' We now distinguish failed unscaled disjoint-group matching from a changed, equal-vector-norm estimand. A fresh lexical cohort tests the latter with fixed groups and scale; it confirms a prediction-direction effect on the same artifact, rather than generalization to another model or a complete explanation of crossover.')
insert=r'''
\subsection{Failed strength matching and equal-norm prediction directions}\label{sec:normnew}
A cache-only follow-up used the actual 32 FIT blocks and 128 recipient documents (64 each in \emph{so}/\emph{when}), correcting an earlier report's scope label. All five fixed disjoint size-32 alternative groups failed joint count/norm matching: their mean counts were 6.05--6.19 versus 10.375 for top32, and norms 211.47--222.38 versus 747.39. A post-run triangle-inequality certificate bounds the mean norm of \emph{any} disjoint size-32 group by 441.559, implying a norm-distribution Wasserstein-1 distance of at least 305.828, above the fixed descriptive FIT band 207.058. This is a pooled finite-FIT support bound, not a framewise impossibility proof or equivalence test. The five overlapping alternatives share 28--31 features with one another; they remain failed unscaled strength controls.

A separately reviewed follow-up changed the estimand. Write $S_G$ for the summed signed threshold-switch decoder contribution of group $G$, and construct
\[
 y_G=y_{\mathrm{TC\_FULL}}-\rho S_G/\|S_G\|,\qquad \rho=101.51097375005.
\]
The six groups and pooled FIT scale were fixed before the new readouts; native error was not used to construct the directions. Joint eligibility requires all six norms to permit amplification at most four. These are norm-rescaled EXCEPT-minus-FULL prediction directions around TC\_FULL/RR, scored through the native suffix, not equalized native switch counts, native feature ablations or a native circuit. The historical ON arm refers to positive crossings, not TC\_FULL. Endpoint magnitudes and nonswitching contributions remain. The primary statistic is the equal-block top32 MSE increment relative to TC\_FULL minus the equal mean of five alternative-group increments. A positive value means removing the top direction damages prediction more than removing the control directions.

\begin{table}[ht]
\centering\small
\begin{tabular}{lrrr}\toprule
Cohort/frame & Eligible contexts & Blocks & Top minus controls\\\midrule
Exposed historical so/when &128/128&32/32& .165807\\
Fresh lexical so/when &128/128&32/32& .198352\\
Fresh changed-context transfer &45/64&26/32& .083652\\
Fresh object construction/readout &12/64&9/32& .013883\\\bottomrule
\end{tabular}
\caption{Equal-norm direction diagnostic, full donor edit at dose 1; MSE-increment units. Positive contrasts measure relative prediction damage. Coverage is conditional on joint six-direction eligibility.}\label{tab:normnew}
\end{table}
The historical result is posthoc on already exposed outcomes. The fresh experiment fixes the same groups and scale on 32 new, disjoint exclusive-name-category pairs (256 contexts total), without readout-based refitting or selection. Its primary \emph{so}/\emph{when} confirmation concerns the same Gemma-270M/L15 artifact and she-minus-he readout. Changed-context transfer retains that readout; the object frame changes both construction (``receptionist greeted'') and readout to her-minus-him, so token identity is not isolated. Its 12/64-context, nine-block eligibility is a severe limitation: the positive eligible-subset result cannot establish broad object-readout transfer. Controls overlap and are not five independent replications. No new-model generalization or complete crossover mechanism follows. All three stages have genuine independent completion approvals; preserved reports' pending lines are superseded by those receipts.

'''
s=s.replace('\\section{Earlier diagnostics and their limits}',insert+'\\section{Earlier diagnostics and their limits}')
needle='It therefore provides a bounded intervention diagnosis, not a recovered native circuit.'
s=s.replace(needle,needle+' The new norm-rescaled direction test addresses one strength confound by changing the intervention, and fresh lexical data reproduce its positive prediction-damage contrast. Failed unscaled matching remains a distinct negative result. The restricted transfer and especially object eligibility constrain generalization; equal output norm still does not equalize switch count, semantic content or curvature.')
append=r'''
\section{Equal-norm follow-up details and provenance}\label{app:normnew}
The following tables render accepted summaries without refitting, resampling or new scientific calls. Seeds 03--07 abbreviate 20261103--20261107; each names one of the five alternative groups, not an independent sample. All increments are relative to the same eligible TC\_FULL reference; the primary gives equal weights to blocks and to the five controls.
\input{norm_followup_tables.tex}
The historical reference MSE is .112131887720. Top32 MSE is .273347195574; the five control MSEs in seed order are .108177924684, .107393014732, .107107574160, .107584686004 and .107436853421. Historical frame contrasts are .228974517693 (so) and .102639852254 (when). Intended norm is 101.51097375005; actual FP32 norms range 101.510941793--101.511005899, with maximum rounding residual .000152280 below the declared .000203219 bound. Amplification ranges .05138--3.51638. The FIT scale uses the tenth percentile of the minimum of six norms, with 127/128 FIT contexts eligible; TEST eligibility and scale were not retuned.

Actual matching-audit cost was zero model loads and zero native/TC forwards: selective cached tensor algebra only. The historical equal-norm stage made 420 native suffix attempts, 356 exact-target aliases, no skips, no backward/TC/prefix calls and one native model load, including eight technical controls. The fresh stage counted 2133 forward attempts, 529 aliases and 426 skips, zero backwards, and one native/TC load each; attempts include local branch operations and 16 technical controls. There were no cloud calls or downloads. Matching reports retain conditional estimates for unmeasured conditions; those estimates are not executed work.

Compact frozen reports, plans, summaries, input/output bindings, actual independent reviews and canonical receipts are in \path{latest_evidence/}; \path{latest_evidence/sources.json} binds every copied source by SHA-256. In particular, the scope-corrected matching report is \path{latest_evidence/switch/REPORT_v2.txt}; accepted results are \path{latest_evidence/norm/FINAL_ANALYSIS.json} and \path{latest_evidence/fresh/run/SUMMARY.json}. Completion receipts are \path{latest_evidence/switch/review/completion_review_v2.json}, \path{latest_evidence/norm/review/completion_review.json} and \path{latest_evidence/fresh/review/completion_review_v2.json}. Original evidence directories copied from B13 remain byte-identical. Full raw caches, weights and individual tensor targets stay in the laboratory archive. These scientific approvals do not constitute editorial approval of this manuscript revision.
'''
s=s.replace('\\section{Release status',append+'\n\\section{Release status') if '\\section{Release status' in s else s.replace('\\end{document}',append+'\n\\end{document}')
(H/'main.tex').write_text(s,encoding='utf-8')
# Render full five-group, frame-specific values directly from accepted fresh report; no recomputation.
r=(R/'analysis/B_fresh_transfer_20261103/REPORT.txt').read_text(encoding='utf-8')
rows=[]
for frame,eligible,blocks,contrast,inc,eff in re.findall(r'(primary_so_when|so|when|transfer|object): eligible(.*?);blocks(.*?);top-minus-controls MSEincrement=(.*?);groupincrements=(\{.*?\});absoluteeffects=(\{.*?\})',r):
 inc=json.loads(inc);eff=json.loads(eff)
 for g in ['top32']+[f'control_2026110{i}' for i in range(3,8)]:rows.append(f'{frame.replace("_"," ")} & {g.replace("control_202611","seed ")} & {inc[g]:.9f} & {eff[g]:.9f}'+r'\\')
t=r'''\begin{table}[p]\centering\footnotesize
\begin{tabular}{llrr}\toprule
Fresh frame & Group & MSE increment & Mean absolute effect\\\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\caption{Every frozen group on every fresh frame, plus the primary pooled so/when summary. Context and block coverage are in Table~\ref{tab:normnew}; so and when each cover 64/64 contexts in all 32 blocks.}\end{table}
'''
# historical pooled increments
p=json.loads((R/'analysis/B_norm_control_20261103/FINAL_ANALYSIS.json').read_text())['payload']
t+=r'\begin{table}[ht]\centering\small\begin{tabular}{lrrr}\toprule Group & MSE & Increment & Absolute effect\\\midrule'+'\n'
for g in ['top32']+[f'control_2026110{i}' for i in range(3,8)]:
 m=p['metrics'][g];t+=f'{g.replace("control_202611","seed ")} & {m["MSE"]:.9f} & {m["MSE_increment"]:.9f} & {m["absolute_effect"]:.9f}'+r'\\'+'\n'
t+=r'\bottomrule\end{tabular}\caption{All historical pooled groups, 128/128 contexts in 32 blocks.}\end{table}'
(H/'norm_followup_tables.tex').write_text(t,encoding='utf-8')
# Old evidence preservation
pres=[]
for folder in ['figures','final_test_evidence','followup_evidence','mechanism_evidence','new_test_evidence','qwen06_evidence','release_inventory']:
 for p in (O/folder).rglob('*'):
  if p.is_file():pres.append({'path':p.relative_to(O).as_posix(),'old_sha256':sha(p),'new_sha256':sha(H/p.relative_to(O))})
(H/'evidence_preservation.json').write_text(json.dumps({'all_identical':all(x['old_sha256']==x['new_sha256'] for x in pres),'files':pres},indent=2))
(H/'CHANGELOG.md').write_text('B14, November 3, 2026. Added independently approved failed unscaled matching, historical equal-norm TC-direction diagnostic, and fresh lexical/changed-context/object follow-up with full eligibility and group tables. Preserved B13 evidence byte-for-byte. No scientific calls/refit/bootstrap. Editorial review pending.\n')
print(H)
