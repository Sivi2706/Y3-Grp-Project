#!/usr/bin/env python3
r"""
Water Effects abstract mapping for a Bibliometrix screening export.

Usage:
  python water_effects_histogram.py --input "C:\path\Include_Candidates.csv"
  python water_effects_histogram.py --input "C:\path\All_Screening_Decisions.csv"

Requires:
  pip install pandas matplotlib

Outputs:
  water_effects_category_counts.csv
  water_effects_paper_classifications.csv
  water_effects_histogram.png
  water_effects_unmatched_papers.csv

Interpretation:
  Counts = abstracts/titles mentioning a theme (multi-label).
  Not proof of experimentally demonstrated effects or strength of evidence.
"""
import argparse
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# Regex word boundaries reduce accidental substring matches.
# The categories represent reported / discussed themes, not confirmed effects.
EFFECT_PATTERNS = {
    "Toxicity / mortality": [
        r"\btoxicit(?:y|ies)\b", r"\btoxic effects?\b", r"\bmortalit(?:y|ies)\b",
        r"\blethal(?:ity)?\b", r"\bcell death\b", r"\bcytotoxic\w*\b",
    ],
    "Oxidative stress / inflammation": [
        r"\boxidative stress\b", r"\breactive oxygen species\b", r"\bROS\b",
        r"\binflammat\w*\b", r"\bantioxidant\w*\b", r"\blipid peroxidation\b",
    ],
    "Growth / development": [
        r"\bgrowth (?:inhibit\w*|reduc\w*|impair\w*|retard\w*|rate|performance)\b",
        r"\bdevelopmental (?:toxic\w*|effect\w*|delay\w*|abnormal\w*)\b",
        r"\bstunted growth\b", r"\bbody (?:size|weight|mass)\b",
    ],
    "Reproduction / endocrine": [
        r"\breproduc\w*\b", r"\bfertilit\w*\b", r"\bfecundit\w*\b",
        r"\bendocrine\b", r"\bhormon\w*\b", r"\bembryo\w*\b",
    ],
    "Feeding / behaviour": [
        r"\bfeed(?:ing)? (?:behavio\w*|activit\w*|rate|impair\w*)\b",
        r"\bingestion\b", r"\bbehavio\w*\b", r"\bmovement\b",
        r"\blocomo\w*\b", r"\bavoidance\b",
    ],
    "Bioaccumulation / trophic transfer": [
        r"\bbioaccumulat\w*\b", r"\bbiomagnif\w*\b",
        r"\btrophic transfer\b", r"\bfood (?:chain|web)\b",
        r"\btissue accumulat\w*\b",
    ],
    "Microbial / community change": [
        r"\bmicrobial communit\w*\b", r"\bmicrobiom\w*\b", r"\bmicrobiot\w*\b",
        r"\bbiofilm\w*\b", r"\bcommunity (?:structure|composition|shift\w*)\b",
        r"\bbiodiversit\w*\b",
    ],
    "Water quality / physicochemical": [
        r"\bwater quality\b", r"\bturbidit\w*\b", r"\bdissolved oxygen\b",
        r"\bpH\b", r"\bconductivit\w*\b", r"\bsuspended solids?\b",
        r"\bphysicochemical\b", r"\bwater chemistr\w*\b",
    ],
    "Nutrient cycling / biogeochemistry": [
        r"\bnitrogen cycl\w*\b", r"\bphosphorus cycl\w*\b",
        r"\bnutrient cycl\w*\b", r"\bnitrif\w*\b", r"\bdenitrif\w*\b",
        r"\bbiogeochem\w*\b", r"\bnutrient (?:concentration\w*|dynamics)\b",
    ],
    "Contaminant transport / adsorption": [
        r"\badsorp\w*\b", r"\bdesorp\w*\b", r"\bsorb\w*\b",
        r"\bcontaminant (?:transport|carrier|mobilit\w*)\b",
        r"\bheavy metal\w*\b", r"\bchemical leach\w*\b",
    ],
    "Human health / exposure": [
        r"\bhuman health\b", r"\bhealth risk\w*\b",
        r"\bdietary exposure\b", r"\bdrinking water\b",
        r"\bhuman exposure\b", r"\bpublic health\b",
    ],
    "Habitat / ecosystem functioning": [
        r"\becosystem function\w*\b", r"\becological impact\w*\b",
        r"\bhabitat degrad\w*\b", r"\becosystem health\b",
        r"\bsediment function\w*\b", r"\becosystem servic\w*\b",
    ],
}

