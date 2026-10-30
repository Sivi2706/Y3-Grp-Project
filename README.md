# Microplastic survey engineering package v4

Two independent LaTeX documents and reproducible engineering assumptions.

- `Method_Rationale/main.tex` updates the original 10,833-paper method-screening document with **G6-G10**, including the two-hour/400-square-metre feasibility gates. The existing 49-tag screening rules and provenance are retained. `Method_Rationale/data/2h_Method_Operational_Gates.csv` adds transparent operational filter results; **this is not a new PRISMA screen**.
- `Boat_Critical_Components/boat_components.tex` separately documents electronics, motor/thrust, buoyancy, pump, GNSS, ArduPilot boat reuse, communications, LiFePO4 power and 2-hour operational scenarios.
- `scripts/design_inputs.json` contains edit-ready numerical assumptions, and `scripts/recalculate_boat.py` produces recalculated CSVs/JSON. Run `scripts/operational_gate_screen.py` to regenerate the separate project-level method screen.
- Neither document should imply the boat has been built or validated; maker specifications are distinct from calculated estimates.

## Key computed engineering assumptions
- Full wet loaded vessel: 22.0 kg (including 8 litres retained sample water), displacement at full submergence 56.5 kg; initial 60% working budget 33.9 kg.
- LiFePO4 example nominal 256 Wh; with 80% usable fraction 204.8 Wh.
- Track A example 93.0 min; Track B example 95.9 min. Both are preliminary timing models.
- At 3.12 particles/L, a 1-L station has expected count 3.12 and Poisson relative standard error ≈ 57%; the measurement quality constraint is distinct from map completion.

## Reproducing the outputs in Windows PowerShell
```
py scripts\recalculate_boat.py
py scripts\operational_gate_screen.py
cd Method_Rationale
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
cd ..\Boat_Critical_Components
pdflatex boat_components.tex
biber boat_components
pdflatex boat_components.tex
pdflatex boat_components.tex
```

Original bibliometric re-screen, when source CSV is present:
```
cd Method_Rationale
python -m pip install pandas
python reproduce_screening.py --input "C:\path\Include_Candidates.csv" --out data
python build_selection_sections.py
```
Note: do not regenerate method counts without the actual underlying 10,833 paper CSV, and do not treat bibliography keyword matches as full-text validation.
