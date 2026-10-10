"""Recalculate exploratory method mentions from original candidate CSV.
Run: python reproduce_method_scan.py "C:/path/All_Screening_Decisions.csv"
Requires: pandas
"""
from pathlib import Path
import sys,re
import pandas as pd
if len(sys.argv)<2: raise SystemExit('Usage: python reproduce_method_scan.py path/to/All_Screening_Decisions.csv')
p=Path(sys.argv[1]); d=pd.read_csv(p,usecols=['TI','AB','DE','ID','Lab_Methods','Screening_Decision'],low_memory=False)
d=d.loc[d['Screening_Decision'].eq('Include candidate')].copy()
t=d[['TI','AB','DE','ID']].fillna('').agg(' '.join,axis=1)
patterns={
'Impedance / EIS':r'\bimpedan\w*\b|\bimpedimetr\w*\b|\bEIS\b',
'Ultrasound / sonication':r'\bultrason\w*\b|\bultrasound\b|\bsonicat\w*\b',
'Acoustic / photoacoustic':r'\bacoust\w*\b|\bphotoacoust\w*\b',
'Electrochemical sensing':r'\belectrochem\w*\b|\bvoltammetr\w*\b|\bamperometr\w*\b',
'Microfluidics':r'\bmicrofluidic\w*\b|\blab.on.a.chip\b',
'Flow cytometry':r'\bflow cytometr\w*\b',
'Digital holography':r'\bholograph\w*\b',
'Hyperspectral imaging':r'\bhyperspectral\b',
'Polarisation / scattering':r'\bpolarized light scatter\w*\b|\bpolarised light scatter\w*\b|\bpolarimetri\w*\b',
'Photoacoustic':r'\bphotoacoust\w*\b',
'Nile Red staining':r'\bnile red\b',
'Pyrolysis GC--MS':r'\bpyrolysis\b|\bpy.gc.ms\b',
'FTIR / infrared':r'\bftir\b|\binfrared\b',
'Raman':r'\braman\b'}
rows=[]
for method,pattern in patterns.items():
 m=t.str.contains(pattern,regex=True,flags=re.I)
 rows.append({'Method':method,'All_10833':int(m.sum()),'Lab_tag_6654':int((m & d.Lab_Methods.eq(True)).sum()),'Rule':pattern})
out=Path(__file__).parent/'Data'/'method_mentions_recomputed.csv'
pd.DataFrame(rows).to_csv(out,index=False)
print(pd.DataFrame(rows).drop(columns='Rule').to_string(index=False))
print('Saved',out)