COMPILED = {
    category: re.compile("|".join(patterns), flags=re.IGNORECASE)
    for category, patterns in EFFECT_PATTERNS.items()
}


def is_true(value):
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input screening CSV")
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument("--include-manual", action="store_true",
                        help="Include manual-review rows (default: exclude)")
    args = parser.parse_args()

    path = Path(args.input)
    outdir = Path(args.output) if args.output else path.parent / "Water_Effects_Analysis"
    outdir.mkdir(parents=True, exist_ok=True)

    cols_needed = ["TI", "AB", "DI", "PY", "Water_Effects", "Screening_Decision"]
    # Read only columns needed: the original CSV can exceed 100 MB.
    available = list(pd.read_csv(path, nrows=0).columns)
    usecols = [col for col in cols_needed if col in available]
    if "Water_Effects" not in usecols:
        raise ValueError("Input file has no 'Water_Effects' column.")
    df = pd.read_csv(path, usecols=usecols, low_memory=False)

    selected = df["Water_Effects"].map(is_true)
    if "Screening_Decision" in df.columns and not args.include_manual:
        selected &= df["Screening_Decision"].fillna("").str.strip().eq("Include candidate")
    water = df.loc[selected].copy()
    if water.empty:
        raise ValueError("No Water_Effects papers selected; inspect CSV labels.")

    for col in ["TI", "AB", "DI", "PY"]:
        if col not in water:
            water[col] = ""
    text = (water["TI"].fillna("").astype(str) + " " +
            water["AB"].fillna("").astype(str))
    water["Abstract_Available"] = water["AB"].fillna("").astype(str).str.strip().ne("")

    for cat, rx in COMPILED.items():
        water[cat] = text.str.contains(rx, na=False).astype(bool)

    categories = list(COMPILED)
    counts = water[categories].sum().sort_values(ascending=False)
    percent = (counts / len(water) * 100).round(1)

    result = pd.DataFrame({
        "Effect_Category": counts.index,
        "Papers_Mentioning": counts.values.astype(int),
        "Percentage_of_Water_Effects_Papers": percent.values,
    })
    result.to_csv(outdir / "water_effects_category_counts.csv", index=False)

    water["Number_of_Categories"] = water[categories].sum(axis=1)
    water["Matched_Categories"] = water[categories].apply(
        lambda row: "; ".join(row.index[row.to_numpy(dtype=bool)]), axis=1
    )
    export_cols = ["TI", "PY", "DI", "AB", "Screening_Decision",
                   "Abstract_Available", "Matched_Categories",
                   "Number_of_Categories"] + categories
    water[ [x for x in export_cols if x in water] ].to_csv(
        outdir / "water_effects_paper_classifications.csv", index=False
    )
    water.loc[water["Number_of_Categories"].eq(0), ["TI", "PY", "DI", "AB"]].to_csv(
        outdir / "water_effects_unmatched_papers.csv", index=False
    )

    # Single horizontal bar chart (category histogram, multi-label).
    fig, ax = plt.subplots(figsize=(12, 7.5))
    plotted = result.iloc[::-1]
    bars = ax.barh(plotted["Effect_Category"], plotted["Papers_Mentioning"])
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_xlabel("Number of papers mentioning category (title or abstract)")
    ax.set_title(f"Water Effects literature: themes mentioned in {len(water):,} papers")
    ax.grid(axis="x", alpha=0.2)
    ax.set_axisbelow(True)
    ax.set_xlim(right=max(result["Papers_Mentioning"].max() * 1.13, 1))
    fig.text(0.01, 0.012,
             "Multi-label keyword mapping; categories overlap. A mention does not establish a causal effect.",
             fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(outdir / "water_effects_histogram.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    print(f"Water Effects papers analysed: {len(water):,}")
    print(f"With abstracts: {water['Abstract_Available'].sum():,}")
    print(f"No category matched: {(water['Number_of_Categories'] == 0).sum():,}")
    print(result.to_string(index=False))
    print(f"\nSaved files to: {outdir.resolve()}")


if __name__ == "__main__":
    main()
