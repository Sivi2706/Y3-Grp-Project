#!/usr/bin/env python3
"""Reproduce title/abstract/keyword METHOD-TERM screening and auditable paper lists.

python reproduce_screening.py --input "C:/path/Include_Candidates.csv"
Only screening, not full-text confirmation or final eligibility.
All method tags are multi-label. Engineering gate/fit is an assessment independent of counts.
"""
from __future__ import annotations
import argparse, csv, re, math
from pathlib import Path
from collections import Counter
import pandas as pd

# ID, family, method label, regex, role, track A, track B, rationale
# Proposed fit: P=plausible core; C=conditional feasibility; S=support, not a stand-alone counter;
# X=excluded as routine core under no-specialist-lab/fast mapping constraint.
METHODS = [
 ('M01','Collection / pretreatment','Manual field grab / surface sampling',r'\b(?:grab sampl\w*|field sampl\w*|surface water sampl\w*|water sampl\w*|sampling campaign\w*)\b','COLLECT','S','P','volume/contamination control'),
 ('M02','Collection / pretreatment','Pump / automated water intake',r'\b(?:peristaltic pump\w*|automated sampl\w*|water pump\w*|pumping system\w*|flow.?through sampl\w*)\b','COLLECT','S','S','flow calibration & carry-over'),
 ('M03','Collection / pretreatment','Membrane / vacuum filtration',r'\b(?:membrane filtrat\w*|vacuum filtrat\w*|filter membran\w*|filtration system\w*|microplastic filtrat\w*)\b','PREP','C','P','time & membrane recovery'),
 ('M04','Collection / pretreatment','Density / flotation separation',r'\b(?:density separat\w*|density flotation|flotation separat\w*|salt.?saturat\w*)\b','PREP','X','C','reagents and waste'),
 ('M05','Collection / pretreatment','Chemical / enzymatic digestion',r'\b(?:chemical digest\w*|oxidative digest\w*|hydrogen peroxide digest\w*|enzymatic digest\w*|wet peroxide oxidat\w*|organic matter digest\w*)\b','PREP','X','C','chemical safety/time'),
 ('M06','Collection / pretreatment','Ultrasonic sample sonication',r'\b(?:ultrasonicat\w*|sonicat\w*|ultrasonic bath\w*)\b','PREP','X','C','preparation, not detection'),
 ('M07','Optical particle readout','Brightfield / stereo optical microscopy',r'\b(?:bright.?field microscop\w*|stereo.?microscop\w*|stereomicroscop\w*|optical microscop\w*|digital microscop\w*)\b','SENSE','C','P','particle appearance not polymer proof'),
 ('M08','Optical particle readout','Flow-through / micro-flow particle imaging',r'\b(?:flow.?through imagin\w*|micro.?flow imag\w*|flow imagin\w*|imaging flow cytomet\w*|particle imaging velocimet\w*)\b','SENSE','P','C','volume/focus & duplicates'),
 ('M09','Optical particle readout','Camera + AI counting / segmentation',r'\b(?:microplastic\w*.{0,40}(?:deep learning|machine learning|u.?net|yolo|computer vision|automated count\w*)|(?:u.?net|yolo|computer vision|image segment\w*|automated particle count\w*).{0,55}microplastic\w*)\b','SENSE','P','P','MP-like images vs true MPs'),
 ('M10','Optical particle readout','Polarised light scattering / polarimetry',r'\b(?:polarized light scatter\w*|polarised light scatter\w*|polarimetr\w*|polarization.?sensitiv\w*|polarisation.?sensitiv\w*)\b','SENSE','C','C','sediment/algae discrimination'),
 ('M11','Optical particle readout','Laser / nephelometric particle scattering',r'\b(?:laser light scatter\w*|nephelomet\w*|light scattering sensor\w*|optical particle counter\w*)\b','SENSE','C','C','optical non-specificity'),
 ('M12','Optical particle readout','Fluorescence / laser induced fluorescence',r'\b(?:fluorescence microscop\w*|fluorescence imag\w*|laser.?induced fluorescen\w*|fluorescence spectroscop\w*)\b','SENSE','C','C','photobleaching/matrix'),
 ('M13','Optical particle readout','Nile Red fluorescent staining',r'\b(?:nile red|nile.?red stain\w*)\b','SENSE','X','C','wet chemistry, false positives'),
 ('M14','Optical particle readout','Flow cytometry / fluorescence cytometry',r'\b(?:flow cytomet\w*|imaging cytomet\w*)\b','SENSE','C','C','expensive/complex; identity uncertain'),
 ('M15','Optical particle readout','Digital holography / inline holography',r'\b(?:digital holograph\w*|in.?line holograph\w*|holographic microscop\w*)\b','SENSE','C','C','optical alignment, inference'),
 ('M16','Optical particle readout','Hyperspectral / multispectral laboratory imaging',r'\b(?:hyperspectral imag\w*|hyperspectral microscop\w*|multispectral imag\w*)\b','SENSE','C','C','cost/illumination/background'),
 ('M17','Optical particle readout','UV-visible absorbance / colorimetry',r'\b(?:uv.?vis (?:spectroscop\w*|absorb\w*)|colorimetric (?:detect\w*|assay\w*)|colourimetric (?:detect\w*|assay\w*))\b','PROXY','S','S','matrix dependence'),
 ('M18','Electrical / acoustic','Electrical impedance spectroscopy (EIS)',r'\b(?:electrical impedance spectroscop\w*|electrochemical impedance spectroscop\w*|impedanc\w*|impedimetr\w*|\bEIS\b)\b','SENSE','C','C','salt/electrode artefacts'),
 ('M19','Electrical / acoustic','Resistive pulse / Coulter / microchannel sensing',r'\b(?:resistive.?pulse\w*|coulter counter\w*|coulter principle|electrical cytomet\w*|electrofluidic sens\w*|wheatstone bridge.{0,60}microplastic\w*)\b','SENSE','C','C','throughput/clogs, size cut-off'),
 ('M20','Electrical / acoustic','Electrochemical / voltammetric sensing',r'\b(?:electrochemical (?:sens\w*|detect\w*)|voltammetr\w*|amperometr\w*)\b','SENSE','C','C','electrode specificity & fouling'),
 ('M21','Electrical / acoustic','Dielectrophoresis / capacitive particle sensing',r'\b(?:dielectrophore\w*|capacit\w*.{0,28}microplastic\w*|microplastic\w*.{0,28}capacit\w*)\b','SENSE','C','C','field geometry and salinity'),
 ('M22','Electrical / acoustic','Microwave / RF dielectric resonance',r'\b(?:microwave (?:sens\w*|resonat\w*|detect\w*)|radiofrequency (?:sens\w*|detect\w*)|dielectric resonat\w*)\b','SENSE','C','C','water permittivity dominates'),
 ('M23','Electrical / acoustic','Ultrasonic attenuation / scattering detection',r'\b(?:ultrasonic (?:detect\w*|sens\w*|scatter\w*|attenuat\w*)|ultrasound (?:detect\w*|sens\w*|scatter\w*|attenuat\w*))\b','SENSE','C','C','particle/background contrast'),
 ('M24','Electrical / acoustic','Acoustic focusing / acoustophoresis',r'\b(?:acoustophore\w*|acoustic focus\w*|acoustic separat\w*|acoustic concentrat\w*)\b','PREP','C','C','enrichment only, not counting'),
 ('M25','Electrical / acoustic','Photoacoustic sensing / spectroscopy',r'\b(?:photoacoust\w*|optoacoust\w*)\b','SENSE','C','C','specialised transducers/lasers'),
 ('M26','Reference / analytical','FTIR / micro-FTIR / ATR-FTIR',r'\b(?:micro.?ftir|\bftir\b|fourier.?transform infrared|atr.?ftir)\b','REFERENCE','X','X','specialist instrument; useful external reference'),
 ('M27','Reference / analytical','Raman / micro-Raman spectroscopy',r'\b(?:raman\b|micro.?raman|raman spectroscop\w*)\b','REFERENCE','X','X','specialist instrument; useful external reference'),
 ('M28','Reference / analytical','Surface-enhanced Raman (SERS)',r'\b(?:surface.?enhanced raman|\bSERS\b)\b','REFERENCE','X','X','nanostructured substrates/laser'),
 ('M29','Reference / analytical','Py-GC-MS / thermal decomposition',r'\b(?:pyrolysis.?gc.?ms|py.?gc.?ms|thermal desorption.?gc.?ms|pyrolysis.?gas chrom\w*)\b','REFERENCE','X','X','polymer mass, destructive/lab'),
 ('M30','Reference / analytical','SEM / TEM electron microscopy',r'\b(?:scanning electron microscop\w*|transmission electron microscop\w*|\bSEM\b.{0,25}microplastic\w*|\bTEM\b.{0,25}microplastic\w*)\b','REFERENCE','X','X','fixed equipment; morphology'),
 ('M31','Reference / analytical','Dynamic light scattering / nanoparticle tracking',r'\b(?:dynamic light scattering|nanoparticle tracking analysis|\bNTA\b.{0,30}microplastic\w*|\bDLS\b.{0,30}microplastic\w*)\b','REFERENCE','X','X','nanoparticle proxy, no polymer proof'),
 ('M32','Reference / analytical','Plasmonics / SPR / LSPR sensing',r'\b(?:surface plasmon resonance|localized surface plasmon|localised surface plasmon|\bLSPR\b|\bSPR\b.{0,25}microplastic\w*)\b','SENSE','C','C','substrates/selectivity/expense'),
 ('M33','Reference / analytical','Fluorescence tagging / immunoassay',r'\b(?:fluorescent tagg\w*|fluorescent label\w*|immunoassay\w*.{0,35}microplastic\w*)\b','PREP','X','C','reagents and field stability'),
 ('M34','Indirect / geospatial','Turbidity / suspended solids',r'\b(?:turbidit\w*|suspended sediment concentrat\w*|total suspended solids|\bTSS\b)\b','PROXY','S','S','not selective for MP'),
 ('M35','Indirect / geospatial','Conductivity / resistivity / salinity probe',r'\b(?:electrical conductivit\w*|electrical resistivit\w*|conductivity probe\w*|conductivity sensor\w*|water salinit\w*)\b','PROXY','S','S','ions dominate; auxiliary covariate'),
 ('M36','Indirect / geospatial','pH / dissolved oxygen / temperature probes',r'\b(?:dissolved oxygen|\bpH\b.{0,30}(?:water|measure\w*|microplastic\w*)|water temperature probe\w*)\b','PROXY','S','S','environmental covariates only'),
 ('M37','Indirect / geospatial','RGB / aerial drone imagery',r'\b(?:rgb imag\w*|rgb camera\w*|uav imag\w*|drone imag\w*|aerial imag\w*|drone.?based remote sens\w*)\b','PROXY','S','S','water appearance, not individual MPs'),
 ('M38','Indirect / geospatial','Satellite / remote sensing / spectral indices',r'\b(?:satellite remote sens\w*|satellite imag\w*|sentinel.?2|landsat|remote.?sens\w*.{0,30}microplastic\w*)\b','PROXY','S','S','surface signal, calibration needed'),
 ('M39','Indirect / geospatial','GIS / geostatistics / spatial interpolation',r'\b(?:geostatistic\w*|kriging\b|inverse distance weight\w*|spatial interpolation|geographical information system|\bGIS\b.{0,30}microplastic\w*)\b','MAP','S','S','maps points; not sensing'),
 ('M40','Indirect / geospatial','Machine learning / predictive regression',r'\b(?:support vector machin\w*|random forest\w*|convolutional neural network\w*|deep learning\w*|machine learning\w*|predictive model\w*)\b','ANALYSIS','S','S','model does not independently establish polymer'),
 ('M41','Collection / pretreatment','Microfluidics / lab-on-chip handling',r'\b(?:microfluidic\w*|lab.?on.?a.?chip)\b','HANDLING','S','S','microchannels need antifouling/volume control'),
 ('M42','Reference / analytical','NIR / SWIR / near infrared spectroscopy',r'\b(?:near.?infrared spectroscop\w*|short.?wave infrared|\bSWIR\b|\bNIR\b.{0,25}microplastic\w*)\b','REFERENCE','C','C','spectral sampling & water interference'),
 ('M43','Reference / analytical','Laser-induced breakdown spectroscopy (LIBS)',r'\b(?:laser.?induced breakdown spectroscop\w*|\bLIBS\b.{0,25}microplastic\w*)\b','REFERENCE','X','X','pulsed laser / target preparation'),
 ('M44','Electrical / acoustic','Nanopore ionic current / pulse sensing',r'\b(?:nanopore (?:sens\w*|detect\w*|count\w*)|ionic current (?:puls\w*|sens\w*)|nanopore resistive pulse)\b','SENSE','C','C','pore clogging; selectivity'),
 ('M45','Reference / analytical','AFM atomic force microscopy',r'\b(?:atomic force microscop\w*|\bAFM\b.{0,30}microplastic\w*)\b','REFERENCE','X','X','lab-scale nanoscale morphology'),
 ('M46','Collection / pretreatment','Magnetic / electrostatic separation',r'\b(?:magnetic separat\w*|magnetophore\w*|electrostatic separat\w*)\b','PREP','X','C','functionalisation / recovery controls'),
 ('M47','Optical particle readout','Smartphone / handheld digital microscopy',r'\b(?:smartphone (?:microscop\w*|detect\w*|imag\w*)|mobile.?phone microscop\w*|handheld (?:microscop\w*|imaging))\b','SENSE','C','P','low cost; resolution and repeatability'),
 ('M48','Electrical / acoustic','QCM / piezoelectric mass sensor',r'\b(?:quartz crystal microbalanc\w*|\bQCM\b.{0,25}microplastic\w*|piezoelectric (?:sensor|detect\w*))\b','SENSE','C','C','selective adhesion / drift'),
 ('M49','Optical particle readout','Optical coherence tomography (OCT)',r'\b(?:optical coherence tomograph\w*|\bOCT\b.{0,25}microplastic\w*)\b','SENSE','C','C','cost/penetration/selectivity'),
]

