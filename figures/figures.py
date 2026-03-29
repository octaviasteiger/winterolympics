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

