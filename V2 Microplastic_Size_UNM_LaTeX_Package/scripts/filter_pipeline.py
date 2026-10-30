#!/usr/bin/env python3
"""Reproducible filter pipeline for the microplastic literature review.
Usage:  python filter_pipeline.py path/to/Bibliometrix_Filtered.RData  [outdir]
Requires: pandas, pyreadr.  Writes CSV/JSON files used by the LaTeX report.
"""
import sys, os
INPUT = sys.argv[1] if len(sys.argv)>1 else 'Bibliometrix_Filtered.RData'
OUT   = sys.argv[2] if len(sys.argv)>2 else 'data'
os.makedirs(OUT, exist_ok=True)
import pyreadr, pandas as pd
M=pyreadr.read_r(INPUT)['M']

import re, pandas as pd
M=M.copy()
M['txt']=(M.TI.fillna('')+' . '+M.AB.fillna('')+' . '+M.DE.fillna('')).str.upper()
M['txt']=M.txt.str.replace('\u00b5','U').str.replace('\u03bc','U').str.replace('\u2013','-').str.replace('\u2212','-')
MP=r'MICRO-?PLASTIC|MICROFIBER|MICROFIBRE|PLASTIC PARTICLE|PLASTIC DEBRIS|MICRO- AND NANO'
FW=r'\bRIVERS?\b|\bPONDS?\b|\bLAKES?\b|\bSTREAMS?\b|FRESHWATER|FRESH WATER|RESERVOIR|\bCANALS?\b|\bCREEKS?\b|\bWETLANDS?\b|\bTRIBUTAR'
M['mp']=M.txt.str.contains(MP,regex=True)
M['fw']=M.txt.str.contains(FW,regex=True)
UNIT=r'(?:UM|MM|MICRON|MICROMETER|MICROMETRE|MICROMETERS|MICROMETRES|NM)'
NUM=r'\d+(?:[.,]\d+)?'
size_re=re.compile(rf'({NUM})\s*(?:-|TO|AND|–)\s*({NUM})\s*({UNIT})\b|(?:<|<=|BELOW|SMALLER THAN|LESS THAN|UNDER|>|ABOVE|LARGER THAN|MORE THAN|UP TO)\s*({NUM})\s*({UNIT})\b|\b({NUM})\s*({UNIT})\b')
M['size_hit']=M.txt.apply(lambda t: bool(size_re.search(t)))
M['sizeword']=M.txt.str.contains(r'SIZE|SIZES|SIZE CLASS|SIZE DISTRIBUTION|DIAMETER|LENGTH',regex=True)

import re, json, pandas as pd, numpy as np

def clean(s): 
    s = s if isinstance(s,str) else ''
    return s.upper().replace('\u00b5','U').replace('\u03bc','U').replace('\u2013','-').replace(' MU M',' UM').replace('\\&','&')

# ---------- Q1 funnel ----------
WB = r'\bRIVERS?\b|\bPONDS?\b|\bLAKES?\b|\bSTREAMS?\b|\bRESERVOIRS?\b|\bCREEKS?\b|\bCANALS?\b|TRIBUTAR'
M['wb'] = M.txt.str.contains(WB, regex=True)
M['txt_c'] = M.txt
F = {}
F['0_all'] = len(M)
F['1_abstract'] = int(M.AB.notna().sum())
F['2_mp'] = int(M.mp.sum())
F['3_fw'] = int((M.mp & M.fw).sum())
F['4_wb'] = int((M.mp & M.wb).sum())
S = M[M.mp & M.wb].copy()
F['5_sizeexpr'] = int(S.size_hit.sum())

NUMU = r'(\d+(?:\.\d+)?)\s*(UM|MM|NM|MICRON[S]?|MICROMETRE[S]?|MICROMETER[S]?)'
def to_mm(v,u):
    v=float(v); u=u.upper()
    if u=='MM': return v
    if u=='NM': return v/1e6
    return v/1000.0
