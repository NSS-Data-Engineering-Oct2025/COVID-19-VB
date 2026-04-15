# import requests
# import pandas as pd

# API_URL_Vaccine = "https://data.cdc.gov/resource/unsk-b7fc.json?$limit=50000"

# # Fetch data
# response = requests.get(API_URL_Vaccine)
# response.raise_for_status()  # ensures request worked

# data = response.json()

# # Convert to DataFrame
# df = pd.DataFrame(data)

# # Show all columns
# print("Columns:", sorted(df.columns))
# print("Total columns:", len(df.columns))

# import pandas as pd
# import requests

# url = "https://data.cdc.gov/resource/unsk-b7fc.json?$limit=50000"
# data = requests.get(url).json()
# df = pd.DataFrame(data)

# # Total rows
# print("Total rows:", len(df))
# df['date'] = pd.to_datetime(df['date'])
# print("Earliest date:", df['date'].min())
# print("Latest date:", df['date'].max())

import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

def fetch_covid_data(url):
    all_data = []
    offset = 0
    limit = 10000
    while True:
        response = requests.get(url, params={"$offset": offset, "$limit": limit})
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        all_data.extend(data)
        offset += limit
    return pd.DataFrame(all_data)

def main():
    df = fetch_covid_data(API_URL)
    print("Columns:", df.columns)
    print("\nSample rows with start_date and end_date:")
    print(df[["start_date", "end_date"]].head(20))  # Check first 20 rows
    
    # Optional: count how many nulls are there
    null_counts = df[["start_date", "end_date"]].isna().sum()
    print("\nNull counts per column:")
    print(null_counts)

if __name__ == "__main__":
    main()