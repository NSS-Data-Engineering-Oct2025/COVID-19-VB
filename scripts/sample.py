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

import pandas as pd
import requests

url = "https://data.cdc.gov/resource/unsk-b7fc.json?$limit=50000"
data = requests.get(url).json()
df = pd.DataFrame(data)

# Total rows
print("Total rows:", len(df))
df['date'] = pd.to_datetime(df['date'])
print("Earliest date:", df['date'].min())
print("Latest date:", df['date'].max())