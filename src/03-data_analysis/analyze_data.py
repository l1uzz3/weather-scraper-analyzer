import pandas as pd, sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect(r"/workspaces/weather-scraper-analyzer/data/weather_data.db")

hourly_df = pd.read_sql(r"SELECT * FROM hourly_data", conn)
daily_df = pd.read_sql(r"SELECT * FROM daily_data", conn)

# Convert 'date' columns to datetime | This is because SQLite doesn't have a datetime datatype so it stores the data as object. So we have to convert it here for further use even
# even if in the fetch script we converted it to date

hourly_df['date'] = pd.to_datetime(hourly_df['date'])
daily_df['date'] = pd.to_datetime(daily_df['date']) 

daily_df.drop(columns='index', inplace=True)
hourly_df.drop(columns='index', inplace=True)

# Set the date as the index for easier resampling

hourly_df = hourly_df.set_index('date')
daily_df = daily_df.set_index('date')

# For hourly data
hourly_metrics = {
    'temperature_2m_C': ['mean', 'max', 'min', 'std'],
    'relative_humidity_2m_percent': ['mean', 'max', 'min', 'std'],
    'precipitation_mm': ['mean', 'max', 'min', 'std'],
    'wind_speed_10m_kmh': ['mean', 'max', 'min', 'std'],
    'wind_direction_10m_deg': ['mean', 'max', 'min', 'std'],
    'wind_gusts_10m_kmh': ['mean', 'max', 'min', 'std']

}
# SETTING THE DATE FRAMES 


# Weekly aggregation
weekly_hourly = hourly_df.resample('W').agg(hourly_metrics)
weekly_hourly
# Monthly aggregation
monthly_hourly = hourly_df.resample('ME').agg(hourly_metrics)

# Seasonal (quarterly) aggregation
seasonal_hourly = hourly_df.resample('QE').agg(hourly_metrics)

# Yearly aggregation
yearly_hourly = hourly_df.resample('YE').agg(hourly_metrics)

# For daily data 
daily_metrics = {
    'temperature_2m_max_C': ['mean', 'max', 'min', 'std'],
    'temperature_2m_min_C': ['mean', 'max', 'min', 'std'],
    'temperature_2m_mean_C':['mean', 'max', 'min', 'std'],
    'precipitation_sum_mm': ['mean', 'max', 'min', 'std'],
    'wind_speed_10m_max_kmh': ['mean', 'max', 'min', 'std'],
    'wind_gusts_10m_max_kmh': ['mean', 'max', 'min', 'std'],
    'wind_direction_10m_dominant_deg': ['mean', 'max', 'min', 'std']
}

# Weekly aggregation
weekly_daily = daily_df.resample('W').agg(daily_metrics)

# Monthly aggregation
monthly_daily = daily_df.resample('ME').agg(daily_metrics)

# Seasonal (quarterly) aggregation
seasonal_daily = daily_df.resample('QE').agg(daily_metrics)

# Yearly aggregation
yearly_daily = daily_df.resample('YE').agg(daily_metrics)


# Setting up the high temperature variability for further plotting 
yearly_hourly['temperature_2m_C_rolling_mean'] = yearly_hourly['temperature_2m_C']['mean'].rolling(window=3).mean()

# Map quarters to seasons
def map_season(quarter):
    if quarter == 1:
        return 'Winter'
    elif quarter == 2:
        return 'Spring'
    elif quarter == 3:
        return 'Summer'
    elif quarter == 4:
        return 'Autumn'

# Apply the function to assign seasons
seasonal_hourly['season'] = seasonal_hourly.index.quarter.map(map_season)

# Filter for high variability in temperature across seasons
high_variability_seasonal = seasonal_hourly[seasonal_hourly['temperature_2m_C']['std'] > 5]
print("Seasons with high temperature variability:")
print(len(high_variability_seasonal))




# Plot with colors representing each season
plt.figure(figsize=(10, 6))
for season, color in zip(['Winter', 'Spring', 'Summer', 'Autumn'], ['blue', 'green', 'red', 'orange']):
    subset = high_variability_seasonal[high_variability_seasonal['season'] == season]
    plt.plot(subset.index, subset['temperature_2m_C']['std'], marker='o', linestyle='-', label=season, color=color)

plt.title('Seasons with High Temperature Variability (Std Dev > 5°C) using hourly data')
plt.xlabel('Season')
plt.ylabel('Temperature Variability (Standard Deviation)')
plt.legend()
plt.grid(True)
plt.show()

# Rolling average for temperature to observe trend
yearly_daily['temperature_2m_C_rolling_mean'] = yearly_daily['temperature_2m_mean_C']['mean'].rolling(window=3).mean()

# Plotting trends

plt.figure(figsize=(10, 5))
plt.plot(yearly_daily.index, yearly_daily['temperature_2m_mean_C']['mean'], label='Yearly Average Temp')
plt.plot(yearly_daily.index, yearly_daily['temperature_2m_C_rolling_mean'], label='3-Year Rolling Avg Temp', linestyle='--')
plt.title('Temperature Trends Over Years (daily data)')
plt.xlabel('Year')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.show()