rng = re.compile(NUMU.replace('(UM','(?:(UM',1) if False else r'(\d+(?:\.\d+)?)\s*(UM|MM|NM)?\s*(?:-|TO)\s*(\d+(?:\.\d+)?)\s*(UM|MM|NM|MICRON[S]?|MICROMETRE[S]?)')
lt  = re.compile(r'(?:<=|<|&LT;|BELOW|SMALLER THAN|LESS THAN|UNDER|\\LE|LE;|&LE;)\s*(\d+(?:\.\d+)?)\s*(UM|MM|NM|MICRON[S]?)')
DOM = re.compile(r'DOMINAT|MAJORITY|MOST|PREDOMIN|MAINLY|MAIN\b|PREVAIL|PREVALEN|COMMON|ABUNDANT|ACCOUNT|CONCENTRATED|WIDESPREAD|COPIOUS|PRIMARILY')
DEFN = re.compile(r'DEFIN|ARE (?:PLASTIC|PARTICLES)|BETWEEN 1 UM AND 5 MM|SIZE OF 1 UM|LESS THAN OR EQUAL TO 5|\(PLASTICS? <|RANGING FROM 0\.1 TO 5|DIAMETER OF <5|SIZE DISTRIBUTION OF 0\.05-5|0\.05-5 MM')
rows=[]
for idx,r in S.iterrows():
    ab = clean(r.AB)
    best=None
    for sent in re.split(r'(?<=[.!?])\s+(?=[A-Z`\'(<])', ab):
        if not DOM.search(sent) or DEFN.search(sent): continue
        if not re.search(r'SIZE|DIAMETER|LENGTH|<|FRAGMENT|FIBR|FIBER|PARTICLE|MPS|MICROPLASTIC',sent): continue
        m = rng.search(sent); l = lt.search(sent)
        cand=None
        if l and (not m or l.start() <= m.start()):
            ub = to_mm(l.group(1),l.group(2)); lb=0.0; txt=l.group(0)
        elif m:
            u2=m.group(4); u1=m.group(2) or u2
            a=to_mm(m.group(1),u1); b=to_mm(m.group(3),u2); lb,ub=min(a,b),max(a,b); txt=m.group(0)
        else: continue
        if ub>=5 or ub<=0: continue
        if lb<0 and ub<=0: continue
        best=(lb,ub,txt,sent); break
    if best:
        lb,ub,txt,sent=best
        cls = '<0.1 mm (<100 um)' if ub<=0.1 else '0.1-0.5 mm' if ub<=0.5 else '0.5-1 mm (incl. generic <1 mm)' if ub<=1.0 else '1-5 mm (ub >1 mm)'
        rows.append(dict(id=idx,year=int(r.PY),doi=r.DI,title=r.TI,journal=r.SO,doctype=r.DT,expr=txt,lb_mm=lb,ub_mm=ub,size_class=cls,sentence=sent[:400]))
D=pd.DataFrame(rows)
F['6_dominant_size']=len(D)
print(F)
print(D.size_class.value_counts())

# water-body tags (used for the river / lake / pond split)
_t = D.id.map(lambda i: M.loc[i,'txt'])
D['river'] = _t.str.contains(r'\bRIVERS?\b|\bSTREAMS?\b|\bCREEKS?\b|TRIBUTAR')
D['lake']  = _t.str.contains(r'\bLAKES?\b|\bRESERVOIRS?\b')
D['pond']  = _t.str.contains(r'\bPONDS?\b')

D.to_csv(f'{OUT}/q1_dominant_size_papers.csv',index=False)
json.dump(F,open(f'{OUT}/funnel_q1.json','w'),indent=1)
S[['PY','AU','TI','SO','DI','DT','TC']].to_csv(f'{OUT}/q1_river_pond_lake_microplastic_papers.csv')

# ---------------- Q2: University of Nottingham Malaysia ----------------
def blob(r):
    return ' | '.join(str(r[c]) for c in ['C1','affiliations','AU_UN','RP','AU1_UN','organization']
                      if r[c] is not None and str(r[c])!='nan').upper()
b = M.apply(blob, axis=1)
UNM = (r'NOTTINGHAM[^|;]{0,80}MALAYSIA|NOTTINGHAM[^|;]{0,200}SEMENYIH|SEMENYIH[^|;]{0,200}NOTTINGHAM|'
       r'UNMC|NOTTINGHAM[^|]{0,120}BROGA|NOTTINGHAM[^|]{0,120}SELANGOR')
U = M[b.str.contains(UNM, regex=True)]
U[['PY','AU','TI','SO','DI','DT','TC','C1','AB','DE']].to_csv(f'{OUT}/q2_unm_papers.csv')
print('UNM papers:', len(U))
