# Winter Olympics Medal Analysis

## Research Question
What drive medal success in the Winter Olympics? This project tests three factors: national wealth (GDP per capita), population size and whether hosting the Games gives a country a measurable advantage. An OLS regression is used to estimate each effect independently, alongside visualisation of historical trends and era comparisons.

## Data Sources
Olympedia (https://www.olympedia.org) - Every medal, event and country code for all 24 Winter Olympic Games was scraped using Python
World Bank API (https://data.worldbank.org) - GDP per Capita and population by country and year which was downloaded using wbgapi

## Project Structure

``` 
winterolympics/
├── analysis/
|   ├── analysis.py/                   # Aggregates data to country-year level and runs OLS regression
├── data/
│   ├── clean/                         # Cleaned data — committed to GitHub
│   │   ├── alltime_table.csv          # All-time medal totals by country
│   │   ├── medals_clean.csv           # Cleaned raw medal data
│   │   ├── medals_country_year.csv    # Aggregated country-year dataset for regression
│   │   ├── tied_noc.csv               # Seperated tied medal rows
│   │   ├── worldbank.csv              # Medals merged with World Bank indicators
│   │   ├── worldbank_final.csv        # Final merged dataset including tied medals
│   └── raw/                           # Scraped data — gitignored, regenerate with scrape.py
├── figures/                     
│   ├── figures.py                     # Generates all output PNG figures
│   ├── fig1_alltime.png               # All-time medal table (top 20)
│   ├── fig2_trends.png                # Medal trends over time (top 6 nations)
│   ├── fig3_gdp_medals.png            # GDP per capita vs medals scatter plot
│   ├── fig4_host_compare.png          # Host year vs non-host year comparison
│   ├── fig5_regression.png            # Regression coefficient plot
│   └── fig6_fallen_powers.png         # Early era dominance vs modern performance
├── outputs/                           
|   └── regression_results.csv         # OLS regression coefficients and statistics
├── report/
│   ├── blog.qmd                       # Quarto report source file
│   ├── blog.html                      # Rendered HTML report
│   └── blog_files/                    
├── scripts/
│   ├── clean.py                       # Cleans raw scraped data
│   ├── merge_tied.py                  # Reintegrates tied medal rows with economic data
│   ├── scrape.py                      # Scrapes medal tables from olympedia.org
|   └── world_bank_medals.py           # Fetches World Bank data and merges with medals
├── Makefile                           # Automates the full pipeline
├── README.md
└── requirements.txt
```

## How to Replicate
### Using Make
1. Install Quarto: https://quarto.org/docs/get-started/
   
2. Clone the repository:
   ```
   git clone https://github.com/octaviasteiger/winterolympics.git
   cd winterolympics
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the full pipeline:
   ```
   make
   ```
   This runs every step in order automatically: scrape --> clean --> fetch World Bank data --> merge --> analyse --> generate figures --> render report
