import sys
import pandas as pd
import numpy as np
import sqlite3
from prophet import Prophet
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import psutil

# Importing WeatherAnalyzer from the analyze_data script
sys.path.append('/workspaces/weather-scraper-analyzer/src/03-data_analysis')
from analyze_data import WeatherAnalyzer

def log_resource_usage(step):
    """
    Log and display resource usage (CPU and memory).

    Args:
        step (str): Description of the step in the process for logging.
    """
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    print(f"[{step}] CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}%")

def fit_prophet_model(series, variable_name):
    """
    Fit a Prophet model to a time series and forecast for the next 5 years.

    Args:
        series (pd.Series): The time series data to fit.
        variable_name (str): Name of the variable being forecasted.

    Returns:
        pd.DataFrame: Forecasted values with confidence intervals.
        str: Variable name.
    """
    # Prepare data for Prophet model
    df = series.reset_index()
    df.columns = ['ds', 'y']

    # Log resource usage before and after fitting
    log_resource_usage(f"Before fitting Prophet model for {variable_name}")
    model = Prophet()
    model.fit(df)
    log_resource_usage(f"After fitting Prophet model for {variable_name}")

    # Forecast for the next 5 years
    future = model.make_future_dataframe(periods=5 * 365)
    forecast = model.predict(future)

    # Display the confidence interval for the forecast
    print(f"\n{variable_name} Forecast Confidence Interval (First 10 rows):")
    print(forecast[['ds', 'yhat_lower', 'yhat_upper']].head(10))

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], variable_name

def main():
    """
    Main function to execute the weather data analysis and forecast process.
    """
    # Connect to SQLite database and load daily weather data
    conn = sqlite3.connect(r"/workspaces/weather-scraper-analyzer/data/weather_data.db")
    daily_df = pd.read_sql(r"SELECT * FROM daily_data", conn)

    # Preprocess data
    daily_df = daily_df.drop(columns='index')
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    daily_df = daily_df.set_index('date')
    daily_df.index = pd.to_datetime(daily_df.index).to_period('D').to_timestamp()

    # Initialize WeatherAnalyzer (if needed for further analysis)
    analyzer = WeatherAnalyzer(None, daily_df)

    # Define variables for forecasting
    variables = {
        "Temperature": daily_df['temperature_2m_mean_C'].dropna(),
        "Precipitation": daily_df['precipitation_sum_mm'].dropna(),
        "Wind Speed": daily_df['wind_speed_10m_max_kmh'].dropna()
    }

    # Log initial resource usage and measure start time
    start_time = datetime.now()
    log_resource_usage("Start of the process")

    # Fit Prophet model for each variable and store results
    prophet_results = {}
    for var_name, series in variables.items():
        prophet_results[var_name] = fit_prophet_model(series, var_name)

    # Log final resource usage and measure end time
    end_time = datetime.now()
    print(f"Model fitting duration: {end_time - start_time}")
    log_resource_usage("End of the process")

    # Plot forecast results for each variable
    for var_name, (forecast, _) in prophet_results.items():
        plt.figure(figsize=(14, 7))
        plt.plot(forecast['ds'], forecast['yhat'], color='green', label="Forecast")
        plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='green', alpha=0.3, label="Confidence Interval")
        plt.title(f"Prophet Forecast for {var_name} (2025 to 2030)")
        plt.xlabel("Date")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.gca().xaxis.set_major_locator(mdates.YearLocator(1))  # Show every year
        plt.xticks(rotation=45)
        plt.ylabel(var_name)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Confidence Interval")
        plt.show()

if __name__ == "__main__":
    main()
