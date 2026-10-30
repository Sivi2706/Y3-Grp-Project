import pandas as pd, json, re, unicodedata, sys
sys.path.insert(0,'.')
U = pd.read_csv('data/q2_unm_papers.csv', index_col=0)
D = pd.read_csv('data/q1_dominant_size_papers.csv')
F = json.load(open('data/funnel_q1.json'))
ALL = pd.read_csv('data/q1_river_pond_lake_microplastic_papers.csv', index_col=0)

def asc(s):
    s = str(s).replace('\\&','&').replace('\\TEXTBACKSLASH','')
    return unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode()
def esc(s):
    s = asc(s)
    for a,b in [('\\','\\textbackslash{}'),('&','\\&'),('%','\\%'),('$','\\$'),('#','\\#'),('_','\\_'),('{','\\{'),('}','\\}'),('~','\\textasciitilde{}'),('^','\\textasciicircum{}')]:
        s = s.replace(a,b)
    return s
PROPER = ['Langat','Semenyih','Malaysia','Malaysian','Selangor','Klang','Cherating','Baram','Miri','Borneo','Perak','China','India','Asia','Southeast','Kelantan','Nottingham','Brazil','Indonesia','Vietnam','Thailand','Pahang','Penang','Melaka','Skudai','Tebrau']
def sentcase(t):
    t = asc(t).lower()
    t = t[:1].upper()+t[1:]
    for p in PROPER: t = re.sub(r'\b'+p.lower()+r'\b', p, t)
    t = re.sub(r'\b(pet|pe|pp|ftir|sem|u-net|ldir|bet|wwtps?|ii)\b', lambda m: m.group(1).upper(), t)
    return t
def authors(a):
    out=[]
    for x in str(a).split(';')[:6]:
        p = x.strip().split()
        if not p: continue
        out.append(p[0].title()+' '+p[1] if len(p)>1 else p[0].title())
    s=', '.join(out)
    if len(str(a).split(';'))>6: s+=' et al.'
    return s
def journal(j): return asc(j).title().replace(' And ',' and ').replace(' Of ',' of ').replace('\\&','&')

# ---------- bibliography ----------
bib = {}
def cite_row(r, key):
    bib[key] = f"{esc(authors(r.AU))} ({int(r.PY)}). {esc(sentcase(r.TI))}. \\textit{{{esc(journal(r.SO))}}}." + (f" doi:\\,{esc(r.DI)}." if isinstance(r.DI,str) else '')
def find(sub, doi=None):
    import pyreadr
    return None
# load full M only for non-UNM refs we cite
import pyreadr
M = pyreadr.read_r(sys.argv[1])['M']
def row(sub):
    h = M[M.TI.str.contains(sub, regex=False)]
    assert len(h)>=1, sub
    return h.iloc[0]
REFS = {
 'zaki24':'TROPICAL RIVERINE SURFACE WATER OF SELANGOR RIVER BASIN',
 'zaki23':'FRESHWATER SEDIMENTS: ABUNDANCE AND DISTRIBUTION IN SELANGOR RIVER BASIN',
 'ali25':'INTEGRATED RISK ASSESSMENT OF MICROPLASTIC POLLUTION IN THE LANGAT RIVER',
 'anuar23':'MULTIDIMENSIONAL APPROACH FOR MICROPLASTICS MONITORING IN TWO MAJOR',
 'bouida26':'MICROPLASTICS IN TROPICAL MALAYSIAN RIVERS: A REVIEW',
 'sheriff26':'MICROPLASTICS UBIQUITY IN FRESHWATER, MARINE AND COASTAL ENVIRONMENTS IN MALAYSIA',
 'hassan25':'TRACKING MICROPLASTICS AT THE SOURCE',
 'cherating20':'CASE STUDY ON CHERATING RIVER',
 'klang21':'AN EVIDENCE IN SURFACE TROPICAL WATER OF KLANG RIVER ESTUARY',
 'baram21':'BARAM RIVER ESTUARY',
 'raipur24':'URBAN TROPICAL FRESHWATER PONDS AS MICROPLASTICS HOTSPOTS',
}
for k,v in REFS.items(): cite_row(row(v),k)
# UNM refs
UK = {}
for i,r in U.iterrows():
    t=r.TI
    key = ('mofijur21' if 'SOURCE, DISTRIBUTION' in t else 'alowaisy26' if 'PHYTOPLANKTON' in t else 'chen21a' if 'SPATIO-TEMPORAL' in t else
           'chen21b' if 'SOUTHEAST ASIA' in t else 'hanun23' if 'WEATHERING' in t else 'chen23' if 'BED SEDIMENTS' in t else
           'lee22' if 'U-NET' in t else 'ng24' if 'FISH AND MACROINVERTEBRATES' in t else 'chen22')
    UK[key]=i; cite_row(r,key)

