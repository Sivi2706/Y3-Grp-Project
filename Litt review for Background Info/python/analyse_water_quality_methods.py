#!/usr/bin/env python3
"""Thesis evidence map: 1,023 Water Quality / Physicochemical records.
Usage: python analyse_water_quality_methods.py --input "01_water_quality_physicochemical.csv"
Requires: pip install pandas
Extractive analysis: method/result sentences are from abstracts, not independently verified.
"""
import argparse, re
from pathlib import Path
import pandas as pd

METHODS = {
 'Field water/sediment sampling': r'\b(sampled|sampling|collected|collection|field survey|field investigation|sampling site|sampling station|water sample|sediment sample)\b',
 'Filtration / digestion / density separation': r'\b(filtrat\w*|digest\w*|density separa\w*|flotation|siev\w*|pretreatment|pre-treatment)\b',
 'Microscopy / imaging / visual counting': r'\b(microscop\w*|stereomicroscop\w*|image analys\w*|image process\w*|optical imag\w*|visual identif\w*|particle count\w*)\b',
 'FTIR / infrared spectroscopy': r'\b(ftir|micro-ftir|µ-ftir|fourier.transform infrared|infrared spectroscop\w*|atr-ftir)\b',
 'Raman spectroscopy': r'\b(raman|micro-raman|µ-raman)\b',
 'Other instrumental / chemical analysis': r'\b(pyrolysis.gc.ms|py.gc.ms|gc.ms|hplc|sem.edx|electron microscop\w*|thermal analys\w*|fluorescen\w*|spectrophotomet\w*)\b',
 'Water-quality sensors / in-situ instruments': r'\b(turbidimeter|turbidity sensor|conductivity sensor|multiparameter probe|water quality sensor|in.situ sensor|online monitor\w*|electrode|nephelomet\w*)\b',
 'Turbidity / suspended-solids measurement': r'\b(turbidit\w*|total suspended solid\w*|\btss\b|suspended sediment\w*|\bssc\b)\b',
 'Conductivity / pH / dissolved oxygen': r'\b(electrical conductivit\w*|conductivit\w*|\bph\b|dissolved oxygen|resistivit\w*|salinit\w*)\b',
 'Remote sensing / drone / GIS': r'\b(remote sensing|satellite|drone\w*|unmanned aerial|\buav\b|geospatial|\bgis\b|hyperspectral|multispectral|rgb imag\w*|geographic information system\w*)\b',
 'Statistical correlations / regression': r'\b(correlat\w*|regression|pearson|spearman|statistical analys\w*|linear model\w*|multivariate|principal component|\bpca\b)\b',
 'Machine learning / prediction': r'\b(machine learning|random forest|neural network|deep learning|prediction model|predictive model|support vector|artificial intelligence|gradient boost\w*)\b',
 'Controlled laboratory exposure / experiment': r'\b(experiment\w*|laboratory exposure|controlled condition\w*|incubat\w*|microcosm\w*|mesocosm\w*|batch experiment\w*)\b',
 'Review / bibliometric synthesis': r'\b(systematic review|literature review|bibliometric|meta.analysis|scoping review|narrative review|we reviewed|this review|reviewed studies)\b',
}
RESULT_RE = re.compile(r'\b(found|showed|revealed|indicat\w*|demonstrat\w*|observ\w*|detect\w*|ranged?|increas\w*|decreas\w*|significant\w*|correlat\w*|associated|concentrations?|abundance|particles?\s*/\s*(?:l|m3)|items?\s*/\s*(?:l|m3)|reported|result\w*|suggest\w*)\b',re.I)
METHOD_RE = re.compile(r'\b(method\w*|sampl\w*|collect\w*|analys\w*|analyz\w*|using|used|measur\w*|assess\w*|determin\w*|spectroscop\w*|microscop\w*|monitor\w*|conducted|performed|quantif\w*|tested|experiment\w*)\b',re.I)
SPLIT = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9(])')

def sentences(text):
    return [s.strip() for s in SPLIT.split(str(text or '').replace('\n',' ')) if len(s.strip())>25]

