"""
Shared utilities for BWIB Deep Dive analysis figures.

Provides common data loading and helper functions for all figures and tables.
"""

import sqlite3
from pathlib import Path
import pandas as pd


# Configuration
DB_PATH = "data/gender_data.db"
OUTPUT_DIR = Path("publications/bwib_deep_dive")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_author_data(start_year=2015, end_year=2025):
    """
    Load author data from database and CSV files to distinguish Biology vs Comp Bio.

    Args:
        start_year: Start year for data range (default 2015)
        end_year: End year for data range (default 2025)

    Returns:
        DataFrame with columns: name, p_female, position, dataset, year, pmid
    """
    conn = sqlite3.connect(DB_PATH)

    # Load biology data
    bio_query = """
    SELECT
        a.name,
        a.p_female,
        ap.position,
        'Biology' as dataset,
        p.year,
        p.pmid
    FROM author_positions ap
    JOIN authors a ON ap.author_id = a.id
    JOIN papers p ON ap.paper_id = p.id
    WHERE p.year >= ? AND p.year <= ?
    ORDER BY p.pmid
    """

    bio_df = pd.read_sql_query(bio_query, conn, params=(start_year, end_year))

    # Load computational biology PMIDs from CSV to filter
    comp_pmids = set()
    comp_csv = Path("data/processed/pubmed_compbio_2015_2025.csv")
    if comp_csv.exists():
        comp_csv_df = pd.read_csv(comp_csv, usecols=['pmid'])
        comp_pmids = set(comp_csv_df['pmid'].astype(str).unique())

    # Mark papers that are in the comp bio CSV as Computational Biology
    bio_df['dataset'] = bio_df['pmid'].astype(str).apply(
        lambda x: 'Computational Biology' if x in comp_pmids else 'Biology'
    )

    conn.close()
    return bio_df


def get_paper_author_gender_data(start_year=2015, end_year=2025):
    """
    Get paper-level data for PI effect analysis with Biology vs Comp Bio distinction.

    Args:
        start_year: Start year for data range (default 2015)
        end_year: End year for data range (default 2025)

    Returns:
        DataFrame with columns: name, p_female, position, dataset, year, pmid, last_author_gender
    """
    conn = sqlite3.connect(DB_PATH)

    # Get last author gender for each paper
    query = """
    WITH last_authors AS (
        SELECT
            ap.paper_id,
            a.p_female as last_author_pfemale
        FROM author_positions ap
        JOIN authors a ON ap.author_id = a.id
        WHERE ap.position = 'last'
    )
    SELECT
        a.name,
        a.p_female,
        ap.position,
        'Biology' as dataset,
        p.year,
        p.pmid,
        CASE
            WHEN la.last_author_pfemale > 0.8 THEN 'female'
            WHEN la.last_author_pfemale < 0.2 THEN 'male'
            ELSE 'unknown'
        END as last_author_gender
    FROM author_positions ap
    JOIN authors a ON ap.author_id = a.id
    JOIN papers p ON ap.paper_id = p.id
    JOIN last_authors la ON p.id = la.paper_id
    WHERE p.year >= ? AND p.year <= ?
    AND la.last_author_pfemale IS NOT NULL
    ORDER BY p.pmid
    """

    df = pd.read_sql_query(query, conn, params=(start_year, end_year))

    # Load computational biology PMIDs from CSV to filter
    comp_pmids = set()
    comp_csv = Path("data/processed/pubmed_compbio_2015_2025.csv")
    if comp_csv.exists():
        comp_csv_df = pd.read_csv(comp_csv, usecols=['pmid'])
        comp_pmids = set(comp_csv_df['pmid'].astype(str).unique())

    # Mark papers that are in the comp bio CSV as Computational Biology
    df['dataset'] = df['pmid'].astype(str).apply(
        lambda x: 'Computational Biology' if x in comp_pmids else 'Biology'
    )

    conn.close()
    return df


def save_table_to_files(df, prefix, title):
    """
    Save a table to both CSV and markdown formats.

    Args:
        df: DataFrame to save
        prefix: Filename prefix (e.g., "Table1_proportion_female_authors")
        title: Human-readable title for markdown file
    """
    # Save as CSV
    csv_path = OUTPUT_DIR / f"{prefix}.csv"
    df.to_csv(csv_path, index=False)

    print(f"✓ {title} saved to {csv_path}")
    return csv_path