# ---------- numbers ----------
cls = ['<0.1 mm (<100 um)','0.1-0.5 mm','0.5-1 mm (incl. generic <1 mm)','1-5 mm (ub >1 mm)']
def pct(d): 
    v = d.size_class.value_counts().reindex(cls).fillna(0); return [round(100*x/len(d),1) for x in v], len(d)
pa,na = pct(D); pr,nr = pct(D[D.river]); pl,nl = pct(D[D.lake]); pp,npd = pct(D[D.pond])
cnt = D.size_class.value_counts().reindex(cls).astype(int).tolist()
print(pa,na,pr,nr,pl,nl,pp,npd,cnt)

def coords(p): return ' '.join(f'({x},{y})' for x,y in zip(['lt100','100to500','500to1000','1to5'],p))
tpl = open('scripts/template.tex').read()
sm=lambda d:round(100*(len(d)-int((d.size_class==cls[3]).sum()))/len(d),1)
rep = {
 '@@SUBMM_A@@':str(sm(D)),'@@SUBMM_R@@':str(sm(D[D.river])),'@@SUBMM_L@@':str(sm(D[D.lake])),'@@SUBMM_P@@':str(sm(D[D.pond])),
 '@@N0@@':f"{F['0_all']:,}", '@@N1@@':f"{F['1_abstract']:,}", '@@N2@@':f"{F['2_mp']:,}", '@@N3@@':f"{F['3_fw']:,}",
 '@@N4@@':f"{F['4_wb']:,}", '@@N5@@':f"{F['5_sizeexpr']:,}", '@@N6@@':f"{F['6_dominant_size']:,}",
 '@@C_ALL@@':coords(pa),'@@C_RIV@@':coords(pr),'@@C_LAK@@':coords(pl),'@@C_POND@@':coords(pp),
 '@@NA@@':str(na),'@@NR@@':str(nr),'@@NL@@':str(nl),'@@NP@@':str(npd),
 '@@PA1@@':str(pa[0]),'@@PA2@@':str(pa[1]),'@@PA3@@':str(pa[2]),'@@PA4@@':str(pa[3]),
 '@@CNT1@@':str(cnt[0]),'@@CNT2@@':str(cnt[1]),'@@CNT3@@':str(cnt[2]),'@@CNT4@@':str(cnt[3]),
 '@@PR1@@':str(pr[0]),'@@PR2@@':str(pr[1]),'@@PR3@@':str(pr[2]),'@@PR4@@':str(pr[3]),
 '@@PL1@@':str(pl[0]),'@@PL2@@':str(pl[1]),'@@PL3@@':str(pl[2]),'@@PL4@@':str(pl[3]),
}
# UNM table rows
unm_rows=[]
cat = {'chen21a':'Core -- river monitoring','chen23':'Core -- river monitoring','chen22':'Core -- source apportionment','ng24':'Core -- biota / method comparison',
       'lee22':'Core -- image analysis','chen21b':'Review (SE Asia)','mofijur21':'Peripheral review (Show PL)','alowaisy26':'Peripheral review (Show PL)','hanun23':'Peripheral lab study (Taiwan-led)'}
order=['chen21a','chen21b','chen22','chen23','lee22','ng24','hanun23','mofijur21','alowaisy26']
for k in order:
    r=U.loc[UK[k]]
    unm_rows.append(f"\\cite{{{k}}} & {int(r.PY)} & {esc(sentcase(r.TI))} & {esc(journal(r.SO))} & {int(r.TC)} & {cat[k]} \\\\")
rep['@@UNMROWS@@']='\n'.join(unm_rows)
rep['@@BIB@@']='\n'.join(f"\\bibitem{{{k}}} {v}" for k,v in sorted(bib.items()))
for k,v in rep.items(): tpl = tpl.replace(k,v)
open('report.tex','w').write(tpl)
