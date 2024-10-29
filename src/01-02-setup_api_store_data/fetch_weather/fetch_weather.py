import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": 45.7537,
	"longitude": 21.2257,
	"start_date": "2000-01-01",
	"end_date": "2024-10-27",
	"hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "weather_code", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
	"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"],
	"timezone": "GMT"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(3).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(5).ValuesAsNumpy()
hourly_wind_gusts_10m = hourly.Variables(6).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["precipitation"] = hourly_precipitation
hourly_data["weather_code"] = hourly_weather_code
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m

hourly_df = pd.DataFrame(data = hourly_data)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
daily_temperature_2m_mean = daily.Variables(3).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(4).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(5).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(6).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(7).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}
daily_data["weather_code"] = daily_weather_code
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant

daily_df = pd.DataFrame(data = daily_data)


# print df shapes
print("""
      .
      .
      .
""")
print(f"Hourly dataframe shape: {hourly_df.shape}. Null values: \n{hourly_df.isna().sum()}\nDaily dataframe shape: {daily_df.shape}. Null values: \n{daily_df.isna().sum()}")
print("""
      .
      .
      .
""")
print("Cleaning dataframes...")
hourly_df.dropna(inplace=True)
print("hourly_dataframe cleaned.")
print(f"Null values: {hourly_df.isna().sum()}")

daily_df.dropna(inplace=True)
print("daily_dataframe cleaned.")
print(f"Null values: {daily_df.isna().sum()}")

# modifying with .rename using the dictionary method.

hourly_df.rename(columns={
    'temperature_2m': 'temperature_2m_C', # celsius
    'relative_humidity_2m': 'relative_humidity_2m_percent', # percent
    'precipitation': 'precipitation_mm', # milimeters
    'wind_speed_10m': 'wind_speed_10m_kmh', # km/h
    'wind_direction_10m': 'wind_direction_10m_deg', # degrees
    'wind_gusts_10m': 'wind_gusts_10m_kmh' # km/h
}, inplace=True)

daily_df.rename(columns={
    'temperature_2m_max': 'temperature_2m_max_C', 
    'temperature_2m_min': 'temperature_2m_min_C',
    'temperature_2m_mean': 'temperature_2m_mean_C',
    'precipitation_sum': 'precipitation_sum_mm',
    'wind_speed_10m_max': 'wind_speed_10m_max_kmh',
    'wind_gusts_10m_max': 'wind_gusts_10m_max_kmh',
    'wind_direction_10m_dominant': 'wind_direction_10m_dominant_deg'
}, inplace=True)

# converting date from object to datetime without the unnecessary timezone info at the end 

hourly_df['date'] = pd.to_datetime(hourly_df['date']).dt.tz_localize(None)
daily_df['date'] = pd.to_datetime(daily_df['date']).dt.tz_localize(None)
print("Successfully converted date times without timezone information at the end:")
print(hourly_df['date'].dtypes)
print(daily_df['date'].dtypes)

# store the data into SQLite db
import sqlite3

conn = sqlite3.connect("/workspaces/weather-scraper-analyzer/data/weather_data.db")

hourly_df.to_sql("hourly_data", conn, if_exists='replace')
daily_df.to_sql("daily_data", conn, if_exists='replace')
# c = conn.cursor()
# c.execute("DROP TABLE daily_dataframe;")
print("Done")



print(hourly_df.columns)
print(daily_df.columns)