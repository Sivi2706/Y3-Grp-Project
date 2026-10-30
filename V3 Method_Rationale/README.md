# Microplastic dual-track screening and method selection (v3)

## Deliverable
- `main.tex` + `references.bib`: Overleaf-compatible LaTeX report and IEEE-numbered citations
- `Figures/prisma.png`: the previously provided PRISMA-style preliminary screening graphic
- `generated/method_charts.tex`: two PGFPlots method charts automatically regenerated from the 10,833-record screen
- `generated/all_methods_table.tex`: 49 method tag frequencies and track-specific disposition
- `generated/weighted_table.tex`: transparent 19-concept weighted comparison (engineering assumptions)
- `main.pdf`: compiled draft

## Actual screening source and scope
`Include_Candidates.csv` from the 10,833-paper preliminary Web of Science/Scopus merged dataset. The CSV itself is **not** bundled (to avoid duplicating a large user-owned database). The analysis scans `TI`, `AB`, `DE`, and `ID`, uses explicit regular expressions, and keeps overlapping tags.

**Results in this version**
- 10,833 records scanned
- 49 defined method-term tags; five role families
- 6,483 paper–method assignments
- 3,974 distinct papers matched at least one defined term
- 6,859 papers unmatched by the defined dictionary (NOT excluded from the review)
- 137 unmatched papers flagged for additional technical-method screening

This is a terminology index, NOT a systematic full-text appraisal. It is not evidence that every matched article used the method experimentally or that it demonstrated reliable MP concentration measurement. It does not exhaust all possible instruments. Full-text review and expansion of the dictionary remain necessary, especially among technical leads.

## Data files
- `data/All_49_Method_Tags.csv` — taxonomy, keyword rules, role, count, Track A/B disposition
- `data/Method_to_Paper_Index.csv` — papers behind each tag (title, authors, year, DOI, excerpt)
- `data/Unmatched_Candidates_For_Further_Method_Review.csv` — all initially unmatched candidates
- `data/Unclassified_Technical_Leads.csv` — subset of unmatched candidates with possible technical-method terms
- `data/Track_A_B_Weighted_Comparison.csv` — transparent concept scores, six criteria, Track A/B gates
- `data/SCREENING_NOTES.txt` — limitations and distinctions

The existing chart of 14 broad methodology categories is retained from the earlier 6,654 Laboratory Methods candidates. The new 49-tag dictionary screens all 10,833 and uses different fields and rules. **Do not combine their counts or expect identical labels to have equal counts.**

## Re-run in Windows VS Code / PowerShell
Place `Include_Candidates.csv` alongside the scripts or adjust the path.

```powershell
python -m pip install pandas
python reproduce_screening.py --input ".\Include_Candidates.csv" --out ".\data"
python build_selection_sections.py
```

Compile in Overleaf (pdfLaTeX + Biber), or locally:

```powershell
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

## Engineering interpretation
P = preferred core route; C = conditional prototype test; S = support (not a standalone MP counter); X = excluded **as a routine field/core device**, not scientifically invalid. Track A assumes boat/wet sensing, Track B assumes measured-volume collection and shoreline processing. Weighted scores are explicitly provisional judgments; hard-gate failures override them. Any concentration estimate without polymer-confirmed specificity must be labelled as MP-like/suspected particle concentration.

Main deliverable recommendation: Track B portable collection + filter + imaging/AI is the simplest testable map route. Track A flow-through imaging/AI is the live-track leading prototype. EIS/resistive pulse, polarisation and selected optical alternatives remain conditional. Regardless of track, record water volume, detectable size, georeferenced intake time, quality flags and uncertainty.
