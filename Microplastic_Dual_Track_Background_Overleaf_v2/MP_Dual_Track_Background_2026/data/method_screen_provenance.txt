# Comprehensive Microplastic Methods Screening (2026)

Standalone IEEE-style LaTeX review with **both** the original 14-category method-screening bar chart (6,654 Laboratory Methods candidate papers) and the targeted emerging-methods chart (10,833 candidate papers), plus in-text cited working principles and chemistry-lab validation plan.

## Files
- `main.tex` and `references.bib`: compile using pdflatex + biber + pdflatex twice (Overleaf: pdfLaTeX + Biber).
- `Data/original_14_method_counts.csv`: previous broad-method screening counts.
- `Data/method_mentions.csv`: targeted emerging-method screening counts.
- `Data/cited_paper_abstracts.csv`: representative citation source audit.
- `Data/method_candidates_for_manual_review.csv`: preliminary matched records.
- `reproduce_method_scan.py`: targeted keyword screening script.
- `main.pdf`: compiled preview.

**Important:** Original 14-method screen and targeted emerging-method screen have different denominators / search fields. They should not be merged into a single percentage or interpreted as definitive equipment use, study quality, or detection capability.
