"""Re-render saved accepted cells only, preserving every value and panel."""
from pathlib import Path
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
source=HERE/'final_test_evidence/summary.json'
r=json.loads(source.read_text(encoding='utf-8'))
assert r['status']=='descriptive_complete' and len(r['cells'])==288
styles={
 'TC':dict(marker='o',linestyle='-',color='#2166ac'),
 'TAYLOR':dict(marker='s',linestyle='--',color='#b2182b'),
 'RIDGE':dict(marker='^',linestyle='-.',color='#1b7837'),
 'MEAN':dict(marker='D',linestyle=':',color='#762a83'),
 'FROZEN':dict(marker='v',linestyle=(0,(7,2)),color='#d98500'),
 'ZERO':dict(marker='x',linestyle=(0,(2,2)),color='#666666')}
points=[]
for gray in (False,True):
 fig,axes=plt.subplots(2,2,figsize=(9,6.8),sharex=True,sharey=True)
 for row,op in enumerate(('full','projected')):
  for col,template in enumerate(('equal_main_energy_mixture','transfer')):
   ax=axes[row,col]
   for method,style in styles.items():
    cells=sorted((x for x in r['cells'] if x['operator']==op and x['template']==template and x['method']==method),key=lambda x:x['dose'])
    assert [x['dose'] for x in cells]==[.05,.1,.25,.5,1.,2.]
    doses=[x['dose'] for x in cells];errors=[100*x['relative_error_RMS'] for x in cells]
    opts=dict(style)
    if gray:opts['color']='#444444' if method!='ZERO' else '#777777'
    ax.plot(doses,errors,markersize=4,linewidth=1.3,label=method,markerfacecolor='white',markeredgewidth=1.,**opts)
    if not gray:points.append(dict(operator=op,template=template,method=method,doses=doses,relative_error_percent=errors))
   ax.set_xscale('log');ax.set_yscale('log');ax.grid(alpha=.2)
   ax.set_title(op.title()+'; '+('main-template mixture' if col==0 else 'held-out transfer template'),fontsize=10)
   if row==1:ax.set_xlabel('Dose coefficient c')
   if col==0:ax.set_ylabel('Relative RMS readout error (%)')
 handles,labels=axes[0,0].get_legend_handles_labels()
 fig.legend(handles,labels,loc='lower center',ncol=6,frameon=False,handlelength=3)
 fig.tight_layout(rect=(0,.055,1,1))
 name='new_test_dose_grayscale' if gray else 'new_test_dose'
 fig.savefig(HERE/'figures'/f'{name}.pdf');fig.savefig(HERE/'figures'/f'{name}.png',dpi=180)
 plt.close(fig)
(HERE/'figure_accessibility.json').write_text(json.dumps(dict(source='final_test_evidence/summary.json',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),styles=styles,panels=4,curves=24,points=points,new_model_calls=0,new_resampling=0),indent=2)+'\n')
print('Rendered four panels with six independent marker/line styles; values copied from accepted cells.')
