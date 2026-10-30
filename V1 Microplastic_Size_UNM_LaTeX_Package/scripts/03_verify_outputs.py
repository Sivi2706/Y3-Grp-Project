#!/usr/bin/env python3
"""Check screening arithmetic, DOI linkage and UNM affiliation corpus boundaries."""
from pathlib import Path
import json, pandas as pd, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'data'
counts=json.loads((OUT/'screening_counts.json').read_text())
flags=pd.read_csv(OUT/'All_10833_Screening_Flags.csv',low_memory=False)
selected=pd.read_csv(OUT/'Curated_Size_Evidence_Studies.csv',low_memory=False)
unm=pd.read_csv(OUT/'UNM_9_Full_Evidence.csv',low_memory=False)
other=pd.read_csv(OUT/'Nottingham_OtherCampuses_24.csv',low_memory=False)
first=pd.read_csv(OUT/'Waterbody_Size_FirstPass_2085.csv',low_memory=False)
checks={
 'rows':len(flags)==10833==counts['candidate_pool'],
 'waterbody_size':len(first)==flags.RQ1_FirstPass_Waterbody_Size.sum()==2085,
 'unm':len(unm)==flags.Strict_UNM_Semenyih_Affiliation.sum()==9,
 'other_nottingham':len(other)==24,
 'all_nottingham':len(unm)+len(other)==33,
 'selected_count':len(selected)==17,
 'selected_unique_dois':len(selected.DOI.unique())==17,
 'flags_indices_unique':flags.Original_Row_Index.is_unique,
 'unm_indices_subset':set(unm.Original_Row_Index).issubset(set(flags.Original_Row_Index)),
}
for k,v in checks.items():print(f'{"PASS" if v else "FAIL"}: {k}')
if not all(checks.values()):sys.exit(1)
print('All checks passed; counts apply only to the supplied corpus and screening rules.')
