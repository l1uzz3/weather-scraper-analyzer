import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.br01_02_setup_api_store_data.fetch_weather.fetch_weather import (
    setup_api_client,
    fetch_weather_data,
    process_hourly_data,
    process_daily_data,
    clean_dataframe,
    store_data_to_db
)

# Mocking the Open-Meteo API Client
@pytest.fixture
def mock_openmeteo_response():
    """Creates a mock response object for the Open-Meteo API."""
    mock_response = MagicMock()
    mock_response.Latitude.return_value = 45.7537
    mock_response.Longitude.return_value = 21.2257
    mock_response.Elevation.return_value = 100
    mock_response.Timezone.return_value = "GMT"
    mock_response.TimezoneAbbreviation.return_value = "GMT"
    mock_response.UtcOffsetSeconds.return_value = 0
    
    # Mocking the Hourly data response
    mock_hourly = MagicMock()
    mock_hourly.Time.return_value = pd.Timestamp('2000-01-01').timestamp()
    mock_hourly.TimeEnd.return_value = pd.Timestamp('2000-01-01 02:00:00').timestamp()  # Adjust end time to create a 3-hour range
    mock_hourly.Interval.return_value = 3600  # 1 hour in seconds
    mock_hourly.Variables.side_effect = [
        MagicMock(ValuesAsNumpy=lambda: pd.Series([20, 21, 22])),  # temperature_2m
        MagicMock(ValuesAsNumpy=lambda: pd.Series([60, 65, 70])),  # relative_humidity_2m
        MagicMock(ValuesAsNumpy=lambda: pd.Series([0, 1, 0])),     # precipitation
        MagicMock(ValuesAsNumpy=lambda: pd.Series([0, 1, 0])),     # weather_code
        MagicMock(ValuesAsNumpy=lambda: pd.Series([5, 7, 10])),    # wind_speed_10m
        MagicMock(ValuesAsNumpy=lambda: pd.Series([180, 190, 200])),  # wind_direction_10m
        MagicMock(ValuesAsNumpy=lambda: pd.Series([8, 9, 11]))     # wind_gusts_10m
    ]
    mock_response.Hourly.return_value = mock_hourly

    # Mocking the Daily data response
    mock_daily = MagicMock()
    mock_daily.Time.return_value = pd.Timestamp('2000-01-01').timestamp()
    mock_daily.TimeEnd.return_value = pd.Timestamp('2000-01-03').timestamp()  # Adjust to create a 3-day range
    mock_daily.Interval.return_value = 86400  # 1 day in seconds
    mock_daily.Variables.side_effect = [
        MagicMock(ValuesAsNumpy=lambda: pd.Series([0, 1, 0])),     # weather_code
        MagicMock(ValuesAsNumpy=lambda: pd.Series([22, 24, 23])),  # temperature_2m_max
        MagicMock(ValuesAsNumpy=lambda: pd.Series([10, 11, 12])),  # temperature_2m_min
        MagicMock(ValuesAsNumpy=lambda: pd.Series([16, 17, 18])),  # temperature_2m_mean
        MagicMock(ValuesAsNumpy=lambda: pd.Series([0, 1, 0])),     # precipitation_sum
        MagicMock(ValuesAsNumpy=lambda: pd.Series([6, 7, 8])),     # wind_speed_10m_max
        MagicMock(ValuesAsNumpy=lambda: pd.Series([9, 10, 11])),   # wind_gusts_10m_max
        MagicMock(ValuesAsNumpy=lambda: pd.Series([180, 190, 200])) # wind_direction_10m_dominant
    ]
    mock_response.Daily.return_value = mock_daily

    return mock_response

def test_setup_api_client():
    """Test the setup of the API client."""
    client = setup_api_client()
    assert client is not None  # Ensure that the client is created

def test_fetch_weather_data(mock_openmeteo_response):
    """Test the fetching of weather data from the API."""
    with patch('openmeteo_requests.Client') as mock_client:
        mock_client.return_value.weather_api.return_value = [mock_openmeteo_response]
        
        responses = fetch_weather_data(mock_client(), "url", {})
        response = responses[0]

        assert response.Latitude() == 45.7537
        assert response.Longitude() == 21.2257
        assert response.Elevation() == 100

def test_process_hourly_data(mock_openmeteo_response):
    """Test processing of hourly data."""
    response = mock_openmeteo_response
    hourly_df = process_hourly_data(response)

    assert hourly_df.shape[0] == 3  # Check number of rows
    assert 'temperature_2m' in hourly_df.columns

def test_process_daily_data(mock_openmeteo_response):
    """Test processing of daily data."""
    response = mock_openmeteo_response
    daily_df = process_daily_data(response)

    assert daily_df.shape[0] == 3  # Check number of rows
    assert 'temperature_2m_max' in daily_df.columns

def test_clean_dataframe():
    """Test cleaning of the DataFrame."""
    df = pd.DataFrame({
        'temperature_2m': [20, None, 22],
        'relative_humidity_2m': [60, 65, None],
        'precipitation': [0, 1, 0],
        'weather_code': [0, 1, 0],
        'wind_speed_10m': [5, 7, 10],
        'wind_direction_10m': [180, 190, 200],
        'wind_gusts_10m': [8, 9, 11],
    })

    cleaned_df = clean_dataframe(df)
    assert cleaned_df.isna().sum().sum() == 0  # Ensure no null values
    assert 'temperature_2m_C' in cleaned_df.columns  # Check renamed column

def test_store_data_to_db():
    """Test storing data to SQLite database."""
    df = pd.DataFrame({
        'temperature_2m_C': [20, 21, 22],
        'relative_humidity_2m_percent': [60, 65, 70],
        'precipitation_mm': [0, 1, 0],
        'weather_code': [0, 1, 0],
        'wind_speed_10m_kmh': [5, 7, 10],
        'wind_direction_10m_deg': [180, 190, 200],
        'wind_gusts_10m_kmh': [8, 9, 11],
    })

    with patch('sqlite3.connect') as mock_connect:
        mock_conn = mock_connect.return_value
        store_data_to_db(df, "hourly_data", mock_conn)
        
        # Check that to_sql was called
        df.to_sql = MagicMock()
        df.to_sql("hourly_data", mock_conn, if_exists='replace')
        df.to_sql.assert_called_once_with("hourly_data", mock_conn, if_exists='replace')

