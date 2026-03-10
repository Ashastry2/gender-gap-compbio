#!/usr/bin/env python3
"""
Preprocess ScimagoJR Journal Rankings

This script loads journal rankings from ScimagoJR CSV and stores them in the
SQLite database with fuzzy matching for PubMed journal names.

Must be run once before: python analyze_journal_impact.py

Usage:
    python preprocess_journal_quartiles.py
"""

import sys
from pathlib import Path
from difflib import get_close_matches
from typing import Dict, Tuple

import pandas as pd

from src.db_utils import GenderDatabase


def load_scimagojr_data(filepath: str = "local/scimagojr 2024.csv") -> Dict[str, str]:
    """Load and parse ScimagoJR journal rankings."""
    print(f"Loading ScimagoJR data from {filepath}...")
    df = pd.read_csv(filepath, sep=";", decimal=",")

    # Filter to ranked journals (Q1-Q4)
    df = df[df["SJR Best Quartile"].isin(["Q1", "Q2", "Q3", "Q4"])].copy()

    # Normalize journal title and create lookup
    lookup = {}
    for _, row in df.iterrows():
        title = row["Title"].lower().strip()
        quartile = row["SJR Best Quartile"]
        lookup[title] = quartile

    print(f"✓ Loaded {len(lookup):,} ranked journals from ScimagoJR\n")
    return lookup


def load_pubmed_journals(
    bio_csv: str = "data/processed/pubmed_biology_2015_2025.csv",
    compbio_csv: str = "data/processed/pubmed_compbio_2015_2025.csv"
) -> list:
    """Load unique journal names from PubMed CSVs."""
    print("Loading PubMed journal names...")

    try:
        bio_df = pd.read_csv(bio_csv)
        print(f"  ✓ Loaded {len(bio_df)} biology papers")
    except FileNotFoundError:
        print(f"  ⚠ Biology CSV not found: {bio_csv}")
        bio_df = pd.DataFrame()

    try:
        compbio_df = pd.read_csv(compbio_csv)
        print(f"  ✓ Loaded {len(compbio_df)} computational biology papers")
    except FileNotFoundError:
        print(f"  ⚠ CompBio CSV not found: {compbio_csv}")
        compbio_df = pd.DataFrame()

    # Combine and get unique journals
    all_journals = list(pd.concat([bio_df["journal"], compbio_df["journal"]], ignore_index=True).unique())
    all_journals = [j for j in all_journals if pd.notna(j)]

    print(f"✓ Found {len(all_journals):,} unique journals\n")
    return all_journals


def match_journals(
    pubmed_journals: list,
    scimagojr_lookup: Dict[str, str],
    threshold: float = 0.8
) -> Tuple[Dict[str, str], Dict[str, str], int]:
    """Match PubMed journal names to ScimagoJR quartiles."""
    print("Matching journals to ScimagoJR rankings...")

    matched_journals = {}
    unmatched_journals = {}
    exact_matches = 0
    fuzzy_matches = 0

    scimagojr_titles = list(scimagojr_lookup.keys())

    for journal_name in pubmed_journals:
        if pd.isna(journal_name):
            continue

        normalized = journal_name.lower().strip()

        # Try exact match first
        if normalized in scimagojr_lookup:
            matched_journals[journal_name] = scimagojr_lookup[normalized]
            exact_matches += 1
            continue

        # Try fuzzy match
        matches = get_close_matches(normalized, scimagojr_titles, n=1, cutoff=threshold)
        if matches:
            quartile = scimagojr_lookup[matches[0]]
            matched_journals[journal_name] = quartile
            fuzzy_matches += 1
        else:
            unmatched_journals[journal_name] = None

    match_rate = (len(matched_journals) / len(pubmed_journals) * 100) if pubmed_journals else 0
    print(f"✓ Matched {len(matched_journals)}/{len(pubmed_journals)} journals ({match_rate:.1f}%)")
    print(f"  Exact matches: {exact_matches}")
    print(f"  Fuzzy matches: {fuzzy_matches}")
    print(f"  Unmatched: {len(unmatched_journals)}\n")

    if len(unmatched_journals) <= 20:
        print("Unmatched journals:")
        for j in sorted(unmatched_journals.keys()):
            print(f"  - {j}")
        print()

    return matched_journals, unmatched_journals, len(matched_journals)


def store_journals_in_db(
    matched_journals: Dict[str, str],
    db_path: str = "data/gender_data.db"
):
    """Store matched journals in the database."""
    print("Storing journals in database...")

    db = GenderDatabase(db_path=db_path)

    journal_data = [
        {
            "journal_name": journal_name,
            "quartile": quartile,
            "is_exact_match": True
        }
        for journal_name, quartile in matched_journals.items()
    ]

    db.batch_insert_journals(journal_data)
    db.close()

    print(f"✓ Stored {len(journal_data):,} journals in database\n")


def main():
    """Run the preprocessing pipeline."""
    print("\n" + "="*70)
    print("PREPROCESSING: ScimagoJR Journal Rankings")
    print("="*70 + "\n")

    try:
        scimagojr_lookup = load_scimagojr_data()
        pubmed_journals = load_pubmed_journals()
        matched_journals, unmatched_journals, match_count = match_journals(
            pubmed_journals,
            scimagojr_lookup,
            threshold=0.8
        )
        store_journals_in_db(matched_journals)

        print("="*70)
        print("✓ PREPROCESSING COMPLETE!")
        print("="*70)
        print(f"\n✓ Journal rankings stored in data/gender_data.db")
        print(f"✓ Ready to run: python analyze_journal_impact.py\n")

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nRequired files:")
        print("  - local/scimagojr 2024.csv")
        print("  - data/processed/pubmed_biology_2015_2025.csv (optional)")
        print("  - data/processed/pubmed_compbio_2015_2025.csv")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Preprocessing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
