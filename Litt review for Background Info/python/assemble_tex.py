from pathlib import Path
import pandas as pd, re, shutil
R=Path(__file__).resolve().parent
D=R/'Data'

SECTIONS=[
 ('Causes','causes','Causes and sources of microplastics','The largest exploratory source tags concern plastic litter/degradation and wastewater. These labels indicate language in the papers, not source-apportionment results. To identify genuine inputs, quantitative source tracking, site characteristics, and reference sampling are needed.'),
 ('Water_Effects','water_effects','Effects on water and aquatic systems','The twelve established Water Effects labels span physicochemical measurements, biological endpoints, contaminant interactions, and exposure. They overlap and should not be interpreted as numbers of studies confirming adverse effects. For device design, the relevant subset is that reporting paired water-property and laboratory microplastic measurements.'),
 ('Lab_Methods','laboratory_methods','Laboratory and measurement methods','The method groups describe techniques mentioned in the relevant titles and abstracts. A match does not establish that the technique was actually used in a study. Laboratory reference counting with polymer confirmation and contamination controls is needed to calibrate any proposed field proxy.'),
 ('Data_Trends','data_trends','Data trends, monitoring and spatial mapping','This exploratory categorisation describes spatial, temporal, monitoring, modelling and imaging vocabulary. Studies predicting water attributes from images must be distinguished from studies estimating laboratory-confirmed microplastic concentrations with independent validation.'),
]
EXAMPLES={
'Causes':[
(r'Odora et al. \cite{MPWE00007}', 'Six Balu River surface-water stations near different industrial operations.', r'Mean 102.5 $\pm$ 12.83 items/L; site means differed. Observational site differences are not causal source attribution.'),
(r'Fan et al. \cite{MPWE00013}', 'Ten Yangtze River sites; stereomicroscopy and micro-FTIR on water and sediment.', r'Surface-water abundance 46.7--204 particles/L; separate sediment data. Provides spatial/matrix context.'),
(r'Di and Wang \cite{MPWE00126}', 'Reservoir surface-water and sediment survey with micro-Raman identification.', r'Water: 1,597--12,611 particles/m$^3$; different patterns were observed in sediments.'),
],
'Water_Effects':[
(r'Liu and Li \cite{MPWE00002}', 'Statistical analysis of microplastics, nitrogen and electrical conductivity in Chinese surface waters.', r'Electrical conductivity was reported as a mediator (path coefficient 0.521); \emph{not} a validated MP concentration sensor.'),
(r'Sau et al. \cite{MPWE02100}', 'Sampling of 24 urban ponds/lakes with water-quality correlations and SVM classification.', r'Reported negative associations with turbidity/DO and positive associations with pH and TDS in that dataset; transfer to rivers is untested.'),
(r'Rojas-Luna et al. \cite{MPWE00090}', 'Six lake stations across wet and dry seasons; filtration after digestion and density separation.', r'Abstract reports mean MP abundance 1.90 particles/L in rainy versus 0.25 particles/L in dry season.'),
],
'Lab_Methods':[
(r'Ermolin \cite{MPWE00061}', 'Review of water/sediment sampling, size/density separation and digestion methods.', r'Explains why sample preparation and recovery controls must be selected for the matrix; no single universal approach.'),
(r'Rojas-Luna et al. \cite{MPWE00090}', r'72 water samples; H$_2$O$_2$ digestion, NaCl density separation, and filtration.', r'Observed abundance ranged from zero to 3.83 particles/L; laboratory extraction method affects the reportable fraction.'),
(r'Fan et al. \cite{MPWE00013}', 'Digital stereomicroscope for particle counting and micro-FTIR for polymer identification.', r'Illustrates the distinction between suspected particle enumeration and polymer confirmation.'),
(r'Narwal and Katyal \cite{MPWE00012}', 'Stereomicroscopy, electron microscopy and ATR-FTIR in surface waters.', r'Abstract reports 16--28 particles/L and polyethylene/polypropylene/polystyrene in analysed samples.'),
],
'Data_Trends':[
(r'Sau et al. \cite{MPWE02100}', 'Sentinel-2 remote sensing, GIS and support-vector-machine analysis.', r'Study reports morphology SVM accuracy of 89\%; remote-sensing validation values are study-specific and require independent replication.'),
(r'Chabot and Marteinson \cite{MPWE04211}', 'Review of aerial spectral, surface-roughness and indirect-proxy approaches.', r'Identifies approaches as largely experimental rather than established operational MP measurements.'),
(r'Liu et al. \cite{MPWE01416}', r'Polarised scattering at 120$^\circ$ and machine-learning classification.', r'Experimental discrimination of polystyrene particles from algae/natural samples; not yet a calibrated river-wide concentration map.'),
(r'Rojas-Luna et al. \cite{MPWE00090}', 'Repeated wet/dry season field sampling.', r'Seasonal difference illustrates why spatial maps need sampling date, rainfall and measurement uncertainty.'),
]
}

