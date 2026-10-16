# Microplastic concentration mapping -- dual-track background review

## Files
- `main.tex`: main review, stakeholder alignment, two-track TikZ workflow, method screening charts, paper-linked method comparisons, pros/cons and validation steps.
- `references.bib`: 23 cited entries. Original bibliographic metadata was consolidated from the project screening bibliography; the three Chen records were transcribed from the stakeholder's cited reading list.
- `Figures/prisma.png`: supplied preliminary PRISMA-style screening graphic.
- `data/original_14_method_counts.csv`: 14-category keyword screen among 6,654 Lab Methods candidates.
- `data/method_mentions.csv`: targeted technology vocabulary screen among the 10,833 preliminary candidates.
- `main.pdf`: compiled preview.

## Compile (Overleaf)
Upload the whole ZIP to Overleaf. Set `main.tex` as root, pdfLaTeX as compiler, Biber for the references. No external image generation is required because the flowchart and charts are editable TikZ/PGFPlots in `main.tex`.

Local: `pdflatex main.tex` -> `biber main` -> `pdflatex main.tex` -> `pdflatex main.tex`.

## Scope/limitations
These are exploratory keyword-screened results, not a completed systematic review. Subcategories overlap and counts are not independently confirmed field deployments. Methods and claims cited from abstracts need full-text verification. A camera/AI system without polymer confirmation can report suspected MP-like particle concentrations but should not claim chemically verified microplastic concentration. Routine FTIR/Raman access is deliberately excluded from the operational plans; an occasional outside polymer check is presented as optional external validation.

## Two measurement tracks
- A: Boat-mounted pump, flow cell, camera+AI, GPS and in-situ estimated counts; EIS is a feasibility add-on only.
- B: Automated discrete GPS-logged sample collection, portable shoreline filtration/imaging and post-survey mapping.

Neither track should claim a validated MP heat map until recovery, specificity, size limits, repeatability and field matrix challenges are addressed.
