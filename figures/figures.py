""" 
figures.py generates all the figures for my final report 

Run it after running analysis.py, as it needs the output from that script

Variables:
SCRIPT_DIR: The directory where the script is located, helps to build file paths relative to the
PROJECT_ROOT: The parent directory of the script, and is used as the base directory for saving data
COUNTRY_YEAR_PATH: The output path for aggregated country-year dataset, and it stores the regression
ALLTIME_PATH: The output path for all-time medal data, it is a summary table for top countries
REGRESSION_PATH: The output path for regression tables
FIGURES_DIR: The directory where the generated figures will be saved
alltime: the dataset containing the top 20 countries by total medal count, used for the all-time medal table figure
cy: the country-year level dataset, which is used for multiple figures including trends over time,GDP comparison and host analysis
reg: the regression results dataset, which contains the coefficients and statistics, used for regression visualisation
GOLD, SILVER, BRONZE, BLUE: Hex color codes for consistent styling of the figures across the report
top6: the list of the top 6 countries by total medal count, used to filter the dataset for the trends over time figure
subset: the filtered dataset containing only the top 6 countries, used for the trends over time
plot_data: the dataset used for the GDP vs medals scatter plot, which drops rows with missing data for the key variables
hosts: a dataset containing the medal counts for each country in the years they hosted, used for the host vs non-host comparison figure
non_host_avg: a dataset containing the average medal counts for each country in the years they did not host, used for the host vs non-host comparison figure
compare: a merged dataset combining the host and non-host medal counts, used for the host vs non-host comparison figure
long: a reshaped version of the compare dataset, which is in long format for easier plotting
key_vars: a list of the key variables of interest from the regression results, used to filter the regression dataset for visualisation
labels: a mapping of the variable names to more readable labels for the regression figure


Requirements: 
pip install pandas matplotlib seaborn

"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os

# Paths, the same as in my other scripts 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
COUNTRY_YEAR_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'medals_country_year.csv')
ALLTIME_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'alltime_table.csv') 
REGRESSION_PATH = os.path.join(PROJECT_ROOT, 'outputs', 'regression_results.csv')
WORLDBANK_PATH = os.path.join(PROJECT_ROOT, 'data', 'clean', 'worldbank_final.csv')
FIGURES_DIR = os.path.join(PROJECT_ROOT, 'figures')

# Setting the style for all the plots, so that it is consistent across all of them 
sns.set_theme(style='whitegrid', font_scale=1.1) 
GOLD = "#FFD700"
SILVER = "#C0C0C0"
BRONZE = "#CD7F32"
BLUE = "#1f77b4"

# Maping NOC to country names
NOC_NAMES = {
    'NOR': 'Norway',    'USA': 'United States', 'AUT': 'Austria',
    'GER': 'Germany',   'FIN': 'Finland',       'SWE': 'Sweden',
    'SUI': 'Switzerland','RUS': 'Russia',        'CAN': 'Canada',
    'ITA': 'Italy',     'FRA': 'France',         'NED': 'Netherlands',
    'GDR': 'East Germany','URS': 'Soviet Union', 'TCH': 'Czechoslovakia',
    'EUN': 'Unified Team','JPN': 'Japan',        'KOR': 'South Korea',
    'CZE': 'Czech Republic','POL': 'Poland',     'GBR': 'Great Britain',
    'BEL': 'Belgium',   'YUG': 'Yugoslavia',    'LIE': 'Liechtenstein',
}


# Function 1 - All time medals, horizontal bar chart 
def fig1_alltime(alltime):

# Drawing the three medals as stacked horizontal bars
    alltime['country'] = alltime['noc'].map(NOC_NAMES).fillna(alltime['noc'])
    fig, ax = plt.subplots(figsize=(12, 9))

    ax.barh(alltime['country'], alltime['gold_medals'], label='Gold', color=GOLD, height=0.6)
    ax.barh(alltime['country'], alltime['silver_medals'], label='Silver', color=SILVER, height=0.6, left=alltime['gold_medals'])
    ax.barh(alltime['country'], alltime['bronze_medals'], label='Bronze', color=BRONZE, height=0.6, left=alltime['gold_medals'] + alltime['silver_medals'])

# Inverting so that the nation with the most medals is at the top
    ax.invert_yaxis()
    
    ax.set_title("All time Winter Olympics Medal Table (top 20)", fontsize=14, pad=12)
    ax.set_xlabel("Total Medals Won", fontsize=12)
    ax.set_ylabel("Country", fontsize=12)
    ax.tick_params(axis='both', labelsize=10)
    ax.legend(loc='lower right')

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig1_alltime.png'))
    plt.close()
    print("Saved fig1_alltime.png")


# Function 2 - Medals trends over time, line chart
def fig2_trends(cy):

    top6 = (cy.groupby('noc')['total_medals'].sum().nlargest(6).index.tolist())
    # Filtering to just the top 6 countries, to make the plot clearer 
    subset = cy[cy['noc'].isin(top6)].copy()
    subset['country'] = subset['noc'].map(NOC_NAMES).fillna(subset['noc'])

    fig, ax = plt.subplots(figsize=(11, 6))

    # Plot one line per country, and hue by country for clarity
    sns.lineplot(data=subset, x='year', y='total_medals', hue='country', marker='o', ax=ax)

    ax.set_title('Winter Olympic Medal Count per Games (Top 6 Nations)', fontsize=14, pad=12)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Medals Won', fontsize=12)
    ax.tick_params(axis='both', labelsize=10)

    # Adding the legend outside of the plot so no overlapping with the lines
    ax.legend(title='Country', bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)

    # Labelling the years when the Games took place
    ax.set_xticks(sorted(cy['year'].unique()))
    ax.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig2_trends.png'))
    plt.close()
    print("Saved fig2_trends.png")

# Function 3 - GDP vs medals, scatter plot and the regression line shows the overall trend
def fig3_gdp_medals(cy):
    plot_data = cy.dropna(subset=['log_gdp_per_capita', 'total_medals'])

    fig, ax = plt.subplots(figsize=(10, 6))

    # Scatter plot with regression line
    sns.regplot(data=plot_data, x='log_gdp_per_capita', y='total_medals', scatter_kws={'alpha': 0.4, 's': 25, 'color': BLUE},
                line_kws={'color': 'red'}, ax=ax)
    
    ax.set_title("Wealthier Countries Win More Medals", fontsize=14, pad=12)
    ax.set_xlabel("Log GDP per Capita (current USD)", fontsize=12)
    ax.set_ylabel("Total Medals Won", fontsize=12)
    ax.tick_params(axis='both', labelsize=10)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig3_gdp_medals.png'))
    plt.close()
    print("Saved fig3_gdp_medals.png")

# Function 4 - Host vs non-host, comparing a country medals when it was the host vs when it was not 
def fig4_host_compare(cy):

    # Flag which rows are host years
    hosts = cy[cy['is_host'] == 1][['noc', 'year','total_medals']].copy()
    hosts = hosts.rename(columns={'total_medals': "host_medals"})

    # For all the host nations, i get the average of their medals when they were not hosting
    non_host_avg = (cy[cy['is_host'] == 0].groupby('noc')['total_medals'].mean().reset_index().rename(columns={'total_medals': 'avg_non_host'}))

    compare = pd.merge(hosts, non_host_avg, on='noc', how='inner')
    compare = compare.sort_values('host_medals', ascending=False).head(15)

    # Reshaping the data for plotting
    long = compare.melt(id_vars=['noc'], value_vars=['host_medals', 'avg_non_host'], var_name='type', value_name='medals')
    long['type'] = long['type'].map({'host_medals': 'Host Year', 'avg_non_host': 'Average Non-Host Year'})
    long['country'] = long['noc'].map(NOC_NAMES).fillna(long['noc'])

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=long, x='country', y='medals', hue='type', ax=ax)

    ax.set_title('Medals when Hosting vs Not Hosting (Top 15 Host Nations)', fontsize=14, pad=12)
    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Total Medals', fontsize=12)
    ax.tick_params(axis='both', labelsize=10)
    ax.legend(title='Year Type')
    ax.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig4_host_compare.png'))
    plt.close()
    print("Saved fig4_host_compare.png")

# Function 5 - Fallen powers
def fig5_fallen_powers(final):
    cy_all = (final.groupby(['year', 'noc'], as_index=False).agg(total_medals=('noc', 'count')))

# average medals per games in each era
    early = cy_all[cy_all['year'] <= 1980]
    modern = cy_all[cy_all['year'] >= 1994]
    early_avg = (early.groupby('noc')['total_medals'].mean().rename('early_avg').reset_index())
    modern_avg = (modern.groupby('noc')['total_medals'].mean().rename('modern_avg').reset_index())

    # Keep only countries that were top 10 in the early era, sort by biggest decline
    top_early = early_avg.nlargest(10, 'early_avg')['noc']
    compare = pd.merge(early_avg[early_avg['noc'].isin(top_early)], modern_avg, on='noc', how='left').fillna(0)
    compare['decline'] = compare['early_avg'] - compare['modern_avg']
    compare = compare.sort_values('decline', ascending=False)

    # reshape and then create bar graph
    long = compare.melt(id_vars=['noc'], value_vars =['early_avg', 'modern_avg'], var_name ='era', value_name='avg_medals')
    long['era'] = long['era'].map({'early_avg': 'Pre-1980 average', 'modern_avg': 'Post-1992 average'})
    long['country'] = long['noc'].map(NOC_NAMES).fillna(long['noc'])

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=long, x='country', y='avg_medals', hue='era', ax=ax)
    ax.set_title('Early Dominance vs Modern Performance\n(Top 10 Pre-1980 Nations)',fontsize=14, pad=12)
    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Average Medals per Games', fontsize=12)
    ax.tick_params(axis='both', labelsize=10)
    ax.legend(title='Era')
    ax.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig5_fallen_powers.png'))
    plt.close()
    print("Saved fig5_fallen_powers.png") 

# Function 6 - Regression
def fig6_regression(reg):

    # Filtering to just the key variables 
    key_vars = ['is_host', 'log_gdp_per_capita', 'log_population']
    reg = reg[reg['variable'].isin(key_vars)].copy()

    # Labeling the axis 
    labels = {'is_host': 'Host Country', 'log_gdp_per_capita': 'Log GDP per Capita', 'log_population': 'Log Population'}
    reg['variable'] = reg['variable'].map(labels)

    reg['ci_lower'] = reg['Coef.'] - reg['[0.025]']
    reg['ci_upper'] = reg['[0.0975]'] - reg['Coef.']
    xerr = [reg['ci_lower'].values, reg['ci_upper'].values]

    # Creating horizontal bar chart
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.barh(reg['variable'], reg['Coef.'], xerr=xerr, capsize=5, error_kw={'linewidth': 1.5, 'ecolor': 'black'}) 
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_title("What predicts Winter Olympic Success?", fontsize=14, pad=12)
    ax.set_xlabel("Regression Coefficient (extra medals per unit increase)", fontsize=12)
    ax.set_ylabel('')
    ax.tick_params(axis='both', labelsize=10)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig6_regression.png'))
    plt.close()
    print("Saved fig6_regression.png")


        

def main():
    alltime = pd.read_csv(ALLTIME_PATH)
    cy = pd.read_csv(COUNTRY_YEAR_PATH)
    reg = pd.read_csv(REGRESSION_PATH)
    final = pd.read_csv(WORLDBANK_PATH)

    fig1_alltime(alltime)
    fig2_trends(cy)
    fig3_gdp_medals(cy)
    fig4_host_compare(cy)
    fig5_fallen_powers(final)
    fig6_regression(reg)
    

    print("Figures created")

if __name__ == "__main__":
    main()
