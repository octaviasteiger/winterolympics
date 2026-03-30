"""
scrape.py
=================================================
Scrapes Winter Olympic medal tables from olympedia.org for every
edition from 1924 to 2022 and saves the raw data as a CSV.

Variables:
WINTER_EDITIONS: A dictionary mapping each Olympic year --> Olympedia edition ID
HEADERS: A dictionary of HTTP request headers to identify my script when making requests and avoids being blocked
SCRIPT_DIR: The directory where the script is located, helps to build file paths relative to the project root
PROJECT_ROOT: The parent directory of the script, and is used as the base directory for saving data
RAW_PATH: Full path to the output CSV file where the scraped data will be saved
year: The year of the Winter Olympics being scraped
all_rows: A list containing all scraped rows
seen_years: A list of years that were successfully scraped and parsed
edition_id: Olympedias edition ID
missing: list of any years that were not successfully scraped
raw_df: A pandas DataFrame which is a structured version of all_rows and is ready for saving to csv

Requirements:
    pip install requests beautifulsoup4 pandas
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# Each key is a year, each value is the Olympedia edition ID
# Found at olympedia.org/editions/medal
WINTER_EDITIONS = {
    1924: 29, 1928: 30, 1932: 31, 1936: 32,
    1948: 33, 1952: 34, 1956: 35, 1960: 36,
    1964: 37, 1968: 38, 1972: 39, 1976: 40,
    1980: 41, 1984: 42, 1988: 43, 1992: 44,
    1994: 45, 1998: 46, 2002: 47, 2006: 49,
    2010: 57, 2014: 58, 2018: 60, 2022: 62,
}

HEADERS = {"User-Agent": "BEE2041 Final Project - Winter Olympics Analysis"}

# __file__ is a built-in Python variable — it always holds the path to this script, this stops it from making the file within scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")

RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "medals_raw.csv")

# Functions

def download_page(url, year):
    """Download and return the HTML for a given URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        print(f"{year}: OK ({response.status_code})")
        return response.text
    except requests.RequestException as e:
        print(f"{year}: FAILED - {e}")
        return None


def parse_table(html, year):
    """Extract all rows from the first table found in the HTML."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")

    if not table:
        print(f"{year}: no table found")
        return []

    rows = []
    for tr in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in tr.find_all(["td", "th"])]
        rows.append([year] + cells)

    return rows


# Main function

def main():
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "raw"), exist_ok=True)

    all_rows = []
    seen_years = []

    for year, edition_id in sorted(WINTER_EDITIONS.items()):
        url = f"https://www.olympedia.org/editions/{edition_id}/medal"
        html = download_page(url, year)

        if html:
            rows = parse_table(html, year)
            if rows:
                all_rows.extend(rows)
                seen_years.append(year)

        time.sleep(10)

    print(f"\nScraped {len(seen_years)} of {len(WINTER_EDITIONS)} editions")
    print(f"Total rows: {len(all_rows)}")

    missing = sorted(set(WINTER_EDITIONS) - set(seen_years))
    if missing:
        print(f"Missing years: {missing}")

    # Save raw data to CSV
    raw_df = pd.DataFrame(all_rows)
    raw_df.to_csv(RAW_PATH, index=False, header=False)
    print(f"Saved: {RAW_PATH} ({len(raw_df)} rows)")

if __name__ == "__main__":
    main()
