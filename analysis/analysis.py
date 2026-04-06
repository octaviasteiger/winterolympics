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
medals_agg: The aggregated country-year level dataset, which is the core dataset used for the regression analysis
totals_per_year: A dataset containing the total number of medals awarded each year, so i can work out medal shares
alltime_table: A dataset containing the top 20 countries of all time by medal count, used for summary statistics and visualisations 
reg_data: The filtered dataset used in regression, and it drops rows with missing data for the key variables
model: The fitted OLS regression model 
results_df: The structured regression output
clean: a filtered version of the main dataset with rows containing missing data removed
medal_share: a calulated variable representing the share of total medals won by each country in a given year

"""

import pandas as pd
import statsmodels.formula.api as smf
import os


# Adding in the paths - these are the same as in my other scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
INPUT_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'worldbank_final.csv')
COUNTRY_YEAR_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'medals_country_year.csv')
ALLTIME_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'alltime_table.csv') 
REGRESSION_PATH = os.path.join(PROJECT_ROOT, 'outputs', 'regression_results.csv')
SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'outputs', 'summary_stats.csv')

def main():
    # Load the final merged dataset
    if not os.path.exists(INPUT_PATH):
        print(f"ERROR: worldbank_final.csv not found. Run merge_tied.py first.")
        return
    
    df = pd.read_csv(INPUT_PATH)
    
    # Drop rows missing economic data, then group to country-year level
    clean = df.dropna(subset=['log_gdp_per_capita', 'log_population'])
    medals_agg = clean.groupby(['year', 'noc', 'iso_code', 'is_host'], as_index=False).agg(
        log_gdp_per_capita=('log_gdp_per_capita', 'mean'), log_population=('log_population', 'mean'), 
        total_medals=('noc', 'count')).sort_values(['year', 'total_medals'], ascending=[True, False]).reset_index(drop=True)


    # Total medals awarded per year so that I can calulcate the medal share
    totals_per_year = (df.groupby('year', as_index=False).agg(medals_awarded=('noc', 'count')))

    # The all time medal table, but only looking at the top 20 nations so that it is more readable
    alltime_table = (df.assign(gold_medals=df['medal'].eq('gold').astype(int),
                               silver_medals=df['medal'].eq('silver').astype(int),
                                 bronze_medals=df['medal'].eq('bronze').astype(int),).groupby(['noc', 'iso_code'], 
                                                                                            as_index=False).agg(total_medals=('medal', 'count'), 
                                                                                            gold_medals=('gold_medals', 'sum'), 
                                                                                            silver_medals=('silver_medals', 'sum'), 
                                                                                            bronze_medals=('bronze_medals', 'sum'), 
                                                                                            games_participated=('year', 'nunique')).sort_values('total_medals', ascending=False).head(20).reset_index(drop=True))

    # Medal share
    medals_agg = pd.merge(medals_agg, totals_per_year, on='year', how='left')
    medals_agg['medal_share'] = medals_agg['total_medals'] / medals_agg['medals_awarded']

    # Summary statistics table
    summary = (medals_agg.groupby('noc')['total_medals'].agg(['mean', 'sum', 'count']).round(1)
               .rename(columns={'mean': 'Avg Medals/games', 'sum': 'Total medals', 'count': 'Games Attended'})
               .sort_values('Total medals', ascending=False).head(15))
    
    #Regression
    reg_data = medals_agg.dropna(subset=['log_gdp_per_capita', 'log_population']).copy()

    # Model 1: basic OLS 
    model_basic = smf.ols('total_medals ~ is_host + log_gdp_per_capita + log_population', data=reg_data).fit()
    print(model_basic.summary())

    # Model 2: same but with dummy for each country
    model_fe = smf.ols('total_medals ~ is_host + log_gdp_per_capita + log_population + C(noc)', data=reg_data).fit()
    print(model_fe.summary())

    # The three variables I need from each model
    keep = ['is_host', 'log_gdp_per_capita', 'log_population']

    # Extract and rename the key columns from basic
    basic_coefs = model_basic.summary2().tables[1].reset_index()
    basic_coefs = basic_coefs.rename(columns={'index': 'variable', 'Coef.': 'OLS_coef', 'P>|t|': 'OLS_pval'})
    basic_coefs = basic_coefs[basic_coefs['variable'].isin(keep)][['variable', 'OLS_coef', 'OLS_pval']]

    # Extract and rename the key columns from fixed effects
    fe_coefs = model_fe.summary2().tables[1].reset_index()
    fe_coefs = fe_coefs.rename(columns={'index': 'variable', 'Coef.': 'FE_coef', 'P>|t|': 'FE_pval'})
    fe_coefs = fe_coefs[fe_coefs['variable'].isin(keep)][['variable', 'FE_coef', 'FE_pval']]

    # Merge the two sets of coefficients into one comparison table
    comparison = pd.merge(basic_coefs, fe_coefs, on='variable').round(3)

    # Add significance stars to each model based on the p-value
    comparison['OLS_stars'] = comparison['OLS_pval'].apply(lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else '')))
    comparison['FE_stars'] = comparison['FE_pval'].apply(lambda p: '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else '')))
    print(comparison)

    # Save the basic OLS coefficients for current figures
    results_df = model_basic.summary2().tables[1].reset_index()
    results_df = results_df.rename(columns={'index': 'variable'})
    
    # Save the outputs
    os.makedirs(os.path.join(PROJECT_ROOT, 'data', 'clean'), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_ROOT, 'outputs'), exist_ok=True)
    
    medals_agg.to_csv(COUNTRY_YEAR_PATH, index=False)
    alltime_table.to_csv(ALLTIME_PATH,   index=False)
    results_df.to_csv(REGRESSION_PATH, index=False)
    summary.to_csv(SUMMARY_PATH)
    comparison.to_csv(os.path.join(PROJECT_ROOT, 'outputs', 'model_comparison.csv'), index=False)
    print("Saved outputs. Run figures.py to generate the figures.")

if __name__ == "__main__":
    main()