def esc(s):
    return (str(s).replace('\\','\\textbackslash{}').replace('&','\\&').replace('%','\\%').replace('_','\\_')
            .replace('#','\\#').replace('$','\\$').replace('{','\\{').replace('}','\\}'))

def overview_plot(filename,counts,height='8cm', maxlabel=0):
    rec=list(counts.itertuples(index=False))
    # low to high in y so largest appears uppermost
    rec=list(reversed(rec))
    names=[esc(str(r.Category).replace(' / ', ' / ')) for r in rec]
    positions=','.join(map(str,range(len(rec))))
    ymax=max(float(r.Count) for r in rec)*1.25
    coords=' '.join(f'({int(r.Count)},{i})' for i,r in enumerate(rec))
    return rf'''\begin{{figure}}[H]
\centering
\begin{{tikzpicture}}
\begin{{axis}}[
 xbar, bar width=6pt, width=0.61\textwidth, height={height},
 xmin=0, xmax={int(ymax)},
 ymin=-0.65,ymax={len(rec)-0.35},
 ytick={{{positions}}},
 yticklabels={{{','.join(names)}}},
 yticklabel style={{font=\scriptsize,align=right,text width=4.3cm}},
 tick label style={{font=\scriptsize}},
 xlabel={{Papers with title/abstract category match}},
 xlabel style={{font=\small}},
 axis x line*=bottom, axis y line*=left,
 xmajorgrids=true, grid style={{gray!18}},
 nodes near coords, point meta=x,
 every node near coord/.append style={{font=\tiny,anchor=west,xshift=1pt}},
 enlarge y limits=0.03,
]
\addplot+[draw=teal!80!black,fill=teal!65] coordinates {{{coords}}};
\end{{axis}}
\end{{tikzpicture}}
\caption{{{filename}: automated, overlapping title/abstract subcategory mentions; not verified study findings.}}
\end{{figure}}
'''

