# Winter Olympics Medal Analysis

## Research Question
How have Winter Olympic medal distributions evolved across countries over time,
and do host countries experience a measurable performance advantage?

## Project Structure

```
winterolympics/
├── data/
│   ├── raw/               # Scraped data — gitignored, regenerate with scrape.py
│   └── clean/             # Cleaned data — committed to GitHub
├── scripts/
│   ├── scrape.py          # Scrapes medal tables from olympedia.org
│   └── clean.py           # Cleans raw data and saves to data/clean/
├── figures/               # Saved plots
├── outputs/               # Final outputs
├── requirements.txt
└── README.md
```

## How to Replicate

1. Clone the repository:
   ```
   git clone <https://github.com/octaviasteiger/winterolympics.git>
   cd winterolympics
   ```

2. Install:
   ```
   pip install -r requirements.txt
   ```

3. Scrape raw data (saves to data/raw/):
   ```
   python scripts/scrape.py
   ```

4. Clean the data (saves to data/clean/):
   ```
   python scripts/clean.py
   ```

## Data Sources
- Medal data scraped from [Olympedia](https://www.olympedia.org/editions/medal)
- Host country data: manually compiled
