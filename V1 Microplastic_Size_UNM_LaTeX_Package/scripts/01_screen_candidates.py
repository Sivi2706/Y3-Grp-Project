#!/usr/bin/env python3
"""Reproduce the literature-screen outputs used by the revised MP/UNM LaTeX review.

IMPORTANT: Runs on the pre-existing 10,833-row Include_Candidates.csv export.
It does not itself read the RData and does NOT establish full-text eligibility.
The curated 17-paper table is a human-reviewed file, not an algorithmic extraction.

Usage:
    python scripts/01_screen_candidates.py --input "C:/path/Include_Candidates.csv"
    python scripts/01_screen_candidates.py --input "..." --output data

Requires pandas. All paths relative to this script's parent project by default.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
N_EXPECTED = 10833
WATER = r'\b(?:river|rivers|pond|ponds|lake|lakes|freshwater|reservoir|reservoirs|stream|streams)\b'
# Broad keyword scan; numeric diameters etc. may just be the definition of MP.
# The extra reservoirs term is deliberately NOT matched in original screen; use original exact pattern to reproduce counts.
WATER_ORIGINAL = r'\b(?:river|rivers|pond|ponds|lake|lakes|freshwater|reservoir|stream|streams)\b'
SIZE = r'(?:particle[- ]?size|size distribution|size fraction|size class|\d+(?:[.]\d+)?\s*(?:\\?mu|µ|μ)m|\d+(?:[.]\d+)?\s*mm|smaller than|less than)'
UNM = r'(?:UNIV(?:ERSITY)?\s+(?:OF\s+)?NOTTINGHAM\s+MALAYSIA|UNIV(?:ERSITY)?\s+(?:OF\s+)?NOTTINGHAM[^;]{0,75}\bSEMENYIH\b|NOTTINGHAM\s+MALAYSIA\s+CAMPUS)'


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def screening(input_file: Path, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    needed = ['TI','AB','PY','AU','DI','DT','SO','C1','affiliations','AU_UN','AU1_UN','RP']
    df = pd.read_csv(input_file, low_memory=False, dtype=str, keep_default_na=False)
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f'Missing columns: {missing}; inspect source CSV before rerun')
    if len(df) != N_EXPECTED:
        raise ValueError(f'Expected original 10,833-paper export, received {len(df):,} rows')
    text = df['TI'] + ' ' + df['AB']
    water = text.str.contains(WATER_ORIGINAL, case=False, regex=True, na=False)
    size = text.str.contains(SIZE, case=False, regex=True, na=False)
    mp = text.str.contains('microplastic', case=False, regex=False, na=False)
    pool = water & size & mp
    affiliations = df[['C1','affiliations','AU_UN','AU1_UN','RP']].agg(' | '.join, axis=1)
    nottingham = affiliations.str.contains('nottingham', case=False, regex=False)
    unm = affiliations.str.contains(UNM, case=False, regex=True, na=False)

    flags = pd.DataFrame({
        'Original_Row_Index': range(len(df)), 'DOI': df['DI'], 'Year': df['PY'],
        'Title': df['TI'], 'Has_Microplastic_Keyword': mp,
        'Has_Waterbody_Keyword': water, 'Has_Size_Keyword': size,
        'RQ1_FirstPass_Waterbody_Size': pool,
        'Any_Nottingham_Affiliation': nottingham,
        'Strict_UNM_Semenyih_Affiliation': unm,
        'Other_Or_Unresolved_Nottingham': nottingham & ~unm,
    })
    flags['RQ1_FirstPass_Reason'] = flags.apply(lambda r: (
        'Candidate only: waterbody + MP + size wording; requires manual size-data verification'
        if r.RQ1_FirstPass_Waterbody_Size else
        'Excluded from FIRST-PASS only: ' + ', '.join(x for ok,x in [
            (r.Has_Waterbody_Keyword,'waterbody term absent'),
            (r.Has_Size_Keyword,'size term absent'),
            (r.Has_Microplastic_Keyword,'microplastic term absent')]
        if not ok)),axis=1)
    flags['RQ2_Affiliation_Reason'] = [
        'Explicit Malaysia campus / Nottingham Semenyih in affiliation metadata' if u else
        'Nottingham mentioned, but Malaysia campus not demonstrated in available metadata' if n else
        'No Nottingham token in scanned affiliation fields'
        for u,n in zip(unm,nottingham)
    ]
    flags.to_csv(out / 'All_10833_Screening_Flags.csv', index=False)
    export_cols = ['Original_Row_Index','PY','TI','AU','DI','DT','SO','AB','C1']
    def write_subset(mask, name):
        sub = df.loc[mask].copy()
        sub.insert(0,'Original_Row_Index',sub.index)
        sub[export_cols].to_csv(out / name, index=False)
    write_subset(pool,'Waterbody_Size_FirstPass_2085.csv')
    write_subset(unm,'UNM_9_Full_Evidence.csv')
    write_subset(nottingham & ~unm,'Nottingham_OtherCampuses_24.csv')

    # Curated extraction was checked by a human against abstracts/full-text where available.
    # A 17 DOI list in the companion file is NOT a validated exhaustive review.
    manual = pd.read_csv(ROOT / 'scripts' / 'curation_size_studies.csv', dtype=str, keep_default_na=False)
    manual['DOI'] = manual['DOI'].str.lower().str.strip()
    normalized = df['DI'].str.lower().str.strip()
    rows=[]
    missing_dois=[]
    duplicate_dois=[]
    for _,item in manual.iterrows():
        ix = normalized.index[normalized.eq(item.DOI)].tolist()
        if not ix:
            missing_dois.append(item.DOI)
            continue
        if len(ix)>1: duplicate_dois.append(item.DOI)
        r = df.loc[ix[0]]
        rows.append({'Original_Row_Index':ix[0],'Year':r.PY,'Title':r.TI,'DOI':item.DOI,
                     'Location':item.Location,'Matrix':item.Matrix,
                     'Reported_Size_Evidence':item.Reported_Size_Evidence,
                     'Evidence_Status':item.Evidence_Status,'Role':item.Role,'Abstract':r.AB})
    if missing_dois:
        raise RuntimeError(f'Curated DOIs not found in original export: {missing_dois}')
    curated = pd.DataFrame(rows).sort_values(['Location','Year'])
    curated.to_csv(out / 'Curated_Size_Evidence_Studies.csv', index=False)
    flow = [
        ['Initial bibliometric include candidates',len(df),'Data provenance; prior deduplication and document-type filter'],
        ['Waterbody keyword in title/abstract',int(water.sum()),'Broad query only'],
        ['Size keyword in title/abstract',int(size.sum()),'Broad query only'],
        ['Waterbody AND size AND microplastic',int(pool.sum()),'First-pass candidate pool; not included studies'],
        ['Curated reported size evidence examples',len(curated),'Purposeful human selection; not exhaustive'],
        ['Any Nottingham affiliation mention',int(nottingham.sum()),'Includes other campuses / uncertain'],
        ['Explicit UNM Semenyih affiliation',int(unm.sum()),'Strict campus metadata rule in this corpus'],
        ['Other / ambiguous Nottingham',int((nottingham & ~unm).sum()),'Audit separately'],
    ]
    pd.DataFrame(flow, columns=['Screening_stage','Records','Interpretation']).to_csv(out/'Screening_Flow_Stages.csv',index=False)
    counts = {
        'candidate_pool':len(df), 'waterbody_keyword':int(water.sum()),
        'size_keyword':int(size.sum()), 'microplastic_keyword':int(mp.sum()),
        'waterbody_AND_size_AND_microplastic':int(pool.sum()),
        'curated_size_studies':len(curated), 'nottingham_anycampus':int(nottingham.sum()),
        'UNM_explicit_affiliation':int(unm.sum()),
        'nottingham_other_campus_or_unspecified':int((nottingham & ~unm).sum()),
        'source_csv_sha256':sha256(input_file),
        'curation_list_sha256':sha256(ROOT/'scripts'/'curation_size_studies.csv'),
        'DOI_duplicates_in_manual_list': duplicate_dois,
        'note':'Curation is a manual example subset, not exhaustive full-text eligibility; UNM completeness only within this export/metadata rule.'
    }
    (out/'screening_counts.json').write_text(json.dumps(counts,indent=2)+'\n',encoding='utf-8')
    for f in ['waterbody_AND_size_AND_microplastic','curated_size_studies','nottingham_anycampus','UNM_explicit_affiliation']:
        print(f,counts[f])
    return counts

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True,help='Previously exported 10,833-row Include_Candidates.csv')
    ap.add_argument('--output',type=Path,default=ROOT/'data',help='Output directory')
    args=ap.parse_args()
    screening(args.input,args.output)
