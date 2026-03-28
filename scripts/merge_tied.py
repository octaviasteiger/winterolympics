""" 
merge_tied.py 

merges the tied medal rows back into the worldbank dataset
run after world_bank_medals.py
requirements:
    pip install pandas

"""
import pandas as pd
import os

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
WORLD_BANK_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'worldbank.csv')
TIED_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'tied_noc.csv')
OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'worldbank_final.csv')

# Host NOC lookup

HOST_NOC = {
    1924: 'FRA', 1928: 'SUI', 1932: 'USA', 1936: 'GER',
    1948: 'SUI', 1952: 'NOR', 1956: 'ITA', 1960: 'USA',
    1964: 'AUT', 1968: 'FRA', 1972: 'JPN', 1976: 'AUT',
    1980: 'USA', 1984: 'YUG', 1988: 'CAN', 1992: 'FRA',
    1994: 'NOR', 1998: 'JPN', 2002: 'USA', 2006: 'ITA',
    2010: 'CAN', 2014: 'RUS', 2018: 'KOR', 2022: 'CHN'
}

# The columns that must be present in the final file

KEEP_COLS = ['year', 'event', 'noc', 'medal', 'iso_code', 'gdp_per_capita',
            'population', 'host_noc', 'is_host', 'log_gdp_per_capita', 'log_population']

def load_data():
    if not os.path.exists(WORLD_BANK_PATH):
        print(f"ERROR: worldbank.csv not found at {WORLD_BANK_PATH}")
        print("Run scripts/world_bank_medals.py first")
        return None, None
    
    wb = pd.read_csv(WORLD_BANK_PATH)
    tied = pd.read_csv(TIED_PATH)

    print(f"Loaded worldbank.csv: {len(wb)} rows")
    print(f"Loaded tied_noc.csv:  {len(tied)} rows")
    print(f"Dash placeholder rows: {(wb['noc'] == '—').sum()}")
 
    return wb, tied
 
 
def remove_placeholders(wb): # remove placeholder rows left from world_bank_medals.py
    
    wb_clean = wb[wb['noc'] != '—'].copy()
    print(f"\nAfter removing '—' rows: {len(wb_clean)} rows remaining")
    return wb_clean
 
 
def build_gdp_lookup(wb_clean):
    # Build a lookup table of GDP/population values by country-year, used to enrich the tied rows, which were saved without this info.
    # One row per country-year — takes the first non-null value found.
    
    gdp_lookup = ( 
        wb_clean[['year', 'noc', 'gdp_per_capita', 'population',
                  'log_gdp_per_capita', 'log_population']]
        .drop_duplicates(subset=['year', 'noc'])
    )
    return gdp_lookup

def complete_tied(tied, gdp_lookup):
    # Add host info and GDP/population data to the tied rows, so this function adds the remaining columns needed for analysis
    
    tied_completed = tied.copy()
 
    # Add host country for each year
    tied_completed['host_noc'] = tied_completed['year'].map(HOST_NOC)
 
    # Check if this relay country was the host that year
    tied_completed['is_host'] = (tied_completed['noc'] == tied_completed['host_noc']).astype(int)
 
    # Merge GDP and population from the worldbank data
    tied_completed = pd.merge(tied_completed, gdp_lookup, on=['year', 'noc'], how='left')
 
    print(f"\nTied rows completed: {len(tied_completed)}")
    print(f"Tied rows missing GDP (pre-1960 expected): "
          f"{tied_completed['gdp_per_capita'].isna().sum()}")
 
    return tied_completed
 
 
def combine_and_save(wb_clean, tied_completed):
    # Stack the cleaned worldbank rows and the completed tied rows, sort by year, and save to worldbank_final.csv.
    
    combined = pd.concat([wb_clean[KEEP_COLS], tied_completed[KEEP_COLS]], ignore_index=True)
 
    combined = combined.sort_values(['year', 'noc', 'medal']).reset_index(drop=True)
 
    # Sanity checks before saving
    print(f"\nFinal dataset: {len(combined)} rows")
    print(f"Years covered: {combined['year'].min()} to {combined['year'].max()}")
    print(f"Unique NOCs:   {combined['noc'].nunique()}")
    print(f"Null GDP rows: {combined['gdp_per_capita'].isna().sum()} "
          f"(pre-1960 Games have no World Bank data — expected)")
    print(f"is_host rows:  {combined['is_host'].sum()}")
 
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "clean"), exist_ok=True)
    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved: {OUTPUT_PATH}")
 
# Main function
 
def main():
    wb, tied = load_data()
    if wb is None:
        return
 
    wb_clean      = remove_placeholders(wb)
    gdp_lookup    = build_gdp_lookup(wb_clean)
    tied_completed = complete_tied(tied, gdp_lookup)
    combine_and_save(wb_clean, tied_completed)
 
 
if __name__ == "__main__":
    main()
 