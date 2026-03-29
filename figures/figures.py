""" 
figures.py generates all the figures for my final report 

Run it after running analysis.py, as it needs the output from that script

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
FIGURES_DIR = os.path.join(PROJECT_ROOT, 'figures')

# Setting the style for all the plots, so that it is consistent across all of them 
sns.set_theme(style='whitegrid', font_scale=1.1) 
GOLD = "#FFD700"
SILVER = "#C0C0C0"
BRONZE = "#CD7F32"
BLUE = "#1f77b4"

# Function 1 - All time medals, horizontal bar chart 
def fig1_alltime(alltime):
    plt.figure()

    plt.barh(alltime['noc'], alltime['gold_medals'], label='Gold', color=GOLD)
    plt.barh(alltime['noc'], alltime['silver_medals'], left=alltime['gold_medals'], label='Silver', color=SILVER)
    plt.barh(alltime['noc'], alltime['bronze_medals'], left=alltime['gold_medals'] + alltime['silver_medals'], label='Bronze', color=BRONZE)

    plt.title("All time Olympic medals by Country")
    plt.xlabel("Total Medals")
    plt.legend()

    plt.savefig(os.path.join(FIGURES_DIR, 'fig1_alltime.png'))
    plt.close()

# Function 2 - Medals trends over time
def fig2_trends(cy):

    top6 = cy.groupby('noc')['total_medals'].sum().nlargest(6).index
    subset = cy[cy['noc'].isin(top6)]

    plt.figure()
    sns.lineplot(data=subset, x='year', y='total_medals', hue='noc')

    plt.title('Medals over time for top 6 countries')
    plt.xlabel('Year')
    plt.ylabel('Total Medals')

    plt.legend(title='Country')
    plt.savefig(os.path.join(FIGURES_DIR, 'fig2_trends.png'))
    plt.close()

# Function 3 - GDP vs medals
def fig3_gdp_medals(cy):
    plot_data = cy.dropna(subset=['log_gdp_per_capita', 'total_medals'])

    plt.figure()
    sns.regplot(data=plot_data, x='log_gdp_per_capita', y='total_medals')

    plt.title('GDP vs Medals')
    plt.xlabel('Log GDP per Capita')
    plt.ylabel('Total Medals')

    plt.savefig(os.path.join(FIGURES_DIR, 'fig3_gdp_medals.png'))
    plt.close()

# Function 4 - Host vs non-host, comparing a country medals when it was the host vs when it was not 
def fig4_host_compare(cy):

    # Flag which rows are host years
    hosts = cy[cy['is_host'] == 1][['noc', 'year','total_medals']].copy()
    hosts = hosts.rename(coloumns={'total_medals': "host_medals"})

    # For all the host nations, i get the average of their medals when they were not hosting
    non_host_avg = (cy[cy['is_host'] == 0].groupby('noc')['total_medals'].mean().reset_index().rename(columns={'total_medals': 'avg_non_host'}))

    compare = compare.merge(hosts, non_host_avg, on='noc', how='inner')
    compare = compare.sort_values('host_medals', ascending=False).head(15)

    # Reshaping the data for plotting
    long = compare.melt(id_vars=['noc'], value_vars=['host_medals', 'avg_non_host'], var_name='type', value_name='medals')
    long['type'] = long['type'].map({'host_medals': 'Host Year', 'avg_non_host': 'Avg Non-Host Year'})

    plt.figure()
    sns.barplot(data=long, x='noc', y='medals', hue='type')

    plt.title('Medals when Hosting vs Not Hosting')
    plt.xticks(rotation=45)

    plt.savefig(os.path.join(FIGURES_DIR, 'fig4_host_compare.png'))
    plt.close()

def main():
    alltime = pd.read_csv(ALLTIME_PATH)
    cy = pd.read_csv(COUNTRY_YEAR_PATH)

    fig1_alltime(alltime)
    fig2_trends(cy)
    fig3_gdp_medals(cy)
    fig4_host_compare(cy)

    print("Figures created")
    
if __name__ == "__main__":
    main()