# Engineering selection is an independent, transparent expert triage (not experimental performance).
CANDIDATES = [
 # name, method IDs, short circuit / process, A gate, B gate, six subjective scores [validity, portable, throughput, no lab, robust, affordable]
 ('Flow-through camera + AI', 'M08,M09', 'Pumped, measured flow; object recognition; count/volume', 'P','C', [3,4,4,5,2,4]),
 ('Portable filtration + microscope / AI', 'M03,M07,M09', 'Collect known V; filter; visual count; optional AI','X','P',[3,5,2,5,3,5]),
 ('Micro-flow imaging particle analyser', 'M08', 'Imaging and morphometry within flow cell','C','C',[3,3,4,4,2,2]),
 ('Polarised light scattering', 'M10', 'Measure material-related polarisation/scattering contrast','C','C',[2,4,5,5,2,3]),
 ('Optical particle scattering / counter', 'M11', 'Laser scatter pulses, particle-size proxy','C','C',[2,4,5,5,2,3]),
 ('Electrical impedance / EIS', 'M18', 'Frequency-dependent electrical response','C','C',[2,4,4,5,2,3]),
 ('Resistive-pulse microfluidic', 'M19', 'Particle-transit electrical pulses','C','C',[3,3,4,4,2,2]),
 ('Nile Red fluorescence + imaging', 'M13,M12', 'Controlled portable stain and microscope','X','C',[3,3,2,3,2,3]),
 ('Flow cytometry / fluorescence counting', 'M14', 'Flow and laser fluorescence/scatter readout','C','C',[3,2,4,3,2,1]),
 ('Digital holographic particle imaging', 'M15', 'Reconstruct digital holograms and size/categorise','C','C',[3,3,4,5,2,2]),
 ('Hyperspectral imaging', 'M16', 'Multi-band optical signatures','C','C',[3,2,2,3,2,1]),
 ('Acoustic focusing + downstream counting', 'M24', 'Enrich suspension; another sensor must count','S','S',[2,2,3,4,2,2]),
 ('Ultrasonic direct attenuation', 'M23', 'Acoustic losses interpreted as particle-related','C','C',[1,4,5,5,1,4]),
 ('Electrochemical functionalised electrode', 'M20', 'Electrode binding/redox response','C','C',[2,3,3,4,2,2]),
 ('Remote RGB / turbidity proxy', 'M34,M37', 'Predict MPs from surface colour/turbidity','S','S',[1,5,5,5,1,5]),
 ('Bulk conductivity / resistivity proxy', 'M35', 'Predict MPs from ion-dependent water impedance','S','S',[1,5,5,5,1,5]),
 ('Micro-FTIR / micro-Raman', 'M26,M27', 'Polymer spectrum and particle ID','X','X',[5,1,1,1,4,1]),
 ('Py-GC-MS polymer mass', 'M29', 'Destructive laboratory polymer mass quantification','X','X',[4,1,1,1,4,1]),
 ('SEM / TEM', 'M30', 'Electron morphology imaging','X','X',[2,1,1,1,3,1]),
]
W_A = {'validity':.30,'portability':.20,'throughput':.20,'no_lab':.12,'robustness':.10,'affordability':.08}
W_B = {'validity':.30,'portability':.10,'throughput':.10,'no_lab':.20,'robustness':.15,'affordability':.15}

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--input',required=True)
 ap.add_argument('--out',default='data')
 args=ap.parse_args()
 out=Path(args.out);out.mkdir(exist_ok=True,parents=True)
 header=pd.read_csv(args.input,nrows=0).columns
 cols=[x for x in ['TI','AB','DE','ID','DI','AU','PY','SO','Screening_Decision'] if x in header]
 data=pd.read_csv(args.input,usecols=cols,dtype=str,keep_default_na=False,low_memory=False)
 if 'Screening_Decision' in data.columns:
  data=data.loc[data.Screening_Decision.str.strip().eq('Include candidate')].copy()
 assert len(data)==10833, f"Expected 10,833, found {len(data)}"
 combined=(data.get('TI','')+' '+data.get('AB','')+' '+data.get('DE','')+' '+data.get('ID','')).str.replace(r'\s+',' ',regex=True)
 main_rows=[]; aud=[]; count=Counter()
 records = data.reset_index(drop=True)
 for id,family,label,regex,role,A,B,risk in METHODS:
  try: rx=re.compile(regex,flags=re.I)
  except re.error as e:raise ValueError(f'{id} {regex}: {e}')
  match=combined.str.contains(rx,na=False)
  indices=match[match].index.to_list()
  count[id]=len(indices)
  main_rows.append({'ID':id,'Family':family,'Method':label,'Matched_papers':len(indices),'Pct_of_10833':round(len(indices)/10833*100,1),'Role':role,'Track_A_pre_screen':A,'Track_B_pre_screen':B,'Key_barrier':risk,'Regex':regex})
  for j in indices:
   r=records.loc[j]
   # provenance excerpt from the title and abstract rather than a pseudo-citation
   mtch=rx.search(str(r.get('AB','')))
   excerpt= (r.get('AB','')[max(0,mtch.start()-100):mtch.end()+150].replace('\n',' ') if mtch else 'Term found in title/keywords')
   aud.append({'ID':id,'Method':label,'Paper_ID':f'SCR{j+1:05d}','Title':r.get('TI',''),'Authors':r.get('AU',''),'Year':r.get('PY',''),'Journal':r.get('SO',''),'DOI':r.get('DI',''),'Excerpt_unverified':excerpt})
 overview=pd.DataFrame(main_rows)
 overview.to_csv(out/'All_49_Method_Tags.csv',index=False,encoding='utf-8-sig')
 pd.DataFrame(aud).to_csv(out/'Method_to_Paper_Index.csv',index=False,encoding='utf-8-sig')
 matched_ids={x['Paper_ID'] for x in aud}
 not_matched=records.loc[[f'SCR{i+1:05d}' not in matched_ids for i in range(len(records))]].copy()
 not_matched.insert(0,'Paper_ID',[f'SCR{idx+1:05d}' for idx in not_matched.index])
 not_matched.to_csv(out/'Unmatched_Candidates_For_Further_Method_Review.csv',index=False,encoding='utf-8-sig')
 # Audit potential missed technical records without treating the keyword match as a method assignment.
 pending=not_matched.loc[(not_matched.get('TI','')+' '+not_matched.get('AB','')).str.contains(
     r'\b(?:sensor|sensory|portable instrument|spectromet\w*|microplastic detect\w*|particle detect\w*|automated count\w*|in.?situ detector)\b',
     case=False,regex=True,na=False)]
 pending.to_csv(out/'Unclassified_Technical_Leads.csv',index=False,encoding='utf-8-sig')
 metric=['validity','portability','throughput','no_lab','robustness','affordability']
 ranked=[]
 for name,mids,principle,a,b,score in CANDIDATES:
  each=dict(zip(metric,score))
  sA=sum(each[x]*W_A[x] for x in metric)
  sB=sum(each[x]*W_B[x] for x in metric)
  ranked.append({'Concept':name,'Method_IDs':mids,'Working_principle':principle,'Track_A_gate':a,'Track_B_gate':b,
                 'A_weighted_score':round(sA,2),'B_weighted_score':round(sB,2),'Tag_references':';'.join(f'{i}:{count[i]}' for i in mids.split(',')),**each})
 pd.DataFrame(ranked).to_csv(out/'Track_A_B_Weighted_Comparison.csv',index=False,encoding='utf-8-sig')
 # Group count bar chart values via csv; generated .tex tables created separately
 totals=overview.groupby('Family')['Matched_papers'].sum().to_dict()
 notes = ['Screening scope: 10,833 preliminary include candidates; TI+AB+DE+ID; multi-label.',
 'Frequency reflects terminology, NOT verified instrument use or experimental success.',
 'Methods and roles overlap; do not add counts as a study total.',
 'M06 = ultrasound sonication for sample preparation; M23 = explicit ultrasound detection; M24 = acoustic concentration only.',
 'M18 impedance/EIS; M19 resistive-pulse; M35 bulk conductivity proxy. These are distinct.',
 'Code output is reproducible. Selection scores/gates are proposed engineering judgments and should be updated after prototyping.',
 f'{len(METHODS)} method-tags; {len(aud)} paper-tag assignments; {len(matched_ids)} unique matched papers; {len(not_matched)} unmatched papers requiring no forced category; {len(pending)} technical leads to inspect.',
 'High counts in the indirect/proxy family are not evidence of MP specificity.']
 (out/'SCREENING_NOTES.txt').write_text('\n'.join(notes))
 print('\n'.join(notes));print(overview[['ID','Method','Matched_papers']].to_string(index=False))

if __name__=='__main__':main()
