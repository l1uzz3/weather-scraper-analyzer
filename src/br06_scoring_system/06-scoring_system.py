import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import sys
from datetime import datetime

# Importing WeatherAnalyzer from the analyze_data script
sys.path.append('/workspaces/weather-scraper-analyzer/src/br03_data_analysis')
from analyze_data import WeatherAnalyzer

# Connect to SQLite database and load daily weather data
with sqlite3.connect(r"/workspaces/weather-scraper-analyzer/data/weather_data.db") as conn:
    daily_df = pd.read_sql(r"SELECT * FROM daily_data", conn)

# Preprocess data
daily_df = daily_df.drop(columns='index')
daily_df['date'] = pd.to_datetime(daily_df['date'])
daily_df = daily_df.set_index('date')
daily_df.index = pd.to_datetime(daily_df.index).to_period('D').to_timestamp()

# Initialize WeatherAnalyzer (if needed for further analysis)
analyzer = WeatherAnalyzer(None, daily_df)

# Define variables for scoring
weather_weights = {
    "temperature": 0.4,  # Weight for temperature
    "precipitation": 0.3,  # Weight for precipitation
    "wind_speed": 0.3  # Weight for wind speed
}

# Define ideal conditions for each parameter
ideal_conditions = {
    "temperature": (18, 25),  # Comfortable temperature range in °C
    "precipitation": 0,  # Ideal precipitation level (no rain)
    "wind_speed": 10  # Ideal wind speed in km/h
}

# Function to calculate event suitability score
def calculate_score(temperature, precipitation, wind_speed):
    # Normalize temperature: higher score if within the ideal range
    if ideal_conditions["temperature"][0] <= temperature <= ideal_conditions["temperature"][1]:
        temp_score = 1
    else:
        temp_score = max(0, min(1, 1 - abs(temperature - ideal_conditions["temperature"][0]) / 
                               (ideal_conditions["temperature"][1] - ideal_conditions["temperature"][0])))

    # Normalize precipitation: higher score if there's no precipitation
    precip_score = 1 if precipitation <= ideal_conditions["precipitation"] else 0

    # Normalize wind speed: higher score if wind speed is close to the ideal
    wind_score = max(0, min(1, 1 - abs(wind_speed - ideal_conditions["wind_speed"]) / ideal_conditions["wind_speed"]))

    # Composite score calculation using weights
    score = (temp_score * weather_weights["temperature"] +
             precip_score * weather_weights["precipitation"] +
             wind_score * weather_weights["wind_speed"])
    return score * 100  # Scale score to be out of 100

# Calculate scores for historical data
scores = []
for index, row in daily_df.iterrows():
    try:
        temperature = row["temperature_2m_mean_C"]
        precipitation = row["precipitation_sum_mm"]
        wind_speed = row["wind_speed_10m_max_kmh"]

        # Skip rows with missing values
        if pd.isnull(temperature) or pd.isnull(precipitation) or pd.isnull(wind_speed):
            continue

        # Calculate the event suitability score
        score = calculate_score(temperature, precipitation, wind_speed)
        scores.append({"date": index, "score": score})
    except Exception as e:
        print(f"Error processing row {index}: {e}")

# Convert scores to a DataFrame
scores_df = pd.DataFrame(scores)

# Save scores to a CSV file for further use
scores_df.to_csv(r"/workspaces/weather-scraper-analyzer/output/event_suitability_scores.csv", index=False)

# Analyze historical scores
print("Descriptive statistics for event suitability scores:")
print(scores_df.describe())

# Group scores by month for average analysis
scores_df['month'] = scores_df['date'].dt.month
monthly_avg_scores = scores_df.groupby('month')['score'].mean()
print("\nAverage Event Suitability Score by Month:")
print(monthly_avg_scores)

# Visualize scores
plt.figure(figsize=(12, 6))
plt.plot(scores_df['date'], scores_df['score'], label="Event Suitability Score", color='green')
plt.axhline(y=70, color='red', linestyle='--', label="Good Event Threshold (70%)")
plt.xlabel('Date')
plt.ylabel('Suitability Score (%)')
plt.title('Event Suitability Score Over Time')
plt.legend()
plt.grid(True)
plt.savefig(r"/workspaces/weather-scraper-analyzer/output/event_suitability_score_plot.png")
plt.show()

# Visualize monthly average scores
plt.figure(figsize=(12, 6))
plt.bar(monthly_avg_scores.index, monthly_avg_scores.values, color='blue', alpha=0.7)
plt.axhline(y=70, color='red', linestyle='--', label="Good Event Threshold (70%)")
plt.xlabel('Month')
plt.ylabel('Average Suitability Score (%)')
plt.title('Average Event Suitability Score by Month')
plt.xticks(range(1, 13), [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
])
plt.legend()
plt.grid(axis='y')
plt.savefig(r"/workspaces/weather-scraper-analyzer/output/average_suitability_score_by_month.png")
plt.show()
