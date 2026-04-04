# Makefile for Winter Olympics Medal Analysis

# Python interpretrer 
PYTHON = python3

# Main output
all: report/report.html 

# Step 1: Scrape data
data/raw/medals_raw.csv : scripts/scrape.py 
	$(PYTHON) scripts/scrape.py 

# Step 2: Clean data
data/clean/medals_clean.csv : scripts/clean.py data/raw/medals_raw.csv 
	$(PYTHON) scripts/clean.py 

# Step 3: Get World bank data
data/clean/worldbank.csv data/clean/tied_noc.csv : scripts/world_bank_medals.py data/clean/medals_clean.csv
	$(PYTHON) scripts/world_bank_medals.py

# Step 4: Merge datasets
data/clean/worldbank_final.csv: scripts/merge_tied.py data/clean/worldbank.csv data/clean/tied_noc.csv
	$(PYTHON) scripts/merge_tied.py

# Step 5: Analysis
data/clean/medals_country_year.csv data/clean/alltime_table.csv outputs/regression_results.csv: analysis/analysis.py data/clean/worldbank_final.csv
	$(PYTHON) analysis/analysis.py

# Step 6: Figures
figures/fig1_alltime.png figures/fig2_trends.png figures/fig3_gdp_medals.png figures/fig4_host_compare.png figures/fig5_regression.png figures/fig6_fallen_powers.png: figures/figures.py data/clean/medals_country_year.csv data/clean/alltime_table.csv data/clean/worldbank_final.csv outputs/regression_results.csv
	$(PYTHON) figures/figures.py

# Step 7: Report
report/report.html: report/report.qmd figures/fig1_alltime.png figures/fig2_trends.png figures/fig3_gdp_medals.png figures/fig4_host_compare.png figures/fig5_regression.png figures/fig6_fallen_powers.png data/clean/medals_country_year.csv outputs/regression_results.csv
	quarto render report/report.qmd

# Clean outputs
clean:
	rm -f data/raw/medals_raw.csv
	rm -f data/clean/*.csv
	rm -f outputs/*.csv
	rm -f figures/*.png
	rm -f report/report.html

