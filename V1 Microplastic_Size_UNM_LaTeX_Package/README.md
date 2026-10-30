# Microplastic sizes, Semenyih River and Nottingham Malaysia laboratory methodology

This is the **revised reproducible Overleaf package**. Main paper: `main.tex`, bibliography: `references.bib`, precompiled output: `main.pdf`.

## Refined research questions

1. Which microplastic size fractions are commonly *reported* in river/pond water, and how do sampler/size thresholds change what can be observed?
2. What is genuinely documented about **Semenyih River** size, morphology and water concentration? Do not substitute Langat size fractions for Semenyih.
3. Which studies in the screening dataset have confirmed **University of Nottingham Malaysia affiliations**, and what lab methods, apparatus, identification evidence, validation and findings do they describe?

## The scripts folder is included

See `scripts/README_SCRIPTS.md`. It contains the **original script used in the previous version**, an expanded reproducible script, a manual DOI curation list, a verification script, a Windows batch launcher and an optional RStudio `.RData`-to-CSV export helper.

### One-command Windows rerun

From PowerShell, after extracting the ZIP:

```powershell
cd "C:\Users\SIVI\Documents\Y3\Group Project\Case studies\Combined\MP_Size_UNM_Literature_Review_Reproducible_2026"
scripts\run_screening_windows.bat "C:\path\to\Include_Candidates.csv"
```

Or:

```powershell
py -m pip install -r scripts\requirements.txt
py scripts\01_screen_candidates.py --input "C:\path\to\Include_Candidates.csv"
py scripts\03_verify_outputs.py
```

The **actual screening conducted here** used the earlier 10,833-row `Include_Candidates.csv` export already present in the project. The attached `Bibliometrix_Filtered(1).RData` workspace was NOT executed using R (R is unavailable in this runtime); `scripts/02_export_from_RData.R` is an optional helper supplied for the user's RStudio, and not a script claimed to have run. The full source CSV (~114 MB) is **not included** in the ZIP, to avoid duplicating the research corpus. The row-level decisions and selected records **are** included.

## What is and is not an 'included study'

- Original pool: 10,833 preliminary records from the prior merged WoS/Scopus screening.
- RQ1 title/abstract keyword screen: 2,085 records, **not 2,085 fully eligible papers**.
- 17 DOI-selected papers form a **human-reviewed representative evidence set**; this is not exhaustive screening of all 2,085 full texts.
- Affiliation query: 33 Nottingham-affiliation mentions, 9 explicit Malaysia-campus matches in this corpus, and 24 other/uncertain campus records. Completeness is limited to the supplied records and available affiliation metadata.
- Semenyih River: the paper reports 3.12 ± 2.49 particles/L (water) and fibre-dominated morphology, but the accessible article abstract does not establish a quantitative **size-bin histogram**. The diagram shows that gap. Nearby Langat data are shown as a clearly labelled **regional comparator**, not a Semenyih observation.
- A 96% FTIR visual-identification check in n=85 selected particles is a subset-specific agreement figure, **not** the whole sampling and processing recovery, not sensitivity, and not the measurement accuracy of a newly built device.

## ZIP contents

- `main.tex`, `references.bib`, `main.pdf`
- `scripts/00_original_screening.py` — actual original code, unchanged
- `scripts/01_screen_candidates.py` — enhanced re-run version; executed on corpus
- `scripts/02_export_from_RData.R` — optional RStudio helper, not executed
- `scripts/03_verify_outputs.py` — executed verification script
- `scripts/curation_size_studies.csv` — curated DOI-based evidence (17 rows)
- `scripts/requirements.txt`, `scripts/run_screening_windows.bat`, `scripts/README_SCRIPTS.md`
- `data/All_10833_Screening_Flags.csv` — all 10,833 records, Boolean flags and reasons
- `data/Screening_Flow_Stages.csv`, `data/screening_counts.json` — count audit and hashes
- `data/Waterbody_Size_FirstPass_2085.csv`, `data/Curated_Size_Evidence_Studies.csv`
- `data/UNM_9_Full_Evidence.csv`, `data/Nottingham_OtherCampuses_24.csv`
- `data/doi_citation_keys.csv` — source DOI-to-citation mapping

## Overleaf instructions

Upload the ZIP to Overleaf, set `main.tex` as main, use **pdfLaTeX + Biber** and compile. The PDF is included for immediate viewing; no source CSV is needed for LaTeX compilation because the figures/tables use the screened findings embedded in the document.

## Research and practical boundaries

UNM affiliations do not prove that all cited instruments remain available on campus today. Thesis-reported instrumentation is reported as *documented in the associated research*, not a current university equipment inventory. Chemical processing procedures should only be undertaken using approved laboratory facilities. FTIR/Raman polymer validation, microscopy particle counting and collection recovery are separate metrics. No unverified numeric size percentages for Semenyih have been manufactured.