preamble=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=2.0cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype}
\usepackage{graphicx,booktabs,array,tabularx,longtable,float,caption}
\usepackage[table]{xcolor}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning}
\usepackage{csquotes}
\usepackage[colorlinks=true,citecolor=blue!55!black,linkcolor=blue!55!black,urlcolor=blue!55!black]{hyperref}
\usepackage[backend=biber,style=ieee,sorting=none,doi=true,url=false]{biblatex}
\addbibresource{references.bib}
\definecolor{teal}{RGB}{21,120,135}
\renewcommand{\arraystretch}{1.16}
\setlength{\parskip}{4pt}
\emergencystretch=3em
\title{Microplastic Pollution in Freshwater\\\large Four-Subtopic Literature Map and Method--Effect Evidence Tables}
\author{Y3 Group Project\\vesh sivi}
\date{October 2026}
\begin{document}
\maketitle
\begin{abstract}
This draft summarises four overlapping sets derived from 10,833 preliminary Web of Science--Scopus include candidates: Causes (6,430), Water Effects (7,575), Laboratory Methods (6,654) and Data Trends (5,320). Tables and PGFPlots charts list every \emph{defined} subcategory and its automated title/abstract match frequency. A second table under each theme gives examples of methods and abstract-reported findings with indexed IEEE citations. The review supports planning a reference-laboratory validation strategy; it is \textbf{not a final full-text systematic review}. Subcategory frequencies are multi-label and must not be interpreted as experimentally established effects.
\end{abstract}
\section{Literature identification and classification}
From 18,942 database records (8,923 Web of Science; 10,019 Scopus), deduplication removed 7,318 records and document-type filtering excluded 727. The remaining 10,897 records yielded 10,833 preliminary include candidates and 64 requiring manual review. Four overlapping top-level themes were assigned to candidate papers; these are not four mutually exclusive bodies of evidence.
\begin{figure}[H]
\centering
\includegraphics[width=0.70\linewidth,height=.58\textheight,keepaspectratio]{Figures/prisma.png}
\caption{Preliminary PRISMA-style screening and thematic classification; final eligibility and full-text review remain outstanding.}
\end{figure}
\begin{table}[H]\centering\small
\caption{Top-level thematic classifications from 10,833 preliminary include candidates.}
\begin{tabular}{lrr}\toprule
Theme & Papers tagged & Share of candidates \\\midrule
Causes and sources & 6,430 & 59.4\% \\
Water effects & 7,575 & 69.9\% \\
Laboratory methods & 6,654 & 61.4\% \\
Data trends and mapping & 5,320 & 49.1\% \\\bottomrule
\end{tabular}
\end{table}
'''

pieces=[preamble]
maincounts=pd.DataFrame([('Causes and sources',6430),('Water effects',7575),('Laboratory methods',6654),('Data trends and mapping',5320)],columns=['Category','Count'])
pieces.append(overview_plot('Four main research themes',maincounts,'5.5cm'))
pieces.append(r'''\noindent\textbf{Classification note.} The Water Effects keywords reproduce the previously reported twelve-theme classification. The other three themes are newly subdivided using explicit keyword dictionaries supplied in the companion Python file. All four groups are multi-label, and both keyword omissions and false matches are possible. Percentages below use the number of candidates \emph{within that parent theme}, not the overall 10,833 records.
''')
for key,slug,title,summary in SECTIONS:
    dat=pd.read_csv(D/f'{slug}_category_counts.csv')
    summ=pd.read_csv(D/f'{slug}_summary.csv').iloc[0]
    pieces.append(r'\clearpage'+ '\n'+rf'\section{{{title}}}'+'\n')
    pieces.append(esc(summary)+'\n')
    pieces.append(overview_plot(title,dat,f'{max(6.7, 0.5*len(dat)+1.5):.1f}cm'))
    pieces.append(r'\begin{table}[H]\centering\footnotesize'+'\n')
    pieces.append(rf'\caption{{Complete defined subcategory list within {title.lower()} (n={int(summ.Total_candidates):,}).}}'+'\n')
    pieces.append(r'\begin{tabularx}{\linewidth}{@{}Xrr@{}}\toprule Subcategory & Tagged papers & Within-theme share \\ \midrule'+'\n')
    for rr in dat.itertuples(index=False):
        pieces.append(f'{esc(rr.Category)} & {int(rr.Count):,} & {rr.Percent:.1f}\\% '+r'\\'+'\n')
    pieces.append(r'\midrule'+ '\n')
    pieces.append(f'No defined subcategory term matched & {int(summ.Unmatched_by_defined_categories):,} & {int(summ.Unmatched_by_defined_categories)/int(summ.Total_candidates)*100:.1f}\\% '+r'\\'+'\n')
    pieces.append(r'\bottomrule\end{tabularx}\end{table}'+'\n')
    pieces.append(r'\noindent\footnotesize\emph{Counts overlap; a paper can be in several rows. The unmatched count reflects this specific dictionary, not a screening exclusion.}\normalsize'+'\n')
    pieces.append(r'\begin{table}[H]\centering\scriptsize'+'\n')
    pieces.append(rf'\caption{{Illustrative study-level methodology and reported findings for {title.lower()}. Findings are extracted/paraphrased from supplied abstracts and require full-text verification.}}'+'\n')
    pieces.append(r'\begin{tabularx}{\linewidth}{@{}p{2.8cm}XX@{}}\toprule Study & Method or working principle & Abstract-reported observation / implication \\ \midrule'+'\n')
    for name,method,result in EXAMPLES[key]:
        pieces.append(f'{name} & {method} & {result} '+r'\\[2pt]'+'\n')
    pieces.append(r'\bottomrule\end{tabularx}\end{table}'+'\n')

pieces.append(r'''\clearpage
\section{Compiled method--effect comparison and next decisions}
\begin{table}[H]\centering\footnotesize
\caption{Connecting literature methods and effects to the proposed controlled-sample experiment.}
\begin{tabularx}{\linewidth}{@{}p{3.0cm}XX@{}}\toprule
Observed / studied relationship & Example literature evidence & What to validate in our chemistry laboratory \\ \midrule
Spatial differences in particle abundance & Balu and Yangtze sampling \cite{MPWE00007,MPWE00013} & Replicate reference concentration by site and time; retain sample volume and GPS position. \\
MPs and nitrogen / conductivity & Surface-water statistical analysis \cite{MPWE00002} & Ionic strength and turbidity must vary independently of MP dose; assess whether adding MP improves prediction. \\
Wet/dry season variation & Repeated seasonal lake sampling \cite{MPWE00090} & Test model transfer across time and rainfall conditions. \\
Particle recovery and chemical identification & Sample-preparation review and stereomicroscope--FTIR surveys \cite{MPWE00061,MPWE00013,MPWE00012} & Quantify blank contamination, spike recovery, repeatability and polymer-confirmation rate. \\
Optical scattering and particle discrimination & Polarised-scattering experiments \cite{MPWE01416} & Challenge the sensor with algae, mineral sediments, differently sized polymers and mixed matrices. \\
Spatial prediction and aerial imagery & GIS/SVM study and aerial review \cite{MPWE02100,MPWE04211} & Train with georeferenced paired sensor--reference data; validate on completely withheld sites and days. \\
\bottomrule\end{tabularx}
\end{table}
\begin{figure}[H]\centering
\begin{tikzpicture}[node distance=3.5mm,b/.style={draw=teal!75!black,rounded corners,fill=teal!7,align=center,text width=0.77\linewidth,minimum height=8mm,font=\small},>=Latex]
\node[b](standards){Prepare clean-water blanks and independently characterised MP spike levels};
\node[b,below=of standards](matrices){Repeat with sediment / ionic / organic-matter interference controls};
\node[b,below=of matrices](reference){Collect laboratory reference counts; verify polymer and particle-size range};
\node[b,below=of reference](proxy){Record matched turbidity, conductivity, pH, temperature and imaging signals};
\node[b,below=of proxy](model){Fit a calibrated model; assess error, recovery, limits and uncertainty};
\node[b,below=of model](field){Blind test at withheld river locations / dates before drawing MP maps};
\foreach \x/\y in {standards/matrices,matrices/reference,reference/proxy,proxy/model,model/field} \draw[->,thick,teal](\x)--(\y);
\end{tikzpicture}
\caption{Proposed laboratory-to-field validation chain. This is a project plan, not a tested result.}
\end{figure}
\section{Interpretation and limitations}
The four top-level counts originate from preliminary screening, not final inclusion; 64 additional records await manual review. Subcategory labels are automated mentions in title/abstract text. Their counts may include reviews, descriptions of prior methods or hypotheses, and do not determine effectiveness, causality or evidence quality. The study examples illustrate different working principles but do not represent a quantitative synthesis of all candidate papers. Before final thesis conclusions, complete full-text screening, confirm reported effects and citations, and pre-specify the calibration and external-validation protocol with the chemistry laboratory.
\printbibliography[title={References}]
\end{document}
''')
tex=''.join(pieces)
tex=tex.replace('\\n\\clearpage','\n\\clearpage')
(R/'main.tex').write_text(tex,encoding='utf-8')
if not (R/'references.bib').exists() or not (R/'Figures'/'prisma.png').exists():
    raise FileNotFoundError('Place references.bib and Figures/prisma.png alongside this script')
print('wrote',R/'main.tex')
