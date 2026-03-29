# Winter Olympics Medal Analysis

## Research Question
How have Winter Olympic medal distributions evolved across countries over time,
and do host countries experience a measurable performance advantage?

## Data Sources
Olympedia (https://www.olympedia.org) - Every medal, event and country code for all 24 Winter Olympic Games was scraped using Python
World Bank API (https://data.worldbank.org) - GDP per Capita and population by country and year which was downloaded using wbgapi

## Project Structure

``` 
winterolympics/
├── analysis/
|   ├── analysis.py/             # Analysis of data - SQL aggregation and OLS regression
├── data/
│   ├── clean/                   # Cleaned data — committed to GitHub
|   └── alltime_table.csv        #
|   └── medals_clean.csv         #
|   └── medals_country_year.csv  #
|   └── tied_noc.csv             #
|   └── worldbank.csv            #
|   └── worldbank_final.csv      # 
│   ├── raw/                     # Scraped data — gitignored, regenerate with scrape.py
├── figures/                     # Saved plots
|   └── fig1_alltime.png         #
|   └── fig2_trends.png          #
|   └── fig3_gdp_medals.png      #
|   └── fig4_host_compare.png    #
|   ├── figures.py/              # Output PNG plots
├── outputs/                     # Final outputs
|   └── regression_results.csv   #
├── scripts/
│   ├── clean.py                 # Cleans raw data and saves to data/clean/
│   ├── merge_tied.py            # reintergrating tied medals
│   ├── scrape.py                # Scrapes medal tables from olympedia.org
|   └── world_bank_medals.py     # Adds world bank data onto the medals data
├── README.md
└── requirements.txt
```

## How to Replicate

1. Clone the repository:
   ```
   git clone https://github.com/octaviasteiger/winterolympics.git
   cd winterolympics
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the scripts in order: 
   ```
   python scripts/scrape.py
   ```

4. Clean the raw data
   ```
   python scripts/clean.py
   ```

5. Download World Bank data and merge
   ```
   python scripts/world_bank_medals
   ```

6. Re-integrate tied medal rows
   ```
   python scripts/merge_tied.py
   ```

7. Run SQL aggregation and OLS regression
   ```
   python analysis/analysis.py
   ```

8. Generate all figures
   ```
   python figures/figures.py
   ```
