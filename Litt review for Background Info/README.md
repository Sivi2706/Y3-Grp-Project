# Freshwater Microplastics: Four-Subtopic Literature Map

## Contents
- `main.tex`: 10-page LaTeX literature map with 5 PGFPlots horizontal charts, 4 complete category tables, 4 study-level methods/results tables and one project-validation matrix.
- `references.bib`: 11 source references cited using numeric IEEE citation style (BibLaTeX + Biber).
- `main.pdf`: compiled preview.
- `Figures/prisma.png`: user-provided preliminary screening flow.
- `Data/*_category_counts.csv`: reproducible, count-verified subcategory data.
- `Data/*_paper_tags.csv`: title/DOI/year + automated subcategory labels for review (not full-text study verification).
- `build_classification.py`: regenerate classifications from your original `Include_Candidates.csv`.
- `assemble_tex.py`: rebuild `main.tex` from the generated counts, tables and defined paper examples.
- `water_effects_histogram.py`, `analyse_water_quality_methods.py`: original rule-based classification dictionaries used for the two existing taxonomies.

## Use in Overleaf
Upload `main.tex`, `references.bib`, `Figures/prisma.png`, retaining the folder layout. Compile with pdfLaTeX and Biber. To regenerate charts from updated source data, run Python locally first.

## Regenerate on Windows / VS Code
With Python and `pandas` installed, from this project folder:

```powershell
python -m pip install pandas
python build_classification.py --input "C:\Users\SIVI\Documents\Y3\Group Project\Case studies\Combined\Include_Candidates.csv"
python assemble_tex.py
```

Then rebuild `main.tex` with pdfLaTeX → Biber → pdfLaTeX → pdfLaTeX (or use Overleaf).

## Limitations
- The top-level counts (6,430 / 7,575 / 6,654 / 5,320) come from the original preliminary include candidates, and overlap.
- The 12 Water Effects subcategories reproduce the prior rule-based counts. The Causes, Laboratory Methods and Data Trends subcategories are exploratory title/abstract keyword matches. Each theme's subcategory tags overlap; unmatched items are not screening exclusions.
- Counts do not establish causal effects, real method use, publication quality or validation performance.
- The study-specific examples are based on supplied bibliographic abstracts; read full texts before making definitive claims in a thesis.
