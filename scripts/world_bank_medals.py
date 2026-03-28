"""fetch_worldbank.py
enriches the cleaned olympic medal data with the world bank indicators, using all medal types
This should provide more data for the analysis later on
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
RELAY_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'relay_noc.csv')


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
# adding in the relay function
# splitting the joined NOC codes into seperate NOCs
def parse_relay_noc(noc_string):
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
# Gold medals
    gold = medals[['year', 'event', 'gold_noc']].rename(columns={'gold_noc': 'noc'})
    gold['medal'] = 'gold'

# Silver medals
    silver = medals[['year', 'event', 'silver_noc']].rename(columns={'silver_noc': 'noc'})
    silver['medal'] = 'silver'
# Bronze medals
    bronze = medals[['year', 'event', 'bronze_noc']].rename(columns={'bronze_noc': 'noc'})
    bronze['medal'] = 'bronze'

# Combine all medals into one dataframe
    medals_long = pd.concat([gold, silver, bronze], ignore_index=True)

# Seperate the relay rows from the individual event rows
    relay_mask = (medals_long['noc'].str.len() > 3) | (medals_long['noc'].isin(['MIX', '-', '']))
    relay_rows = medals_long[relay_mask].copy() 
    medals_long = medals_long[~relay_mask].copy() 

# Parse relay rows into individual country entries and save seperately
    relay_expanded = []
    for _, row in relay_rows.iterrows():
        nocs = parse_relay_noc(row['noc'])
        for noc in nocs:
            if noc in NOC_TO_ISO:
                new_row = row.copy()
                new_row['noc'] = noc 
                new_row['iso_code'] = NOC_TO_ISO[noc]
                new_row['relay'] = True
                relay_expanded.append(new_row)

    relay_clean = pd.DataFrame(relay_expanded) if relay_expanded else pd.DataFrame()
    os.makedirs(os.path.join(PROJECT_ROOT, 'data', 'clean'), exist_ok=True)
    relay_clean.to_csv(RELAY_PATH, index=False)
    print(f"Relay medals saved: {len(relay_clean)} rows to relay_medals.csv")

# mapping NOC to ISO code for merging with worldbank data   
    medals_long['iso_code'] = medals_long['noc'].map(NOC_TO_ISO) 

# Merge with worldbank data
    final = pd.merge(medals_long, worldbank[['iso_code', 'year', 'gdp_per_capita', 'population']], on=['iso_code', 'year'], how='left', indicator=True)
# Check for merge quality, check for missing rows/ dropped rows
    print("\nMerge results:")
    print(final['_merge'].value_counts())

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