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


YEARS = list(range(1924, 2024, 4))  # Winter Olympics years

# Pulling the GDP per capita 
gdp_raw = wb.data.DataFrame('NY.GDP.PCAP.CD', time=YEARS, labels=True)
gdp = (gdp_raw.reset_index().melt(id_vars=['economy', 'Country'], var_name='year', value_name='gdp_per_capita'))
gdp['year'] = gdp['year'].str.replace('YR', '').astype(int)

# Pulling the population data
pop_raw = wb.data.DataFrame('SP.POP.TOTL', time=YEARS, labels=True)
pop = (pop_raw.reset_index().melt(id_vars=['economy', 'Country'], var_name='year', value_name='population'))
pop['year'] = pop['year'].str.replace('YR', '').astype(int)

# Merge GDP and population data
worldbank = pd.merge(gdp, pop, on=['economy', 'Country', 'year'], how='outer')
worldbank = worldbank.rename(columns={'economy': 'iso_code'}) 

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

# NOC to ISO code mapping
noc_to_iso = { 
    'USA': 'USA', 'GER': 'DEU', 'NOR': 'NOR', 'AUT': 'AUT',
    'CAN': 'CAN', 'FIN': 'FIN', 'SWE': 'SWE', 'SUI': 'CHE',
    'FRA': 'FRA', 'ITA': 'ITA', 'GBR': 'GBR', 'NED': 'NLD',
    'RUS': 'RUS', 'URS': 'RUS', 'EUA': 'DEU', 'GDR': 'DEU',
    'FRG': 'DEU', 'CZE': 'CZE', 'TCH': 'CZE', 'AUS': 'AUS',
    'JPN': 'JPN', 'KOR': 'KOR', 'CHN': 'CHN', 'BLR': 'BLR',
    'POL': 'POL', 'CRO': 'HRV', 'SLO': 'SVN', 'SVK': 'SVK',
    'LAT': 'LVA', 'EST': 'EST', 'LIE': 'LIE', 'BEL': 'BEL',
}

# Map NOC to ISO code in medals data
medals_long['iso_code'] = medals_long['noc'].map(noc_to_iso)

#Check for any unmapped NOCs and log them, this will help identify any missing data or errors in the mapping
unmapped = medals_long[medals_long['iso_code'].isna()]['noc'].unique()
if len(unmapped) > 0:
    print(f"WARNING: unmapped NOCs codes: {unmapped}")

# Merge with worldbank data
final = pd.merge(medals_long, worldbank[['iso_code', 'year', 'gdp_per_capita', 'population']], 
                 on=['iso_code', 'year'], how='left', indicator=True)

# Check for merge quality, check for missing rows/ dropped rows
print("\nMerge results:")
print(final['_merge'].value_counts())

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
