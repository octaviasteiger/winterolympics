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
    fig, ax = plt.subplots(figsize=(10, 8))

# Drawing the three medals as stacked horizontal bars
    ax.barh(alltime['noc'], alltime['gold_medals'], label='Gold', color=GOLD, height=0.6)
    ax.barh(alltime['noc'], alltime['silver_medals'], label='Silver', color=SILVER, height=0.6, left=alltime['gold_medals'])
    ax.barh(alltime['noc'], alltime['bronze_medals'], label='Bronze', color=BRONZE, height=0.6, left=alltime['gold_medals'] + alltime['silver_medals'])

# Inverting so that the nation with the most medals is at the top
    ax.invert_yaxis()
    
    ax.set_title("All time Winter Olympics Medal Table (top 20)", fontsize=14, pad=12)
    ax.set_xlabel("Total Medals Won")
    ax.set_ylabel("Country")
    ax.legend(loc='lower right')

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig1_alltime.png'))
    plt.close()
    print("Saved fig1_alltime.png")

# Function 2 - Medals trends over time, line chart
def fig2_trends(cy):

    top6 = (cy.groupby('noc')['total_medals'].sum().nlargest(6).index.tolist())
    # Filtering to just the top 6 countries, to make the plot clearer 
    subset = cy[cy['noc'].isin(top6)]

    fig, ax = plt.subplots(figsize=(11, 6))

    # Plot one line per country, and hue by country for clarity
    sns.lineplot(data=subset, x='year', y='total_medals', hue='noc', marker='o', ax=ax)

    ax.set_title('Winter Olympic Medal Count per Games (Top 6 Nations)', fontsize=14, pad=12)
    ax.set_xlabel('Year')
    ax.set_ylabel('Medals Won')

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
    ax.set_xlabel("Log GDP per Capita")
    ax.set_ylabel("Total Medals Won")

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

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=long, x='noc', y='medals', hue='type', ax=ax)

    ax.set_title('Medals when Hosting vs Not Hosting (Top 15 Host Nations)', fontsize=14, pad=12)
    ax.set_xlabel('Country')
    ax.set_ylabel('Total Medals')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig4_host_compare.png'))
    plt.close()
    print("Saved fig4_host_compare.png")

# Function 5 - Regression coefficients
def fig5_regression(reg):

    # Filtering to just the key variables 
    key_vars = ['is_host', 'log_gdp_per_capita', 'log_population']
    reg = reg[reg['variable'].isin(key_vars)].copy()

    # Labeling the axis 
    labels = {'is_host': 'Host Country', 'log_gdp_per_capita': 'Log GDP per Capita', 'log_population': 'Log Population'}
    reg['variable'] = reg['variable'].map(labels)

    # Creating horizontal bar chart
    plt.figure(figsize=(9, 4))
    plt.barh(reg['variable'], reg['Coef.'])
    
    # Dashed line at zero as bars crossing this are not statistically significant
    plt.axvline(0)

    plt.title("What predicts Winter Olympic Success?", fontsize=14, pad=12)
    plt.xlabel("Regression Coefficient (extra medals per unit increase)")
    plt.ylabel('')

    plt.savefig(os.path.join(FIGURES_DIR, 'fig5_regression.png'))
    plt.close()
    print("Saved fig5_regression.png")


def main():
    alltime = pd.read_csv(ALLTIME_PATH)
    cy = pd.read_csv(COUNTRY_YEAR_PATH)
    reg = pd.read_csv(REGRESSION_PATH)

    fig1_alltime(alltime)
    fig2_trends(cy)
    fig3_gdp_medals(cy)
    fig4_host_compare(cy)
    fig5_regression(reg)

    print("Figures created")

if __name__ == "__main__":
    main()
