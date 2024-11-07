import pandas as pd
import sqlite3

hour_df = pd.read_parquet(r"/workspaces/weather-scraper-analyzer/data/hourly_dataframe.gzip")
day_df = pd.read_parquet(r"/workspaces/weather-scraper-analyzer/data/daily_dataframe.gzip")

# store hour_df to .sql

# create the database
print("Creating SQLite connection...\nweather_data.db stored in the data directory.")
conn = sqlite3.connect(r"/workspaces/weather-scraper-analyzer/data/weather_data.db")

# now insert the pandas df to table using .to_sql

hour_df.to_sql("hourly_data", conn, if_exists='replace', index = False)
day_df.to_sql('daily_data', conn, if_exists = 'replace', index = False)

# commiting insertions
conn.commit()
print("hourly_data and daily_data tables have been successfully created and populated.")

conn.close()
print("SQLite connection closed.")

