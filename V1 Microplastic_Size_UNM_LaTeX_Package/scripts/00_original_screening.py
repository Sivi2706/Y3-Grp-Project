#!/usr/bin/env python3
"""Reproduce screening from the companion exported 10,833-record CSV.

Run: python reproduce_screening.py /path/to/Include_Candidates.csv
The attached .RData is byte-identical to the earlier project copy. This Python
script uses the previously exported Include_Candidates.csv because this runtime
has no R installation. Native R instructions are in README.md.
"""
import re, sys, json, hashlib
from pathlib import Path
import pandas as pd
base=Path(__file__).resolve().parent
src=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/Include_Candidates.csv')
d=pd.read_csv(src,low_memory=False).fillna(''); assert len(d)==10833, f'Expected 10833 candidates, got {len(d)}'
text=(d.TI.astype(str)+' '+d.AB.astype(str))
water=text.str.contains(r'\b(?:river|rivers|pond|ponds|lake|lakes|freshwater|reservoir|stream|streams)\b',case=False,regex=True)
size=text.str.contains(r'(?:particle[- ]?size|size distribution|size fraction|size class|\d+(?:[.]\d+)?\s*(?:\\?mu|µ|μ)m|\d+(?:[.]\d+)?\s*mm|smaller than|less than)',case=False,regex=True)
mp=text.str.contains('microplastic',case=False,regex=False)
size_candidates=d[water & size & mp].copy();size_candidates.insert(0,'Original_Row_Index',size_candidates.index)
cols=['Original_Row_Index','PY','TI','AU','DI','DT','SO','AB','C1']
size_candidates[cols].to_csv(base/'Waterbody_Size_FirstPass_2085.csv',index=False)
# Affiliation matching: literal Malaysia campus or Nottingham+Semenyih/Jalan Broga.
affcols=['C1','affiliations','AU_UN','AU1_UN','RP']
aff=d[affcols].astype(str).agg(' | '.join,axis=1)
strict=aff.str.contains(r'(?:UNIV(?:ERSITY)?\s+(?:OF\s+)?NOTTINGHAM\s+MALAYSIA|UNIV(?:ERSITY)?\s+(?:OF\s+)?NOTTINGHAM[^;]{0,75}\bSEMENYIH\b|NOTTINGHAM\s+MALAYSIA\s+CAMPUS)',case=False,regex=True)
loose=aff.str.contains('nottingham',case=False,regex=False)
assert int(strict.sum())==9, int(strict.sum())
unm=d[strict].copy();unm.insert(0,'Original_Row_Index',unm.index)
unm[cols].to_csv(base/'UNM_9_Full_Evidence.csv',index=False)
not_unm=d[loose & ~strict].copy();not_unm.insert(0,'Original_Row_Index',not_unm.index)
not_unm[cols].to_csv(base/'Nottingham_OtherCampuses_24.csv',index=False)
# Qualitative, double-checked paper-level extraction to avoid interpreting
# abstract definitions of <5mm as a measured dominant size.
chosen={
 '10.1007/s10661-022-10856-5':('Semenyih River, Malaysia','River water','No size-frequency percentages extractable from the accessible abstract','Not reported in abstract','Site-specific gap'),
 '10.1007/s11270-025-08630-7':('Langat River, Malaysia','River surface water','<300: 6.64%; 300-500: 14.19%; 500-1000: 36.81%; 1001-5000: 42.36%','Measured in study; explicit bins','Nearby comparator ONLY'),
 '10.1021/acsestwater.4c00097':('Selangor River Basin, Malaysia','River surface water','600-1000 um: 26.3% (largest reported class)','Measured in study','Regional comparator'),
 '10.5614/j.eng.technol.sci.2020.52.2.7':('Cherating River, Malaysia','River water','0.5-1.0 mm reported prevalent','Measured in study','Regional comparator'),
 '10.1007/s10661-023-12188-4':('Urban tropical ponds, India','Pond surface water','500-1000 um prevalent','Measured in study','Pond comparator'),
 '10.1016/j.scitotenv.2019.02.332':('Wei River, China','River water / sediment','<0.5 mm: 68.1%','Abstract-reported','River comparator'),
 '10.1007/s11356-021-15296-1':('Songhua River, China','River surface water','<0.5 and 0.5-1.0 mm main classes','Abstract-reported','River comparator'),
 '10.1007/s10661-023-11040-z':('Lhasa River, China','River surface water','0-0.5 mm: 75.83%','Abstract-reported','River comparator'),
 '10.1007/s40710-024-00693-8':('Vaal River, South Africa','River surface water','0.06-4.95 mm; >89% <2 mm','Abstract-reported','River comparator'),
 '10.32526/ennrj/21/202200244':('Nhue-Day river basin, Vietnam','River water','0.5-2.0 mm: 71-100% depending on station','Abstract-reported','River comparator'),
 '10.1016/j.marpolbul.2024.116900':('Yellow River, Lanzhou','River water','<1 mm: 83.67%','Abstract-reported','River comparator'),
 '10.1007/s00128-024-03979-7':('Freshwater pond seasonal study','Pond surface water','<1000 um commonly observed','Abstract-reported','Pond comparator'),
 '10.1007/s10653-026-03333-2':('Lake Gahai, China','Lake water','20-50 um: 64.42%','Abstract-reported','Lake comparator'),
 '10.1007/s12403-022-00522-z':('Wei River Plain, China','Surface waters','<0.5 mm dominant','Abstract-reported','River comparator'),
 '10.1007/s10661-024-12430-7':('Wei River, China','River water','<500 um main sizes','Abstract-reported','River comparator'),
 '10.1002/etc.5482':('Vaal River, South Africa','River water / sediment','>80% fragments and fibres <2 mm','Abstract-reported','River comparator'),
 '10.1016/j.envpol.2021.118384':('Songhua River, China','River water','1-5 mm and <=1 mm approximately 50% each','Abstract-reported','River comparator'),
}
dx=d.DI.astype(str).str.lower().str.strip();rows=[]
for doi,(site,matrix,observation,status,role) in chosen.items():
 records=d[dx.eq(doi)]
 if records.empty:
  print('MISSING',doi)
  continue
 r=records.iloc[0]; rows.append({'Original_Row_Index':int(r.name),'Year':r.PY,'Title':r.TI,'DOI':doi,'Location':site,'Matrix':matrix,'Reported_Size_Evidence':observation,'Evidence_Status':status,'Role':role,'Abstract':r.AB})
sel=pd.DataFrame(rows).sort_values(['Location','Year']);sel.to_csv(base/'Curated_Size_Evidence_Studies.csv',index=False)
count={'candidate_pool':len(d),'waterbody_keyword':int(water.sum()),'size_keyword':int(size.sum()),'microplastic_keyword':int(mp.sum()),'waterbody_AND_size_AND_microplastic':len(size_candidates),'curated_size_studies':len(sel),'nottingham_anycampus':int(loose.sum()),'UNM_explicit_affiliation':int(strict.sum()),'nottingham_other_campus_or_unspecified':int((loose & ~strict).sum()),'unm_articles_studies_vs_reviews':'Six primary/experimental and three review/conceptual (manual classification); indexing document type alone is insufficient','rdata_md5':'93a3900c5778ad6630281b231d7ae3e9'}
(base/'screening_counts.json').write_text(json.dumps(count,indent=2))
print(json.dumps(count,indent=2))
