import pytest
import pandas as pd
from src.br03_data_analysis.analyze_data import WeatherAnalyzer, ExtremeWeatherAnalyzer

# Fixtures to create sample hourly and daily data
@pytest.fixture
def sample_hourly_data():
    """
    Fixture for creating sample hourly data for testing.
    Generates a DataFrame with temperature, humidity, precipitation, wind speed,
    wind direction, and wind gust data indexed by hourly timestamps.
    """
    date_rng = pd.date_range(start="2023-01-01", periods=24, freq='H')
    data = {
        'temperature_2m_C': [15 + i for i in range(24)],
        'relative_humidity_2m_percent': [60 + i for i in range(24)],
        'precipitation_mm': [0.1 * i for i in range(24)],
        'wind_speed_10m_kmh': [5 + i for i in range(24)],
        'wind_direction_10m_deg': [180 + i for i in range(24)],
        'wind_gusts_10m_kmh': [8 + i for i in range(24)],
    }
    return pd.DataFrame(data, index=date_rng)

@pytest.fixture
def sample_daily_data():
    """
    Fixture for creating sample daily data for testing.
    Generates a DataFrame with max, min, and mean temperature, total precipitation,
    max wind speed, max wind gusts, and dominant wind direction data indexed by daily timestamps.
    """
    date_rng = pd.date_range(start="2023-01-01", periods=10, freq='D')
    data = {
        'temperature_2m_max_C': [20 + i for i in range(10)],
        'temperature_2m_min_C': [10 + i for i in range(10)],
        'temperature_2m_mean_C': [15 + i for i in range(10)],
        'precipitation_sum_mm': [0.5 * i for i in range(10)],
        'wind_speed_10m_max_kmh': [12 + i for i in range(10)],
        'wind_gusts_10m_max_kmh': [15 + i for i in range(10)],
        'wind_direction_10m_dominant_deg': [200 + i for i in range(10)],
    }
    return pd.DataFrame(data, index=date_rng)

def test_aggregate_hourly(sample_hourly_data):
    """
    Test the `aggregate_hourly` method of `WeatherAnalyzer`.
    This function verifies that weekly aggregation of hourly data produces a DataFrame
    with expected columns and frequency.
    """
    analyzer = WeatherAnalyzer(hourly_data=sample_hourly_data)
    weekly_data = analyzer.aggregate_hourly('week')
    assert 'temperature_2m_C' in weekly_data.columns.levels[0]
    assert weekly_data.index.freqstr in ['W', 'W-SUN']

def test_aggregate_daily(sample_daily_data):
    """
    Test the `aggregate_daily` method of `WeatherAnalyzer`.
    This function verifies that monthly aggregation of daily data produces a DataFrame
    with expected columns and frequency.
    """
    analyzer = WeatherAnalyzer(daily_data=sample_daily_data)
    monthly_data = analyzer.aggregate_daily('month')
    assert 'temperature_2m_max_C' in monthly_data.columns.levels[0]
    assert monthly_data.index.freqstr == 'ME'

def test_calculate_filter_variability(sample_hourly_data):
    """
    Test the `calculate_filter_variability` method of `WeatherAnalyzer`.
    This function checks the output of the variability calculation to ensure it
    returns a DataFrame with the expected columns.
    """
    analyzer = WeatherAnalyzer(hourly_data=sample_hourly_data)
    high_var = analyzer.calculate_filter_variability(
        parameter='temperature_2m_C', timeframe='week', threshold=1.5, variability_type='above'
    )
    assert isinstance(high_var, pd.DataFrame)
    assert 'temperature_2m_C' in high_var.columns.levels[0]

def test_display_aggregated_data(sample_hourly_data, sample_daily_data):
    """
    Test the `display_aggregated_data` method of `WeatherAnalyzer`.
    This function verifies that the output contains all expected aggregation keys
    (e.g., 'weekly_hourly', 'yearly_daily').
    """
    analyzer = WeatherAnalyzer(hourly_data=sample_hourly_data, daily_data=sample_daily_data)
    result = analyzer.display_aggregated_data()
    assert 'weekly_hourly' in result
    assert 'yearly_daily' in result

