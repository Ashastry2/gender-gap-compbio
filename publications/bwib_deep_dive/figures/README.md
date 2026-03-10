# BWIB Deep Dive Blog Post Figures and Tables

This directory contains modular, standalone Python scripts for generating all figures and tables referenced in the **BWIB Deep Dive blog post** (2015-2025 analysis).

## Blog Post

📄 **[BWIB_Deep_Dive_Blog_Post.md](../BWIB_Deep_Dive_Blog_Post.md)** — "Where Do We Stand? Updating a Landmark Study on Gender in Computational Biology"

This analysis replicates the methodology from [Bonham & Stefan (2017)](https://doi.org/10.1371/journal.pcbi.1005134) with contemporary data spanning 2015–2025.

## Figures and Tables

### Figure 1A: P(female) by Author Position
**File:** `figure_1a_position_breakdown.py`

Directly replicates Bonham & Stefan's Fig 1A. Shows the probability that an author in each position (first, second, other, penultimate, last) is female. Compares Biology vs Computational Biology across all positions.

**Run independently:**
```bash
python -m publications.bwib_deep_dive.figures.figure_1a_position_breakdown
```

**Output:** `Fig1A_position_breakdown.png`

---

### Figure 1B: P(female) Over Time
**File:** `figure_1b_temporal_trend.py`

Directly replicates Bonham & Stefan's Fig 1B. Shows temporal trend in female representation from 2015–2025. Line plot with error bars showing Biology and Computational Biology trends separately.

**Run independently:**
```bash
python -m publications.bwib_deep_dive.figures.figure_1b_temporal_trend
```

**Output:** `Fig1B_temporal_trend.png`

---

### Figure 1C: The Female PI Effect
**File:** `figure_1c_pi_effect.py`

Directly replicates Bonham & Stefan's Fig 1C. Demonstrates the "female PI effect": papers with female last authors (presumed principal investigators) have significantly more female co-authors at every position compared to papers with male last authors.

**Run independently:**
```bash
python -m publications.bwib_deep_dive.figures.figure_1c_pi_effect
```

**Output:** `Fig1C_pi_effect.png`

---

### Table 1: Proportion of Female Authors
**File:** `table_1_female_proportion.py`

Directly replicates Bonham & Stefan's Table 1. Shows the mean proportion of female authors for each position, with 95% confidence intervals, for both Biology and Computational Biology (2015–2025).

**Run independently:**
```bash
python -m publications.bwib_deep_dive.figures.table_1_female_proportion
```

**Outputs:**
- `Table1_proportion_female_authors.csv` — Machine-readable format
- `Table1_proportion_female_authors.md` — Markdown-formatted table

---

### Table 2: Female Authors by PI Gender
**File:** `table_2_pi_effect_statistics.py`

Directly replicates Bonham & Stefan's Table 2. Shows the proportion of female authors stratified by the last author's gender (the "female PI effect"), demonstrating that papers with female PIs have more female co-authors at all positions.

**Run independently:**
```bash
python -m publications.bwib_deep_dive.figures.table_2_pi_effect_statistics
```

**Outputs:**
- `Table2_female_authors_with_female_pi.csv` — Machine-readable format
- `Table2_female_authors_with_female_pi.md` — Markdown-formatted table

---

## Running All Figures and Tables

To regenerate all figures and tables at once, use the legacy wrapper script in the parent directory:

```bash
python reproduce_bonham_stefan.py
```

This will run all 5 scripts in sequence and output all figures and tables to the `publications/bwib_deep_dive/` directory.

---

## Shared Utilities

**File:** `utils.py`

Contains shared utility functions used by all figure/table scripts:

- `get_author_data()` — Load author-level data from the database
- `get_paper_author_gender_data()` — Load paper-level data with PI gender classification
- `save_table_to_files()` — Save tables to both CSV and markdown formats
- `OUTPUT_DIR` — Standard output directory for all figures/tables

All scripts import from this module to avoid code duplication and ensure consistent data loading.

---

## Data Sources

All analyses use data from:

1. **PubMed API** — 274,702 papers (2015–2025) across Biology and Computational Biology
2. **SQLite Database** — `data/gender_data.db` with:
   - Author records with gender inference (p_female probability scores)
   - Paper metadata (PMID, year)
   - Author positions (first, second, other, penultimate, last)
3. **Gender Classification**:
   - Offline gender databases (~45k names)
   - LLM-based inference (Groq llama-3.1-8b-instant) for unknowns
   - ~99.1% coverage with 98.4% classification rate for previously unknown names

---

## Reference

Bonham, A. J., & Stefan, M. I. (2017). Women are underrepresented in computational biology: An analysis of the scholarly literature in biology, computational biology, and bioinformatics. *PLOS Computational Biology*, 13(10), e1005134.

https://doi.org/10.1371/journal.pcbi.1005134

---

## Requirements

All scripts require:
- Python 3.9+
- pandas
- numpy
- matplotlib
- sqlite3 (built-in)
- `src.bootstrap` module (from parent project)

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Notes

- All scripts use **bootstrap resampling** (1,000 iterations) for confidence interval estimation
- Confidence intervals are reported as the 2.5th and 97.5th percentiles
- Gender inference uses a threshold of p_female > 0.8 for "female" and < 0.2 for "male" in PI effect analyses
- Ambiguous initial-only names (6.4% of dataset) are excluded from analysis for improved classification reliability
