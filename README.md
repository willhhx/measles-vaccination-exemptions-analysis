# Kindergarten MMR Vaccination, Non-Medical Exemptions, and Measles Cases Across U.S. States, 2024 to 2025

Ecological analysis prepared for the Emory University Journal of Public Health (Original Research).

## Contents
- `latex/manuscript.tex`, `latex/manuscript.pdf`: the paper (compile with `pdflatex manuscript.tex` twice)
- `analysis.py`: full reproducible analysis (pandas, numpy, scipy, matplotlib)
- `build_paper.py`: builds the paper from `outputs/results.json` so every number in the text comes from the analysis
- `data_raw/`: source files (CDC SchoolVaxView; CDC measles cases by jurisdiction as of Nov 5, 2026; U.S. Census Vintage 2025 state estimates)
- `outputs/`: cleaned state table, results (JSON/CSV), figure (PNG, 300 dpi)
- `verification.md`: every claim in the paper with its source and a pass/fail check

## Reproduce
```bash
python3 analysis.py
python3 build_paper.py
```

## Data sources
- CDC. Vaccination Coverage and Exemptions among Kindergartners. https://data.cdc.gov/Vaccinations/Vaccination-Coverage-and-Exemptions-among-Kinderga/ijqb-a7ye
- CDC. Measles Cases and Outbreaks. https://www.cdc.gov/measles/data-research/
- U.S. Census Bureau. State Population Totals and Components of Change: 2020-2025. https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html

Repository: https://github.com/willhhx/measles-vaccination-exemptions-analysis