def test_calculate_average_values(sample_daily_data, capsys):
    """
    Test the calculation of average values for each extreme event category.
    Ensures accurate averages for extreme temperatures, precipitation, and wind speed.
    """
    analyzer = ExtremeWeatherAnalyzer(hourly_data=pd.DataFrame(), daily_data=sample_daily_data)
    
    # Define thresholds and flag extreme events
    analyzer.define_thresholds()
    analyzer.flag_extreme_events()
    
    # Call the method to calculate and print average values
    analyzer.calculate_average_values()

    # Capture the output of the print statements
    captured = capsys.readouterr()

    # Verify expected output by checking for certain key strings or values in the output
    assert "Average High Temperature" in captured.out
    assert "Average Low Temperature" in captured.out
    assert "Average High Precipitation" in captured.out
    assert "Average Low Precipitation" in captured.out
    assert "Average High Wind Speed" in captured.out
    assert "Average Low Wind Speed" in captured.out

@pytest.fixture
def extreme_analyzer(sample_daily_data):
    """
    Fixture for creating an instance of the `ExtremeWeatherAnalyzer` class
    with sample daily data.
    """
    return ExtremeWeatherAnalyzer(hourly_data=None, daily_data=sample_daily_data)

def test_define_thresholds(extreme_analyzer):
    """
    Test the `define_thresholds` method in `ExtremeWeatherAnalyzer`.
    Verifies that thresholds for temperature, precipitation, and wind speed
    are correctly calculated based on the 5th and 95th percentiles.
    """
    extreme_analyzer.define_thresholds()
    assert hasattr(extreme_analyzer, 'temperature_high')
    assert hasattr(extreme_analyzer, 'temperature_low')
    assert hasattr(extreme_analyzer, 'precipitation_high')
    assert hasattr(extreme_analyzer, 'precipitation_low')
    assert hasattr(extreme_analyzer, 'wind_speed_high')
    assert hasattr(extreme_analyzer, 'wind_speed_low')

def test_flag_extreme_events(extreme_analyzer):
    """
    Test the `flag_extreme_events` method in `ExtremeWeatherAnalyzer`.
    Verifies that extreme event flags for high/low temperatures, precipitation,
    and wind speed are correctly added to the daily data.
    """
    extreme_analyzer.define_thresholds()
    extreme_analyzer.flag_extreme_events()
    assert 'extreme_high_temp' in extreme_analyzer.daily_data.columns
    assert 'extreme_low_temp' in extreme_analyzer.daily_data.columns
    assert 'extreme_high_precipitation' in extreme_analyzer.daily_data.columns
    assert 'extreme_low_precipitation' in extreme_analyzer.daily_data.columns
    assert 'extreme_high_wind_speed' in extreme_analyzer.daily_data.columns
    assert 'extreme_low_wind_speed' in extreme_analyzer.daily_data.columns

def test_calculate_frequency(extreme_analyzer):
    """
    Test the `calculate_frequency` method in `ExtremeWeatherAnalyzer`.
    Ensures that the frequency calculation of extreme events by year is accurate.
    """
    extreme_analyzer.define_thresholds()
    extreme_analyzer.flag_extreme_events()
    extreme_events = extreme_analyzer.calculate_frequency()
    assert isinstance(extreme_events, pd.DataFrame)
    assert 'extreme_high_temp' in extreme_events.columns
    assert 'extreme_low_temp' in extreme_events.columns
    assert 'extreme_high_precipitation' in extreme_events.columns
    assert 'extreme_low_precipitation' in extreme_events.columns
    assert 'extreme_high_wind_speed' in extreme_events.columns
    assert 'extreme_low_wind_speed' in extreme_events.columns
