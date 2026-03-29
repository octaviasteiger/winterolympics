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
    fig, ax = plt.subplots(figsize=(10,8 ))
    ax.barh(alltime['noc'], alltime['gold_medals'], color=GOLD, label='Gold', height=0.6)
    ax.barh(alltime['noc'], alltime['silver_medals'], color=SILVER, label='Silver', height=0.6,
            left=alltime['gold_medals'])
    ax.barh(alltime['noc'], alltime['bronze_medals'], color=BRONZE, label='Bronze', height=0.6, 
            left=alltime['gold_medals'] + alltime['silver_medals'])
    
    ax.invert_yaxis() # So that nation with most medals is at the top

    ax.set_title("All time Winter Olympics Medal table (Top 20 Nations)", fontsize=14)
    ax.set_xlabel("Total Medals won")
    ax.set_ylabel("Nation")
    ax.legend(loc='lower right')

    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, "fig1_alltime.png"))
    plt.close()
    print("Saved fig1_alltime.png")