def extract(text, pattern, max_n=2):
    matches=[s for s in sentences(text) if pattern.search(s)]
    return ' | '.join(matches[:max_n]) if matches else 'Not stated clearly in abstract'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', default=None)
    a=ap.parse_args()
    src=Path(a.input); output=Path(a.output) if a.output else src.parent/'Water_Quality_Methodology_Review'
    output.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(src, low_memory=False).fillna('')
    assert len(d)==1023, f'Expected 1,023 input papers, found {len(d)}. Verify input file.'
    text=(d['Title'].astype(str)+' '+d['Original_Abstract'].astype(str))
    # Detect methods using title and abstract; take evidence from abstract preferentially
    for method,regex in METHODS.items():
        d[method]=text.str.contains(regex,case=False,regex=True)
    d['Methodology_Excerpt']=d['Original_Abstract'].apply(lambda x:extract(x,METHOD_RE,max_n=2))
    d['Reported_Result_Excerpt']=d['Original_Abstract'].apply(lambda x:extract(x,RESULT_RE,max_n=2))
    d['Main_Methods_Tags']=d.apply(lambda r:'; '.join(m for m in METHODS if bool(r[m])) or 'Not classified from title/abstract',axis=1)
    d['Abstract_Status']=d['Original_Abstract'].astype(str).apply(lambda x:'Present' if x.strip() else 'Missing')
    d['Review_Priority']=d.apply(lambda r:'High—inspect full text for proxy calibration' if any(r[m] for m in ['Turbidity / suspended-solids measurement','Conductivity / pH / dissolved oxygen','Water-quality sensors / in-situ instruments','Remote sensing / drone / GIS','Statistical correlations / regression']) else 'Standard—inspect full text',axis=1)
    d['Verified_Methodology']=''
    d['Verified_Results_And_Units']=''
    d['Study_Design_Confirmed']=''
    d['Calibration_Against_MP_Concentration']=''
    d['Study_Limitations_Checked']=''
    d['Full_Text_Checked']=''
    d['Reviewer_Notes']=''
    cols=['Paper_ID','Authors','Year','Title','Journal','DOI','DOI_URL','Main_Methods_Tags','Methodology_Excerpt','Reported_Result_Excerpt','Review_Priority','Original_Abstract','Abstract_Status','Verified_Methodology','Verified_Results_And_Units','Study_Design_Confirmed','Calibration_Against_MP_Concentration','Study_Limitations_Checked','Full_Text_Checked','Reviewer_Notes']
    d[cols].to_csv(output/'ALL_1023_Methodology_Results.csv',index=False,encoding='utf-8-sig')
    overview=[]
    for i,(m,pattern) in enumerate(METHODS.items(),1):
        v=d[d[m]]
        name=re.sub('[^A-Za-z0-9]+','_',m).strip('_')
        v[cols].to_csv(output/f'{i:02d}_{name}.csv', index=False,encoding='utf-8-sig')
        overview.append({'Method_Category':m,'Papers_Mentioning_Method':len(v),'Share_of_1023_Percent':round(len(v)/len(d)*100,1),'Interpretation':'Title/abstract keyword match—not verified methodological use'})
    pd.DataFrame(overview).sort_values('Papers_Mentioning_Method',ascending=False).to_csv(output/'METHODOLOGY_OVERVIEW.csv',index=False)
    d[d['Main_Methods_Tags']=='Not classified from title/abstract'][cols].to_csv(output/'NOT_CLASSIFIED_CHECK_MANUALLY.csv',index=False,encoding='utf-8-sig')
    with open(output/'README_Thesis_Use.txt','w',encoding='utf-8') as f:
        f.write('Water quality / physicochemical subset: 1,023 preliminary candidate papers.\n\n')
        f.write('METHOD TAGS ARE AUTOMATED KEYWORD MATCHES. Method/result excerpts are copied directly from abstract sentences, NOT independent verification of findings. They may include background or claims from reviews, and may not describe new experimental results.\n\n')
        f.write('Use the ALL_1023_Methodology_Results.csv master sheet to review evidence, and the per-method files to prioritise full-text checks. Papers can occur in multiple method categories.\n')
        f.write('Before citing in thesis: retrieve source DOI; verify whether it is primary research or review; confirm methodology, measured endpoint, quantitative magnitude and units, controls, uncertainty, and whether MP concentration was paired with a proxy.\n')
        f.write('Do not claim any calibration relationship from tags or excerpts alone.\n')
    print('Papers processed:',len(d));print(pd.DataFrame(overview).sort_values('Papers_Mentioning_Method',ascending=False).to_string(index=False));print('Saved:',output)
if __name__=='__main__':main()
