#!/usr/bin/env python3
"""Rebuild preliminary 4-theme subcategory tables and chart data from Bibliometrix Include_Candidates.csv.
Keyword-based multi-label classifications, not verified conclusions. Requires pandas.
"""
from pathlib import Path
import pandas as pd
import re, runpy, argparse

CAUSES = {
    'Wastewater / sewage / WWTP': r'\b(wastewater|sewage|sewer\w*|effluent\w*|wastewater treatment|\bwwtp\b|septic)\b',
    'Urban and stormwater runoff': r'\b(urban runoff|stormwater|storm water|surface runoff|road runoff|urbaniz\w*|urbanis\w*|impervious surface)\b',
    'Industrial discharge': r'\b(industr\w*|factory|factories|manufactur\w*|industrial discharge|industrial effluent)\b',
    'Agriculture / farm runoff': r'\b(agricultur\w*|farmland|farming|fertiliz\w*|fertilis\w*|livestock|irrigation)\b',
    'Textiles / laundry / fibres': r'\b(textile\w*|laundr\w*|washing machine\w*|synthetic fiber\w*|synthetic fibre\w*|microfiber\w*|microfibre\w*)\b',
    'Tyres / road traffic': r'\b(tire\w*|tyre\w*|traffic|road dust|brake wear|road wear|vehicle\w*)\b',
    'Litter / degradation / fragmentation': r'\b(litter\w*|plastic waste|plastic debris|fragmentation|weathering|degrad\w*|photodegrad\w*)\b',
    'Atmospheric deposition': r'\b(atmospher\w*|airborne|aerial deposition|wet deposition|dry deposition|dust fallout)\b',
    'Land use / catchment influence': r'\b(land use|land-use|land cover|landcover|catchment|watershed|river basin)\b',
    'River flow / sediment transport': r'\b(river flow|streamflow|hydrodynamic\w*|river transport|resuspension|sediment transport|transport pathway\w*|flow velocit\w*)\b',
    'Fishing / recreation / maritime inputs': r'\b(fishing|fisheries|aquacultur\w*|recreational|tourism|boat\w*|shipping|fishnet\w*)\b',
    'Domestic / municipal solid waste': r'\b(domestic waste|household\w*|municipal solid waste|solid waste management|landfill\w*|municipal waste)\b',
}
TRENDS = {
    'Spatial distribution / variability': r'\b(spatial distribution|spatial variation|spatial variability|spatial pattern\w*|spatial heterogene\w*|geographical distribution)\b',
    'Temporal / seasonal change': r'\b(temporal\w*|seasonal\w*|seasonality|wet season|dry season|monsoon|time series|annual variation)\b',
    'Field monitoring / repeated surveys': r'\b(monitoring|field survey\w*|sampling campaign\w*|sampling station\w*|monitoring site\w*|long.term observation\w*)\b',
    'Remote sensing / satellites': r'\b(remote sensing|satellite\w*|sentinel.?2|landsat|hyperspectral|multispectral)\b',
    'UAV / drone surveys': r'\b(drone\w*|\buav\b|unmanned aerial|aerial imag\w*|quadcopter\w*)\b',
    'RGB / image processing': r'\b(rgb|computer vision|image analys\w*|image process\w*|digital image\w*|camera-based|imaging)\b',
    'In-situ / real-time sensing': r'\b(in.situ|in situ|real.time|continuous monitor\w*|sensor network\w*|online sens\w*|field sensor\w*)\b',
    'Correlation / statistical regression': r'\b(correlat\w*|regression|pearson|spearman|generalized linear|generalised linear|multivariate|statistical model\w*)\b',
    'Machine learning / AI': r'\b(machine learning|artificial intelligence|\bai\b|neural network\w*|deep learning|support vector|random forest|gradient boost\w*)\b',
    'Hydrodynamic / transport models': r'\b(hydrodynamic\w*|transport model\w*|particle tracking|advect\w*|dispersion model\w*|numerical simul\w*|fluid dynamic\w*)\b',
    'GIS / interpolation / mapping': r'\b(\bgis\b|geographic information system|geospatial\w*|kriging|interpolation|spatial map\w*|concentration map\w*|spatial model\w*)\b',
    'Automated particle detection / counting': r'\b(automated count\w*|automated detect\w*|particle count\w*|object detection|image segment\w*|\bu-net\b|particle identification)\b',
}

SLUG = {'Causes':'causes','Water_Effects':'water_effects','Lab_Methods':'laboratory_methods','Data_Trends':'data_trends'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',default='/mnt/data/Include_Candidates.csv')
    parser.add_argument('--out',default=str(Path(__file__).resolve().parent/'Data'))
    a=parser.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    base=pd.read_csv(a.input,usecols=['TI','AB','DE','ID','DI','PY','Causes','Water_Effects','Lab_Methods','Data_Trends'],low_memory=False)
    snippets=(base['TI'].fillna('').astype(str)+' '+base['AB'].fillna('').astype(str))
    # Same rules as the previously supplied Water Effects and method analysis.
    water=runpy.run_path(str(Path(__file__).resolve().with_name('water_effects_histogram.py')))['EFFECT_PATTERNS']
    method=runpy.run_path(str(Path(__file__).resolve().with_name('analyse_water_quality_methods.py')))['METHODS']
    groups={
        'Causes': CAUSES,
        'Water_Effects': {k:'|'.join(v) for k,v in water.items()},
        'Lab_Methods': method,
        'Data_Trends': TRENDS,
    }
    for g,rules in groups.items():
        src=base.loc[base[g].astype(bool)].copy()
        txt=snippets.loc[src.index]
        data=[];flags=[]
        for label,rx in rules.items():
            flag=txt.str.contains(rx,regex=True,case=False,na=False)
            data.append({'Category':label,'Count':int(flag.sum()),'Percent':round(flag.sum()/len(src)*100,1),'Parent':g})
            flags.append(flag.reset_index(drop=True).rename(label))
        overview=pd.DataFrame(data).sort_values('Count',ascending=False).reset_index(drop=True)
        overview.to_csv(out/f'{SLUG[g]}_category_counts.csv',index=False)
        flags=pd.concat(flags,axis=1)
        unmatched=int((~flags.any(axis=1)).sum())
        summary=pd.DataFrame({'Parent':[g],'Total_candidates':[len(src)],'Subcategory_assignments':[int(overview.Count.sum())],'Unmatched_by_defined_categories':[unmatched]})
        summary.to_csv(out/f'{SLUG[g]}_summary.csv',index=False)
        print(g,len(src),'assignments',sum(overview.Count),'unmatched',unmatched)
        print(overview[['Category','Count']].to_string(index=False))
        # A manageable paper-level audit file, evidence excerpts remain in source records.
        audits=pd.DataFrame({'Title':src['TI'].fillna('').values,'DOI':src['DI'].fillna('').values,
                             'Year':src['PY'].fillna('').values,
                             'Categories':flags.apply(lambda row:'; '.join(row.index[row.to_numpy(dtype=bool)]),axis=1).values})
        audits.to_csv(out/f'{SLUG[g]}_paper_tags.csv',index=False,encoding='utf-8-sig')

if __name__=='__main__':main()
