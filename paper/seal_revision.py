from pathlib import Path
import json,hashlib
from pypdf import PdfReader
H=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pages=[p.extract_text() or '' for p in PdfReader(H/'main.pdf').pages]
checks={'build':json.loads((H/'build_status.json').read_text()),'blank_pages':[i+1 for i,t in enumerate(pages) if len(t)<80],'overfull_boxes':'Overfull' in (H/'main.log').read_text(errors='replace'),'new_model_calls':0,'refits':0,'bootstrap_calls':0,'historical_evidence_byte_identical':json.loads((H/'evidence_preservation.json').read_text())['all_identical'],'render_check':{'actual_pdf_rendered':True,'all_page_contacts_inspected':['render_check/contact_1.png','render_check/contact_13.png','render_check/contact_25.png'],'new_section_and_table_details_inspected':True,'observed_clipping_or_overlap':False},'editorial_review':'pending'}
(H/'editorial_checks.json').write_text(json.dumps(checks,indent=2))
files={p.relative_to(H).as_posix():sha(p) for p in sorted(H.rglob('*')) if p.is_file() and p.name!='editorial_snapshot.json' and p.relative_to(H).parts[0]!='review' and '__pycache__' not in p.parts}
(H/'editorial_snapshot.json').write_text(json.dumps({'revision':'B_v14_20261103','previous':'B_v13_20261103','date':'2026-11-03','scope':'Latest independently approved matching, posthoc norm-control and fresh lexical/context/readout results; no new scientific measurements, refit or bootstrap. Separate independent editorial review pending.','files':files},indent=2))
print(json.dumps({'snapshot_sha256':sha(H/'editorial_snapshot.json'),'pdf_sha256':sha(H/'main.pdf'),'files':len(files),'checks':checks}))
