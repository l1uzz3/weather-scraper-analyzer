import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import sqlite3

def setup_api_client():
    """
    Set up the Open-Meteo API client with caching and retry.

    :return: Configured Open-Meteo API client.
    """
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)

def fetch_weather_data(client, url, params):
    """
    Fetch weather data from the Open-Meteo API.

    :param client: Configured Open-Meteo API client.
    :param url: URL endpoint for the weather data.
    :param params: Parameters to pass to the API call.
    :return: API response containing weather data.
    """
    return client.weather_api(url, params=params)

def process_hourly_data(response):
    """
    Process hourly data from the API response and return a DataFrame.

    :param response: API response object with hourly weather data.
    :return: DataFrame containing processed hourly weather data.
    """
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            periods=3,
            freq=pd.Timedelta(seconds=hourly.Interval())
        ),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
        "precipitation": hourly.Variables(2).ValuesAsNumpy(),
        "weather_code": hourly.Variables(3).ValuesAsNumpy(),
        "wind_speed_10m": hourly.Variables(4).ValuesAsNumpy(),
        "wind_direction_10m": hourly.Variables(5).ValuesAsNumpy(),
        "wind_gusts_10m": hourly.Variables(6).ValuesAsNumpy(),
    }
    return pd.DataFrame(data=hourly_data)

def process_daily_data(response):
    """
    Process daily data from the API response and return a DataFrame.

    :param response: API response object with daily weather data.
    :return: DataFrame containing processed daily weather data.
    """
    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            periods=3,
            freq=pd.Timedelta(seconds=daily.Interval())
        ),
        "weather_code": daily.Variables(0).ValuesAsNumpy(),
        "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
        "temperature_2m_min": daily.Variables(2).ValuesAsNumpy(),
        "temperature_2m_mean": daily.Variables(3).ValuesAsNumpy(),
        "precipitation_sum": daily.Variables(4).ValuesAsNumpy(),
        "wind_speed_10m_max": daily.Variables(5).ValuesAsNumpy(),
        "wind_gusts_10m_max": daily.Variables(6).ValuesAsNumpy(),
        "wind_direction_10m_dominant": daily.Variables(7).ValuesAsNumpy(),
    }
    return pd.DataFrame(data=daily_data)

def clean_dataframe(df):
    """
    Clean the DataFrame by dropping null values and renaming columns.

    :param df: DataFrame to clean.
    :return: Cleaned DataFrame with renamed columns.
    """
    df.dropna(inplace=True)
    df.rename(columns={
        'temperature_2m': 'temperature_2m_C',
        'relative_humidity_2m': 'relative_humidity_2m_percent',
        'precipitation': 'precipitation_mm',
        'wind_speed_10m': 'wind_speed_10m_kmh',
        'wind_direction_10m': 'wind_direction_10m_deg',
        'wind_gusts_10m': 'wind_gusts_10m_kmh'
    }, inplace=True)
    return df

def store_data_to_db(df, table_name, conn):
    """
    Store the DataFrame into the SQLite database.

    :param df: DataFrame to store.
    :param table_name: Name of the table in the database.
    :param conn: SQLite connection object.
    """
    df.to_sql(table_name, conn, if_exists='replace')

def main(): # pragma: no cover
    """
    *NOT INCLUDED INTO THE TEST COV* | Main function to execute the weather data fetching and processing.
    Sets up the API client, fetches data, processes it, cleans it, and stores it in a database.
    """
    openmeteo = setup_api_client()
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
    
    responses = fetch_weather_data(openmeteo, url, params)
    response = responses[0]
    
    hourly_df = process_hourly_data(response)
    daily_df = process_daily_data(response)

    hourly_df = clean_dataframe(hourly_df)
    daily_df = clean_dataframe(daily_df)

    conn = sqlite3.connect("/workspaces/weather-scraper-analyzer/data/weather_data.db")
    store_data_to_db(hourly_df, "hourly_data", conn)
    store_data_to_db(daily_df, "daily_data", conn)
    
    print("Data stored successfully!")

if __name__ == "__main__":
    main() # pragma: no cover
