"""pip install statsmodels
and add it to the requirements files

analysis.py 
Aggregates the completed medal data and runs an OLS regression to test whether host countries experience a 
measurable performance advantage at the Winter Olympics. 

Variables:
SCRIPT_DIR: The directory where the script is located, helps to build file paths relative to the project root
PROJECT_ROOT: The parent directory of the script, and is used as the base directory for saving data
INPUT_PATH: The path to the final cleaned dataset, which is the main input for the analysis
COUNTRY_YEAR_PATH: The output path for aggregated country-year dataset, and it stores the regression ready data
ALLTIME_PATH: The output path for all-time medal data, it is a summary table for top countries
REGRESSION_PATH: The output path for regression tables
df: The final merged dataset
medals_raw; SQL table name, temporary table created from df and is used for SQL queries
medals_agg: The aggregated country-year level dataset, which is the core dataset used for the regression analysis
totals_per_year: A dataset containing the total number of medals awarded each year, so i can work out medal shares
alltime_table: A dataset containing the top 20 countries of all time by medal count, used for summary statistics and visualisations 
reg_data: The filtered dataset used in regression, and it drops rows with missing data for the key variables
model: The fitted OLS regression model 
medals_lag1: The lagged medal count variable, which controls for past performance
key_vars: The list of key variables of interest
results_df: The structured regression output

"""

import pandas as pd
import numpy as np
import sqlite3
import statsmodels.formula.api as smf
import os


# Adding in the paths - these are the same as in my other scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
INPUT_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'worldbank_final.csv')
COUNTRY_YEAR_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'medals_country_year.csv')
ALLTIME_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'alltime_table.csv') 
REGRESSION_PATH = os.path.join(PROJECT_ROOT, 'outputs', 'regression_results.csv')
def main():
    # Load the final merged dataset
    if not os.path.exists(INPUT_PATH):
        print(f"ERROR: worldbank_final.csv not found. Run merge_tied.py first.")
        return
    
    df = pd.read_csv(INPUT_PATH)
    # SQL aggregation to country-year level
    conn = sqlite3.connect(':memory:')
    df.to_sql('medals_raw', conn, index=False, if_exists='replace')
    # One row per country per Games but only where GDP data exists
    medals_agg = pd.read_sql_query("""
         SELECT
            year, noc, iso_code, host_noc, is_host,
            AVG(log_gdp_per_capita) AS log_gdp_per_capita,
            AVG(log_population)     AS log_population,
            COUNT(*)                AS total_medals
        
        FROM medals_raw
        WHERE log_gdp_per_capita IS NOT NULL
          AND log_population     IS NOT NULL
        GROUP BY year, noc, iso_code, host_noc, is_host
        ORDER BY year ASC, total_medals DESC
    """, conn)
    # Total medals awarded per year so that I can calulcate the medal share
    totals_per_year = pd.read_sql_query("""
        SELECT year, COUNT(*) AS medals_awarded
        FROM medals_raw
        GROUP BY year
    """, conn)
    # The all time medal table, but only looking at the top 20 nations so that it is more readable
    alltime_table = pd.read_sql_query("""
        SELECT
            noc, iso_code,
            COUNT(*)                                           AS total_medals,
            SUM(CASE WHEN medal = 'gold' THEN 1 ELSE 0 END)    AS gold_medals,
            SUM(CASE WHEN medal = 'silver' THEN 1 ELSE 0 END)  AS silver_medals,
            SUM(CASE WHEN medal = 'bronze' THEN 1 ELSE 0 END)  AS bronze_medals,
            COUNT(DISTINCT year)                               AS games_participated
        FROM medals_raw
        GROUP BY noc, iso_code
        ORDER BY total_medals DESC
        LIMIT 20
    """, conn)
    conn.close()
    print(f"Aggregated to {len(medals_agg)} country-year rows")
    # Medal share
    medals_agg = pd.merge(medals_agg, totals_per_year, on='year', how='left')
    medals_agg['medal_share'] = medals_agg['total_medals'] / medals_agg['medals_awarded']
    # Lagged medal count to control for past performance
    medals_agg = medals_agg.sort_values(['noc', 'year']).reset_index(drop=True)
    medals_agg['medals_lag1'] = medals_agg.groupby('noc')['total_medals'].shift(1)
    #OLS regression to test for host advantage
    reg_data = medals_agg.dropna(subset=['log_gdp_per_capita', 'log_population', 'medals_lag1']).copy()
    model = smf.ols('total_medals ~ is_host + log_gdp_per_capita + log_population + medals_lag1 + C(year)', data=reg_data).fit()
    print(model.summary())
    # Save the four key coefficients for the figures 
    key_vars = ['is_host', 'log_gdp_per_capita', 'log_population', 'medals_lag1']
    results_df = pd.concat([
        model.params[key_vars].rename('coefficient'),
        model.bse[key_vars].rename('std_error'),
        model.pvalues[key_vars].rename('p_value'),
        model.conf_int().loc[key_vars].rename(columns={0: 'ci_lower', 1: 'ci_upper'})], axis=1).reset_index(names='variable')
    
    # Save the outputs
    os.makedirs(os.path.join(PROJECT_ROOT, 'data', 'clean'), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, 'outputs'), exist_ok=True)
    medals_agg.to_csv(COUNTRY_YEAR_PATH, index=False)
    alltime_table.to_csv(ALLTIME_PATH,   index=False)
    results_df.to_csv(REGRESSION_PATH, index=False)
    print("Saved outputs. Run figures.py to generate the figures.")

if __name__ == "__main__":
    main()
