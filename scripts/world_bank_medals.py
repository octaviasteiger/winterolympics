"""world_bank_medals.py
completes the cleaned olympic medal data with the world bank indicators, using all medal types
This should provide more data for the analysis later on

Variables:
SCRIPT_DIR: The directory where the script is located, helps to build file paths relative to the project root
PROJECT_ROOT: The parent directory of the script, and is used as the base directory for saving data
MEDALS_PATH: Path to cleaned medals dataset, used to load the medal data for merging with world bank indicators
WORLD_BANK_PATH: The output path for final merged dataset, used for saving the final complete data
TIED_PATH: The output path for processed tied medal data, it stores expanded tied medal rows seperately
NOC_TO_ISO: A dictionary mapping NOC codes to ISO country codes, used for merging with world bank data
HOST_NOC: A dictionary mapping Olympic years to the host country's NOC code, so I can identify host country for each Olympics
noc_string: Combined NOC string from tied medals, used to split into individual NOCs
gdp_raw: Raw GDP per capita data from world bank API
gdp: is a dataframe, it is cleaned GDP data in long format 
pop_raw: Raw population data
pop: cleaned population data in long format
worldbank: Combined GDP and population dataset
medals: The cleaned medals dataset loaded from medals_clean.csv
medals_long: The medals dataset reshaped from wide to long format
tied_mask: A boolean mask so i can indentify problem rows 
tied_rows: A subset of tied or invalid medal rows
medals_long: after filtering out the tied rows, this now contains onyl valid single-country medal rows
tied_clean: It is the expanded dataset where each tied country gets its own row

"""

import wbgapi as wb
import pandas as pd
import numpy as np
import os

# Project paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")

MEDALS_PATH = os.path.join(PROJECT_ROOT, "data", "clean", "medals_clean.csv")
WORLD_BANK_PATH = os.path.join(PROJECT_ROOT, "data", "clean", "worldbank.csv")
TIED_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'tied_noc.csv')


# The winter olympic years
YEARS = [
    1924, 1928, 1932, 1936, 1948, 1952, 1956, 1960,
    1964, 1968, 1972, 1976, 1980, 1984, 1988, 1992,
    1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022
] 

# NOC to ISO code mapping
NOC_TO_ISO = { 
    'USA': 'USA', 'GER': 'DEU', 'NOR': 'NOR', 'AUT': 'AUT',
    'CAN': 'CAN', 'FIN': 'FIN', 'SWE': 'SWE', 'SUI': 'CHE',
    'FRA': 'FRA', 'ITA': 'ITA', 'GBR': 'GBR', 'NED': 'NLD',
    'RUS': 'RUS', 'URS': 'RUS', 'EUA': 'DEU', 'GDR': 'DEU',
    'FRG': 'DEU', 'CZE': 'CZE', 'TCH': 'CZE', 'AUS': 'AUS',
    'JPN': 'JPN', 'KOR': 'KOR', 'CHN': 'CHN', 'BLR': 'BLR',
    'POL': 'POL', 'CRO': 'HRV', 'SLO': 'SVN', 'SVK': 'SVK',
    'LAT': 'LVA', 'EST': 'EST', 'LIE': 'LIE', 'BEL': 'BEL',
    'ESP': 'ESP', 'EUN': 'RUS', 'KAZ': 'KAZ', 'UKR': 'UKR',
    'UZB': 'UZB', 'BUL': 'BGR', 'ROC': 'RUS', 'HUN': 'HUN',
    'NZL': 'NZL', 'YUG': 'SRB', 'LUX': 'LUX', 'DEN': 'DNK',
    'ROU': 'ROU', 'PRK': 'PRK',
}
# Adding in host dictionary 
HOST_NOC = {
    1924: 'FRA', 1928: 'SUI', 1932: 'USA', 1936: 'GER',
    1948: 'SUI', 1952: 'NOR', 1956: 'ITA', 1960: 'USA',
    1964: 'AUT', 1968: 'FRA', 1972: 'JPN', 1976: 'AUT',
    1980: 'USA', 1984: 'YUG', 1988: 'CAN', 1992: 'FRA',
    1994: 'NOR', 1998: 'JPN', 2002: 'USA', 2006: 'ITA',
    2010: 'CAN', 2014: 'RUS', 2018: 'KOR', 2022: 'CHN'
}
# adding in the tied function
# splitting the joined NOC codes into seperate NOCs
def parse_tied_noc(noc_string):
    noc_string = str(noc_string).strip()
    if len(noc_string) % 3 != 0: # check if the string length can be divided by 3
        return []
    return list({noc_string[i : i+3] for i in range(0, len(noc_string), 3)}) # splits the string into 3 letter NOC codes and returns 


