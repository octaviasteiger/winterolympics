"""
clean.py
========
Cleans raw Olympic medal data and saves a structured CSV for analysis.

Variables:
SCRIPT_DIR: The directory where the script is located, helps to build file paths relative to the project root
PROJECT_ROOT: The parent directory of the script, and is used as the base directory for saving data
RAW_PATH: The file path to the raw scrapped medal datset
CLEAN_PATH: The location where cleaned data will be saved
COL_NAMES: The column names assigned to raw CSV, and it gives structure to raw data when loading into pandas
MEDAL_COLS: Is a list, and subset of columns containing medal data, used for identifying sport heading rows
is_sport_row: A boolean mask which identifies rows that are sport section headings, so i can seperate sports labels from actual event rows
tie_gold/silver/bronze: Boolean columns indicating whether a medal is shared 
tied_count: counts of tied medals
df: the main pandas Dataframe used
clean: a helper function that processes the raw medal data by removing headers, identifying sport sections, cleaning text, flagging tied medals, retuning a structured dataframe

Raw CSV has no header and 8 columns:
    0: year
    1: event name OR sport section heading OR literal "Sport/Event"
    2: gold winner name
    3: gold country code (NOC)
    4: silver winner name
    5: silver country code (NOC)
    6: bronze winner name
    7: bronze country code (NOC)

Requirements:
    pip install pandas
"""

import pandas as pd
import os

# stops the issue of a new file being made within the scripts folder instead of the data folder when running the script from the terminal
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")

RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "medals_raw.csv")
CLEAN_PATH = os.path.join(PROJECT_ROOT, "data", "clean", "medals_clean.csv")

# The CSV has no header so i have given my own column names 
COL_NAMES = ["year", "event", "gold_name", "gold_noc",
             "silver_name", "silver_noc", "bronze_name", "bronze_noc"]

MEDAL_COLS = ["gold_name", "gold_noc", "silver_name",
              "silver_noc", "bronze_name", "bronze_noc"]


# Functions
# Checking for tied medals
def is_double_noc(noc):
    """Returns True if the NOC field contains 6 uppercase letters (a tied medal)."""
    if pd.isna(noc):
        return False
    noc = str(noc).strip()
    return len(noc) == 6 and noc.isupper() and noc.isalpha()

# Cleaning function
def clean(df):
    """Clean the raw medals dataframe and return a structured version."""

    # Drops column header rows 
    df = df[df["event"] != "Sport/Event"].copy()
    print(f"After dropping header rows: {len(df)} rows")

    # Identify sport section heading rows (every medal column is blank)
    is_sport_row = df[MEDAL_COLS].apply(
        lambda col: col.isna() | (col.str.strip() == "")
    ).all(axis=1)
    print(f"Sport section rows found: {is_sport_row.sum()}")

    # Extract sport name from heading rows and forward-fill to event rows below
    df["sport"] = df["event"].where(is_sport_row)
    df["sport"] = df["sport"].ffill()

    # Drop the sport heading rows, keeping only event rows
    df = df[~is_sport_row].copy()
    print(f"After dropping sport section rows: {len(df)} rows")

    # Strip whitespace from all string columns
    for col in df.columns:
        df[col] = df[col].str.strip()

    # Convert year to integer
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    # Flag tied medals (NOC field contains 6 uppercase letters when two countries share a medal)
    df["tie_gold"] = df["gold_noc"].apply(is_double_noc)
    df["tie_silver"] = df["silver_noc"].apply(is_double_noc)
    df["tie_bronze"] = df["bronze_noc"].apply(is_double_noc)

    tied_count = (df["tie_gold"].sum(), df["tie_silver"].sum(), df["tie_bronze"].sum())
    print(f"Tied medals found:  gold: {tied_count[0]}, silver: {tied_count[1]}, bronze: {tied_count[2]}")

    # Reorder columns
    df = df[["year", "sport", "event",
             "gold_name", "gold_noc", "tie_gold",
             "silver_name", "silver_noc", "tie_silver",
             "bronze_name", "bronze_noc", "tie_bronze"]]

    return df


# Main function

def main():
    if not os.path.exists(RAW_PATH):
        print(f"Raw data not found at {RAW_PATH}")
        print("Run scripts/scrape.py first.")
        return

    df = pd.read_csv(RAW_PATH, header=None, names=COL_NAMES, dtype=str)
    print(f"Loaded {len(df)} rows from {RAW_PATH}")

    df = clean(df)

    os.makedirs(os.path.join(PROJECT_ROOT, "data", "clean"), exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved: {CLEAN_PATH} ({len(df)} rows)")

    # Quick check of work
    print("\nYears present:", sorted(df["year"].dropna().unique().tolist()))
    print("\nEvents per year:")
    print(df.groupby("year").size().to_string())


if __name__ == "__main__":
    main()
