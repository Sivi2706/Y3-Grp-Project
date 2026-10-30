#!/usr/bin/env python3
"""Generate LaTeX inventory/score sections from audited candidate-screening CSVs.
Run reproduce_screening.py before this file.
"""
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parent
D=R/'data'; G=R/'generated';G.mkdir(exist_ok=True)
t=pd.read_csv(D/'All_49_Method_Tags.csv').fillna('')
s=pd.read_csv(D/'Track_A_B_Weighted_Comparison.csv').fillna('')

def esc(x):
 x=str(x)
 for a,b in [ ('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#'),('$',r'\$'),('{',r'\{'),('}',r'\}'),('~',r'\textasciitilde{}'),('^',r'\textasciicircum{}')]:
  x=x.replace(a,b)
 return x

def latex_doc(text,fn):
 (G/fn).write_text(text,encoding='utf8')

def plot(data, labels, title, fig_label, xmax, height, col):
 n=len(labels)
 ticks=','.join(str(i) for i in range(n))
 ylabel=','.join('{'+esc(k)+'}' for k in labels[::-1])
 coords=' '.join(f'({int(data[k])},{n-1-i})' for i,k in enumerate(labels))
 return rf'''\begin{{figure}}[H]\centering
\begin{{tikzpicture}}
\begin{{axis}}[xbar,width=.67\linewidth,height={height}cm,xmin=0,xmax={xmax},
 ymin=-.7,ymax={n-.3},ytick={{{ticks}}},yticklabels={{{ylabel}}},
 yticklabel style={{font=\scriptsize,align=right,text width=4.7cm}},tick label style={{font=\scriptsize}},
 xmajorgrids=true,grid style={{gray!15}},bar width=7pt,
 xlabel={{Paper-tag matches in 10,833 candidates; overlapping}},xlabel style={{font=\scriptsize}},
 nodes near coords,point meta=x,every node near coord/.append style={{font=\scriptsize,anchor=west,xshift=2pt}}]
\addplot+[draw={col},fill={col}!70] coordinates {{{coords}}};
\end{{axis}}\end{{tikzpicture}}
\caption{{{title}}}\label{{{fig_label}}}
\end{{figure}}
'''
counts=dict(zip(t.ID,t.Matched_papers))
chart_ids=[['M07','M08','M09','M10','M11','M12','M13','M14','M15','M16','M18','M19','M20','M23','M24','M25'],
           ['M26','M27','M28','M29','M30','M31','M34','M35','M36','M38','M40','M41','M42','M46']]
shortnames={
'M07':'Optical / stereo microscopy','M08':'Micro-flow imaging','M09':'Camera + AI counting','M10':'Polarised scattering',
'M11':'Laser particle scatter','M12':'Fluorescence imaging','M13':'Nile Red staining','M14':'Flow cytometry',
'M15':'Digital holography','M16':'Hyperspectral imaging','M18':'Impedance / EIS','M19':'Resistive-pulse sensing','M20':'Electrochemical sensor',
'M23':'Ultrasonic detection','M24':'Acoustic focusing','M25':'Photoacoustic','M26':'FTIR spectroscopy','M27':'Raman',
'M28':'SERS','M29':'Py-GC-MS','M30':'SEM / TEM','M31':'DLS / NTA','M34':'Turbidity / solids','M35':'Conductivity / salinity',
'M36':'pH / oxygen probes','M38':'Satellite / remote sensing','M40':'General machine learning','M41':'Microfluidics','M42':'Near IR / SWIR','M46':'Magnetic separation'
}
charts=''
for a,title,fig_name,maxx,h,col in [
 (chart_ids[0],'Potential optical, electrical and acoustic particle-readout families; ultrasound sample preparation is intentionally excluded from the direct-detector chart.','fig:expanded-sensing',540,9.3,'mpteal'),
 (chart_ids[1],'Reference techniques, pretreatment, ancillary probes and model/mapping tools: prevalence of terms does not imply field sensing capability.','fig:expanded-support',1970,8.4,'mpgold')]:
 labs=[shortnames[k] for k in a]
 vals=dict(zip(labs,[counts[k] for k in a]))
 charts+=plot(vals,labs,title,fig_name,maxx,h,col)+'\n'
latex_doc(charts,'method_charts.tex')
# Table all rows grouped by family
families=['Collection / pretreatment','Optical particle readout','Electrical / acoustic','Reference / analytical','Indirect / geospatial']
legend=r'''\noindent\textbf{Legend:} \textbf{P} = preferred core candidate; \textbf{C} = conditional feasibility; \textbf{S} = supporting/enabling method, not a stand-alone MP counter; \textbf{X} = excluded as routine core under the no-specialist-lab constraint. These are \emph{engineering triage labels}, not published validation status.\par
'''
src=r'''\small
\begin{longtable}{@{}p{.8cm}p{6.0cm}rccp{5.4cm}@{}}
\caption{Expanded method identification across the original 10,833 papers. Matches are title/abstract/keyword terms, may overlap, and are not proof that the authors applied the method.}\label{tab:allmethods}\\
\toprule ID & Explicitly screened method family & Papers & A & B & Constraint / decision rationale \\\midrule
\endfirsthead
\multicolumn{6}{l}{\emph{Table continued: expanded method identification}}\\\toprule
ID & Method family & Papers & A & B & Main barrier \\\midrule
\endhead
\bottomrule\endfoot
'''
for fam in families:
 src+=r'\multicolumn{6}{l}{\textbf{'+esc(fam)+r'}}\\[2pt]'+'\n'
 for _,r in t.loc[t.Family.eq(fam)].iterrows():
  src+=f"{r.ID} & {esc(r.Method)} & {int(r.Matched_papers):,} & {r.Track_A_pre_screen} & {r.Track_B_pre_screen} & {esc(r.Key_barrier)} \\\\\n"
src+='\\end{longtable}\normalsize\n'+legend
latex_doc(src,'all_methods_table.tex')
# result ranking table sort hard-gate first then score (sorted within track)
rows='''\\footnotesize
\\begin{longtable}{@{}p{4.05cm}ccrrp{5.45cm}@{}}
\\caption{Illustrative track-weighted feasibility of candidate \emph{system concepts}; scores and gates are expert engineering assumptions, NOT study performance. Score range: 1--5.}\label{tab:weighted}\\\\
\\toprule Concept & A gate & B gate & A / 5 & B / 5 & Basis / risk \\\\ \\midrule
\\endfirsthead
\\toprule Concept & A & B & A / 5 & B / 5 & Basis / risk \\\\ \\midrule
\\endhead
\\bottomrule\\endfoot
'''
for _,r in s.iterrows():
 rows+=f"{esc(r.Concept)} & {r.Track_A_gate} & {r.Track_B_gate} & {r.A_weighted_score:.2f} & {r.B_weighted_score:.2f} & {esc(r.Working_principle)} \\\\\n"
rows+='\\end{longtable}\\normalsize\n'
latex_doc(rows,'weighted_table.tex')
# output markdown style mini stats
method_counts={k:int(v) for k,v in counts.items()}
print('Generated fragments',len(t),'taxa,',len(s),'concepts, examples')
