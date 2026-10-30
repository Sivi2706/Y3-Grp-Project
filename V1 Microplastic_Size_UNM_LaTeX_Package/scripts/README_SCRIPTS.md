# Reproduce the paper screening

The scientific input is the **previously deduplicated 10,833-record `Include_Candidates.csv`**. It is intentionally NOT bundled (the source file is approximately 114 MB); the source remains in the user's research project. A `.RData` export helper is supplied but was **not executed** in this environment. We ran the Python screening against the existing exported CSV.

## Files

- `00_original_screening.py`: verbatim original screening implementation preserved for provenance.
- `01_screen_candidates.py`: expanded runnable screen, including a reason for each of the 10,833 rows.
- `02_export_from_RData.R`: optional RStudio helper if you need to recreate the CSV from a specific data frame inside `.RData`. Not executed here; do not confuse the RData object with its prior export without comparing counts and fields.
- `03_verify_outputs.py`: asserts all screening counts and DOI linkage.
- `curation_size_studies.csv`: HUMAN-REVIEWED extraction table of 17 cited exemplar papers. Not discovered by purely automated text matching, and does not represent all eligible studies.
- `requirements.txt` and `run_screening_windows.bat`.

## Running in Windows PowerShell

```powershell
cd "C:\Users\SIVI\Documents\Y3\Group Project\Case studies\Combined\MP_Size_UNM_Literature_Review_Reproducible_2026"
py -m pip install -r scripts\requirements.txt
py scripts\01_screen_candidates.py --input "C:\path\to\Include_Candidates.csv"
py scripts\03_verify_outputs.py
```

If you have only `Bibliometrix_Filtered.RData`, load `scripts/02_export_from_RData.R` in RStudio, inspect the object names and dimensions, and export the correct 10,833-row candidate object. If there is no such object, recover the previously saved `Include_Candidates.csv` from the initial PRISMA screening workflow rather than relabeling a larger R object as 10,833 candidates.

## Logic and meanings

- RQ1: a document is a **first-pass candidate** if title+abstract mentions (microplastic) AND (river/pond/lake/freshwater/reservoir/stream) AND (size terms). A mere definition, e.g. “microplastics are smaller than 5 mm,” can trigger a false positive. The 2,085 records require a human full-text eligibility check; 17 are illustrative curated evidence rows, **not** 17 final inclusions out of 2,085.
- RQ2: query institutional-affiliation fields for Nottingham, then require an explicit Malaysia campus designation or Nottingham address near Semenyih. Counts: 33 Nottingham mentions, nine strict Malaysia-campus matches and 24 ambiguous/other campus entries. A paper may have more campuses; “UNM-affiliated” does not imply lab equipment at UNM was used.
- Reviewed size distributions must be extracted from original results and annotated for sample matrix, collection mesh, minimum detectable size and size-bin definitions. The project does not possess Semenyih raw size-frequency data; the Semenyih graphic is a **known-data / missing-size-data** diagram, not a fabricated histogram.
- Method-performance percent metrics have distinct denominators. The 96% FTIR-confirmation proportion among 85 visually selected particles does not measure whole-workflow sensitivity or recovery.

## Output files

`data/All_10833_Screening_Flags.csv` (per-row selection reasons), `data/Screening_Flow_Stages.csv` (count audit), `data/Waterbody_Size_FirstPass_2085.csv`, `data/Curated_Size_Evidence_Studies.csv`, `data/UNM_9_Full_Evidence.csv`, `data/Nottingham_OtherCampuses_24.csv`, `data/screening_counts.json`.

Python packages: pandas. No internet or AI model required for keyword screening. Bibliographic screening is not a substitute for full-text confirmation.