def main(): 
# Pulling the GDP per capita 
    gdp_raw = wb.data.DataFrame('NY.GDP.PCAP.CD', time=YEARS, labels=True)
    gdp = (gdp_raw.reset_index().melt(id_vars=['economy', 'Country'], var_name='year', value_name='gdp_per_capita'))
    gdp['year'] = gdp['year'].astype(str).str.replace('YR', '').astype(int)

# Pulling the population data
    pop_raw = wb.data.DataFrame('SP.POP.TOTL', time=YEARS, labels=True)
    pop = (pop_raw.reset_index().melt(id_vars=['economy', 'Country'], var_name='year', value_name='population'))
    pop['year'] = pop['year'].astype(str).str.replace('YR', '').astype(int)

# Merge GDP and population data
    worldbank = pd.merge(gdp, pop, on=['economy', 'Country', 'year'], how='outer')
    worldbank = worldbank.rename(columns={'economy': 'iso_code'}) 

# Load medals and check file exists
    if not os.path.exists(MEDALS_PATH):
        print(f"ERROR: medals_clean.csv not found at {MEDALS_PATH}")
        print("Run scripts/clean_medals.py first")
        return
    
# Adding in medals data
    medals = pd.read_csv(MEDALS_PATH)

# Reshaping the medals from wide to long format
    medals_long = pd.melt(medals[['year', 'event', 'gold_noc', 'silver_noc', 'bronze_noc']],
        id_vars=['year', 'event'],
        value_vars=['gold_noc', 'silver_noc', 'bronze_noc'],
        var_name='medal',
        value_name='noc')
    
    medals_long['medal'] = medals_long['medal'].str.replace('_noc', '') 

# Seperate the tied rows from the individual event rows
    tied_mask = (medals_long['noc'].str.len() > 3) | (medals_long['noc'].isin(['MIX', '-', '']))
    tied_rows = medals_long[tied_mask].copy() 
    medals_long = medals_long[~tied_mask].copy() 

# Expand the tied rows into one row per country u
    tied_rows['noc_list'] = tied_rows['noc'].apply(parse_tied_noc)
    tied_clean = tied_rows.explode('noc_list').copy()
    tied_clean = tied_clean.dropna(subset=['noc_list'])                         
    tied_clean = tied_clean.drop(columns=['noc']).rename(columns={'noc_list': 'noc'})
    tied_clean = tied_clean[tied_clean['noc'].isin(NOC_TO_ISO)].copy()        
    tied_clean['iso_code'] = tied_clean['noc'].map(NOC_TO_ISO)
    tied_clean['tied'] = True

    os.makedirs(os.path.join(PROJECT_ROOT, 'data', 'clean'), exist_ok=True)
    tied_clean.to_csv(TIED_PATH, index=False)
    print("Saved tied medals to tied_noc.csv")

# mapping NOC to ISO code for merging with worldbank data   
    medals_long['iso_code'] = medals_long['noc'].map(NOC_TO_ISO) 

# Merge with worldbank data
    final = pd.merge(medals_long, worldbank[['iso_code', 'year', 'gdp_per_capita', 'population']], on=['iso_code', 'year'], how='left', indicator=True)

# Add host country columns
    final['host_noc'] = final['year'].map(HOST_NOC)
    final['is_host'] = (final['noc'] == final['host_noc']).astype(int)

# Log any missing data, so instead of 0 it is NaN to avoid errors
    final['log_gdp_per_capita'] = np.log(final['gdp_per_capita'].replace(0, np.nan))
    final['log_population'] = np.log(final['population'].replace(0, np.nan))

# Drop the indicator column before saving
    final = final.drop(columns=['_merge'])

# Save the final merged dataset
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "clean"), exist_ok=True)
    final.to_csv(WORLD_BANK_PATH, index=False)

    print(f"\nSaved {len(final)} rows to {WORLD_BANK_PATH}")
    print(f"Missing GDP values: {final['gdp_per_capita'].isna().sum()}")
    print(f"Missing population values: {final['population'].isna().sum()}")
    print(f"Host year medal rows: {final['is_host'].sum()}")

if __name__ == "__main__":
    main()