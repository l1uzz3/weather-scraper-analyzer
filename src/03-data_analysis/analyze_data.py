import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

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

class WeatherAnalyzer:
    # initializing the class and setting the variables 
    def __init__(self, hourly_data, daily_data):
        self.hourly_data = hourly_data
        self.daily_data = daily_data

        self.hourly_metrics = {
            'temperature_2m_C': ['mean', 'max', 'min', 'std'],
            'relative_humidity_2m_percent': ['mean', 'max', 'min', 'std'],
            'precipitation_mm': ['mean', 'max', 'min', 'std'],
            'wind_speed_10m_kmh': ['mean', 'max', 'min', 'std'],
            'wind_direction_10m_deg': ['mean', 'max', 'min', 'std'],
            'wind_gusts_10m_kmh': ['mean', 'max', 'min', 'std']
        }
        self.daily_metrics = {
            'temperature_2m_max_C': ['mean', 'max', 'min', 'std'],
            'temperature_2m_min_C': ['mean', 'max', 'min', 'std'],
            'temperature_2m_mean_C': ['mean', 'max', 'min', 'std'],
            'precipitation_sum_mm': ['mean', 'max', 'min', 'std'],
            'wind_speed_10m_max_kmh': ['mean', 'max', 'min', 'std'],
            'wind_gusts_10m_max_kmh': ['mean', 'max', 'min', 'std'],
            'wind_direction_10m_dominant_deg': ['mean', 'max', 'min', 'std']
        }

        self.timeframe_mapping = {
            'week': 'W',
            'month': 'ME',
            'season': 'QE',
            'year': 'YE'
        }
        self.season_names = {
            1: 'Winter', 
            2: 'Spring', 
            3: 'Summer', 
            4: 'Autumn'}

    # aggregations hourly, daily (week, month, season, year)

    def aggregate_hourly(self, timeframe):
        # Map descriptive timeframe to the corresponding code
        resample_code = self.timeframe_mapping.get(timeframe, timeframe)  # fallback to original code if not mapped
        return self.hourly_data.resample(resample_code).agg(self.hourly_metrics)

    def aggregate_daily(self, timeframe):
        # Map descriptive timeframe to the corresponding code
        resample_code = self.timeframe_mapping.get(timeframe, timeframe)
        return self.daily_data.resample(resample_code).agg(self.daily_metrics)

    def display_aggregated_data(self):
        # Weekly aggregations
        weekly_hourly = self.aggregate_hourly('W')
        weekly_daily = self.aggregate_daily('W')
        
        # Monthly aggregations
        monthly_hourly = self.aggregate_hourly('ME')
        monthly_daily = self.aggregate_daily('ME')
        
        # Seasonal aggregations
        seasonal_hourly = self.aggregate_hourly('QE')
        seasonal_daily = self.aggregate_daily('QE')
        
        # Yearly aggregations
        yearly_hourly = self.aggregate_hourly('YE')
        yearly_daily = self.aggregate_daily('YE')
        
        return {
            'weekly_hourly': weekly_hourly, 
            'weekly_daily': weekly_daily,
            'monthly_hourly': monthly_hourly,
            'monthly_daily': monthly_daily,
            'seasonal_hourly': seasonal_hourly,
            'seasonal_daily': seasonal_daily,
            'yearly_hourly': yearly_hourly,
            'yearly_daily': yearly_daily
        }

    # calculate above/under variability to find variations (More extreme variations = extreme weather.) 
    def calculate_filter_variability(self, parameter, timeframe, threshold, variability_type):
        data = self.aggregate_hourly(timeframe) if timeframe in self.timeframe_mapping else None
        high_var = data[data[parameter]['std'] > threshold]
        low_var = data[data[parameter]['std'] < threshold]
        return high_var if variability_type == 'above' else low_var

    # generate month colors. 
    def generate_month_colors(self, data): 
        unique_months = data.index.month_name().unique()  # Get unique month names from the index
        color_list = sns.color_palette("hsv", 12)
        self.month_colors = dict(zip(unique_months, color_list)) # merge months and colors together in a dict

    
    # generate season colors
    def generate_season_colors(self, data):
        unique_seasons = data.index.quarter.unique()
        color_list = sns.color_palette("hsv", 4)
        self.season_colors = {self.season_names[season]: color for season, color in zip(unique_seasons, color_list)} # merge seasons and colors together in a dict
    
        
    # generate year_colors 
    def generate_year_colors(self, data):
        unique_years = data.index.year.unique()
        color_list = sns.color_palette("hsv", 30)
        self.year_colors = dict(zip(unique_years, color_list)) # merge years and colors together


    # plot variability
    def plot_variability(self, parameter, timeframe, threshold, variability_type):
        high_variability_data = self.calculate_filter_variability(parameter, timeframe, threshold, variability_type='above')
        low_variability_data = self.calculate_filter_variability(parameter, timeframe, threshold, variability_type='under')
        
        if timeframe == 'week': # WEEK DATA
            
            if variability_type == 'above':
                plt.figure(figsize=(15, 6))
                plt.scatter(high_variability_data.index, high_variability_data[parameter]['std'], marker='o', label=f"{parameter} Std.dev")
                plt.title(f'Higher Variability in {parameter} (Timeframe: {timeframe} | Std.dev > {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend()
                plt.grid(True)
                plt.show()
            elif variability_type == 'under':
                plt.figure(figsize=(15, 6))
                plt.scatter(low_variability_data.index, low_variability_data[parameter]['std'], marker='o', label=f"{parameter} Std.dev")
                plt.title(f'Lower Variability in {parameter} (Timeframe: {timeframe} | Std.dev < {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend()
                plt.grid(True)
                plt.show()
        
        elif timeframe == 'month': # MONTH DATA
         
            self.generate_month_colors(self.hourly_data) # set colors for unique months.

            if variability_type == 'above':

                high_variability_data['month'] = high_variability_data.index.month_name()  # Map index to month names

                plt.figure(figsize=(15, 6))
                # for loop to plot the month & colors
                for month, color in self.month_colors.items():
                    subset = high_variability_data[high_variability_data['month'] == month]
                    plt.scatter(subset.index, subset[parameter]['std'], marker='o', label=f"{month}", color = color, zorder = 3)
                plt.title(f'Higher Variability in {parameter} (Timeframe: {timeframe} | Std.dev > {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Months")
                plt.gca().set_facecolor('#6e6969')  # Set the background to a gray color
                plt.grid(True)
                plt.show()

            elif variability_type == 'under':

                low_variability_data['month'] = low_variability_data.index.month_name()  # Map index to month names

                plt.figure(figsize=(15, 6))
                # for loop to plot the month & colors
                for month, color in self.month_colors.items():
                    subset = low_variability_data[low_variability_data['month'] == month]
                    plt.scatter(subset.index, subset[parameter]['std'], marker='o', label=f"{month}", color = color, zorder = 3)
                plt.title(f'Lower Variability in {parameter} (Timeframe: {timeframe} | Std.dev < {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Months")
                plt.gca().set_facecolor('#6e6969')  # Set the background to a gray color
                plt.grid(True)
                plt.show()

        elif timeframe == 'season': # SEASON DATA
            self.generate_season_colors(self.hourly_data) # set colors for unique seasons
            

            if variability_type == 'above':
                high_variability_data['season'] = high_variability_data.index.quarter.map(self.season_names)  # Map index to seasons

                plt.figure(figsize=(15, 6))
                # for loop to plot the seasons & colors
                for season, color in self.season_colors.items():
                    subset = high_variability_data[high_variability_data['season'] == season]
                    plt.scatter(subset.index, subset[parameter]['std'], marker='o', label=f"{season}", color = color, zorder = 3)
                plt.title(f'{variability_type.capitalize()} variability in {parameter} (Timeframe: {timeframe} | Std.dev > {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Seasons")
                plt.gca().set_facecolor('#6e6969')  # Set the background to a gray color
                plt.grid(True)
                plt.show()

            elif variability_type == 'under':
                low_variability_data['season'] = low_variability_data.index.quarter.map(self.season_names) # map index to seasons

                plt.figure(figsize=(15, 6))
                # for loop to plot the seasons and colors
                for season, color in self.season_colors.items():
                    subset = low_variability_data[low_variability_data['season'] == season]
                    plt.scatter(subset.index, subset[parameter]['std'], marker = 'o', label = {season}, color = color, zorder = 3)
                plt.title(f'{variability_type.capitalize()} variability in {parameter} (Timeframe: {timeframe} | Std.dev < {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Seasons")
                plt.gca().set_facecolor('#6e6969')  # Set the background to a gray color
                plt.grid(True)
                plt.show()
        
        else: # YEAR DATA
            self.generate_year_colors(self.hourly_data) # set colors for unique years.

            if variability_type == 'above':
                high_variability_data['year'] = high_variability_data.index.year  # Map index to years
                plt.figure(figsize=(15, 6))
                # for loop to plot the years & colors
                for year, color in self.year_colors.items():
                    subset = high_variability_data[high_variability_data['year'] == year]
                    plt.scatter(subset.index, subset[parameter]['std'], marker='o', label=f"{year}", color = color, zorder = 3)  

                plt.title(f'Higher Variability in {parameter} (Timeframe: {timeframe} | Std.dev > {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Years")
                plt.gca().set_facecolor('#6e6969')  # Set the background to a dark gray color
                plt.grid(True, color='#444444')  # Set grid lines to a lighter shade for contrast
                plt.tight_layout()
                plt.show()

            elif variability_type == 'under':
                low_variability_data['year'] = low_variability_data.index.year  # Map index to years 
                plt.figure(figsize=(15, 6))
                # for loop to plot the years & colors
                for year, color in self.year_colors.items():
                    subset = low_variability_data[low_variability_data['year'] == year]
                    plt.scatter(subset.index, subset[parameter]['std'], marker='o', label=f"{year}", color = color, zorder = 3)  
                plt.title(f'Lower Variability in {parameter} (Timeframe: {timeframe} | Std.dev < {threshold})')
                plt.xlabel('Time')
                plt.ylabel(f'{parameter} Standard Deviation')
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Years")
                plt.gca().set_facecolor('#6e6969')  # Set the background to a gray color
                plt.grid(True, color='#444444')  # Set grid lines to a lighter shade for contrast
                plt.tight_layout()
                plt.show()
            

    # plotting yearly trends using daily data
    def plot_trend(self, parameter, timeframe):
        weekly_data = self.aggregate_daily('week')
        monthly_data = self.aggregate_daily('month')
        seasonal_data = self.aggregate_daily('season')
        yearly_data = self.aggregate_daily('year')

        if timeframe == 'week':  # Weekly trend as a heatmap
            # Filter to get only 'mean' for the specified parameter
            weekly_data = weekly_data[(parameter, 'mean')].reset_index()
            
            # Rename columns for easy access
            weekly_data.columns = ['date', 'value']
            weekly_data['year'] = weekly_data['date'].dt.year
            weekly_data['week'] = weekly_data['date'].dt.isocalendar().week  # Get ISO week number

            # Aggregate by year and week to ensure unique values for each combination
            weekly_data = weekly_data.groupby(['year', 'week'])['value'].mean().reset_index()

            # Pivot table for the heatmap
            heatmap_data = weekly_data.pivot(index='week', columns='year', values='value')

            # Plotting the heatmap
            plt.figure(figsize=(15, 8))
            sns.heatmap(heatmap_data, cmap="coolwarm", annot=False, fmt=".1f", cbar_kws={'label': f'{parameter.capitalize()}'})
            plt.title(f"Weekly {parameter.capitalize()} Heatmap Over Years")
            plt.xlabel("Year")
            plt.ylabel("Week")
            plt.show()

        elif timeframe == 'month':  # Monthly trend as a heatmap
            # Filter to get only 'mean' for the specified parameter
            monthly_data = monthly_data[(parameter, 'mean')].reset_index()
            
            monthly_data.columns = ['date', 'value']  # Rename columns for easy access
            monthly_data['year'] = monthly_data['date'].dt.year
            monthly_data['month'] = monthly_data['date'].dt.month_name()

            # Pivot table for the heatmap
            heatmap_data = monthly_data.pivot(index='month', columns='year', values='value')

            # Sort the months to ensure the heatmap shows January through December in order
            month_order = ["January", "February", "March", "April", "May", "June", 
                        "July", "August", "September", "October", "November", "December"]
            heatmap_data = heatmap_data.reindex(month_order)

            # Plotting the heatmap
            plt.figure(figsize=(15, 8))
            sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".1f", cbar_kws={'label': f'{parameter.capitalize()}'})
            plt.title(f"Monthly {parameter.capitalize()} Heatmap Over Years")
            plt.xlabel("Year")
            plt.ylabel("Month")
            plt.show()

        elif timeframe == 'season':  # Seasonal trend plot
            seasonal_data['year'] = seasonal_data.index.year
            seasonal_data['season'] = seasonal_data.index.quarter.map(self.season_names)
            
            plt.figure(figsize=(15, 6))
            for season in seasonal_data['season'].unique():
                subset = seasonal_data[seasonal_data['season'] == season]
                plt.plot(subset['year'], subset[parameter]['mean'], marker='o', label=season)
            plt.title(f'Seasonal Average {parameter.capitalize()} Trends')
            plt.xlabel('Year')
            plt.ylabel(f'{parameter.capitalize()} (°C)')
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Seasons")
            plt.show()

        else:  # Yearly trend plot
            yearly_data['year'] = yearly_data.index.year  # Map index to years

            plt.figure(figsize=(15, 6))
            # Plot all years at once
            plt.plot(yearly_data.index, yearly_data[parameter]['mean'], linestyle='-', marker = 'o', color='green', label=f'Yearly Average {parameter}')
            
            plt.title(f'Yearly {parameter.capitalize()} Trends')
            plt.xlabel('Year')
            plt.ylabel(f'{parameter.capitalize()} (°C)')
            plt.legend(loc='upper left', title="Trend")
            plt.show()
                        

# Usage
# analyzer = WeatherAnalyzer(hourly_data=hourly_df, daily_data=daily_df)

### ***PLOTTING TRENDING***

# max_temp_week_trend = analyzer.plot_trend('temperature_2m_max_C', 'week')
# max_temp_month_trend = analyzer.plot_trend('temperature_2m_max_C', 'month')
# max_temp_season_trend = analyzer.plot_trend('temperature_2m_max_C', 'season')
# max_temp_year_trend = analyzer.plot_trend('temperature_2m_max_C', 'year')
# min_temp_week_trend = analyzer.plot_trend('temperature_2m_min_C', 'week')
# min_temp_month_trend = analyzer.plot_trend('temperature_2m_min_C', 'month')
# min_temp_season_trend = analyzer.plot_trend('temperature_2m_min_C', 'season')
# min_temp_year_trend = analyzer.plot_trend('temperature_2m_min_C', 'year')
# mean_temp_week_trend = analyzer.plot_trend('temperature_2m_mean_C', 'week')
# mean_temp_month_trend = analyzer.plot_trend('temperature_2m_mean_C', 'month')
# mean_temp_season_trend = analyzer.plot_trend('temperature_2m_mean_C', 'season')
# mean_temp_year_trend = analyzer.plot_trend('temperature_2m_mean_C', 'year')


# precipitation_week_trend = analyzer.plot_trend('precipitation_sum_mm', 'week')
# precipitation_month_trend = analyzer.plot_trend('precipitation_sum_mm', 'month')
# precipitation_season_trend = analyzer.plot_trend('precipitation_sum_mm', 'season')
# precipitation_year_trend = analyzer.plot_trend('precipitation_sum_mm', 'year')
# windspeed_week_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'week')
# windspeed_month_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'month')
# windspeed_season_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'season')
# windspeed_year_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'year')
# windgust_week_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'week')
# windgust_month_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'month')
# windgust_season_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'season')
# windgust_year_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'year')


### ***PLOTTING VARIABILITY***

# TEMPERATURE
# temp_high_variability_week = analyzer.plot_variability('temperature_2m_C', 'week', 5, 'above')
# temp_low_variability_week = analyzer.plot_variability('temperature_2m_C', 'week', 5, 'under')
# temp_high_variability_month = analyzer.plot_variability('temperature_2m_C', 'month', 5, 'above')
# temp_low_variability_month = analyzer.plot_variability('temperature_2m_C', 'month', 5, 'under')
# temp_high_variability_season = analyzer.plot_variability('temperature_2m_C', 'season', 5, 'above')
# temp_low_variability_season = analyzer.plot_variability('temperature_2m_C', 'season', 5, 'under')
# temp_high_variability_year = analyzer.plot_variability('temperature_2m_C', 'year', 5, 'above')
# temp_low_variability_year = analyzer.plot_variability('temperature_2m_C', 'year', 5, 'under')

# RELATIVE HUMIDITY
# rel_humidity_high_variability_week = analyzer.plot_variability('relative_humidity_2m_percent', 'week', 5, 'above')
# rel_humidity_low_variability_week = analyzer.plot_variability('relative_humidity_2m_percent', 'week', 5, 'under')
# rel_humidity_high_variability_month = analyzer.plot_variability('relative_humidity_2m_percent', 'month', 5, 'above')
# rel_humidity_low_variability_month = analyzer.plot_variability('relative_humidity_2m_percent', 'month', 5, 'under')
# rel_humidity_high_variability_season = analyzer.plot_variability('relative_humidity_2m_percent', 'season', 5, 'above')
# rel_humidity_low_variability_season = analyzer.plot_variability('relative_humidity_2m_percent', 'season', 5, 'under')
# rel_humidity_high_variability_year = analyzer.plot_variability('relative_humidity_2m_percent', 'year', 5, 'above')
# rel_humidity_low_variability_year = analyzer.plot_variability('relative_humidity_2m_percent', 'year', 5, 'under')

# PRECIPITATION
# precipitation_high_variability_week = analyzer.plot_variability('precipitation_mm', 'week', 5, 'above')
# precipitation_low_variability_week = analyzer.plot_variability('precipitation_mm', 'week', 5, 'under')
# precipitation_high_variability_month = analyzer.plot_variability('precipitation_mm', 'month', 5, 'above')
# precipitation_low_variability_month = analyzer.plot_variability('precipitation_mm', 'month', 5, 'under')
# precipitation_high_variability_season = analyzer.plot_variability('precipitation_mm', 'season', 5, 'above')
# precipitation_low_variability_season = analyzer.plot_variability('precipitation_mm', 'season', 5, 'under')
# precipitation_high_variability_year = analyzer.plot_variability('precipitation_mm', 'year', 5, 'above')
# precipitation_low_variability_year = analyzer.plot_variability('precipitation_mm', 'year', 5, 'under')

# WIND SPEED
# windspeed_high_variability_week = analyzer.plot_variability('wind_speed_10m_kmh', 'week', 5, 'above')
# windspeed_low_variability_week = analyzer.plot_variability('wind_speed_10m_kmh', 'week', 5, 'under')
# windspeed_high_variability_month = analyzer.plot_variability('wind_speed_10m_kmh', 'month', 5, 'above')
# windspeed_low_variability_month = analyzer.plot_variability('wind_speed_10m_kmh', 'month', 5, 'under')
# windspeed_high_variability_season = analyzer.plot_variability('wind_speed_10m_kmh', 'season', 5, 'above')
# windspeed_low_variability_season = analyzer.plot_variability('wind_speed_10m_kmh', 'season', 5, 'under')
# windspeed_high_variability_year = analyzer.plot_variability('wind_speed_10m_kmh', 'year', 5, 'above')
# windspeed_low_variability_year = analyzer.plot_variability('wind_speed_10m_kmh', 'year', 5, 'under')

# WIND GUSTS
# windgust_high_variability_week = analyzer.plot_variability('wind_gusts_10m_kmh', 'week', 5, 'above')
# windgust_low_variability_week = analyzer.plot_variability('wind_gusts_10m_kmh', 'week', 5, 'under')
# windgust_high_variability_month = analyzer.plot_variability('wind_gusts_10m_kmh', 'month', 5, 'above')
# windgust_low_variability_month = analyzer.plot_variability('wind_gusts_10m_kmh', 'month', 5, 'under')
# windgust_high_variability_season = analyzer.plot_variability('wind_gusts_10m_kmh', 'season', 5, 'above')
# windgust_low_variability_season = analyzer.plot_variability('wind_gusts_10m_kmh', 'season', 5, 'under')
# windgust_high_variability_year = analyzer.plot_variability('wind_gusts_10m_kmh', 'year', 5, 'above')
# windgust_low_variability_year = analyzer.plot_variability('wind_gusts_10m_kmh', 'year', 5, 'under')
