# Importing libraries
import pandas as pd, sqlite3
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Setting up the connection to the database        
conn = sqlite3.connect(r"/workspaces/weather-scraper-analyzer/data/weather_data.db")
hourly_df = pd.read_sql(r"SELECT * FROM hourly_data", conn)
daily_df = pd.read_sql(r"SELECT * FROM daily_data", conn)

# Dropping the index column.
hourly_df = hourly_df.drop(columns='index')
daily_df = daily_df.drop(columns='index')
# print(hourly_df.head(1))
# print(daily_df.head(1))

# Convert 'date' columns to datetime | This is because SQLite doesn't have a datetime datatype so it stores the data as object. So we have to convert it here for further use even
# even if in the fetch script we converted it to date
hourly_df['date'] = pd.to_datetime(hourly_df['date'])
daily_df['date'] = pd.to_datetime(daily_df['date']) 
# print(hourly_df.dtypes)
# print(daily_df.dtypes)

# Setting the date as index
hourly_df = hourly_df.set_index('date')
daily_df = daily_df.set_index('date')


class WeatherAnalyzer:
    """
    Analyzes and aggregates hourly and daily weather data, providing various metrics and time-based aggregation.
    
    Attributes:
        hourly_data (DataFrame): DataFrame containing hourly weather data.
        daily_data (DataFrame): DataFrame containing daily weather data.
        hourly_metrics (dict): Metrics for hourly data, including mean, max, min, and standard deviation.
        daily_metrics (dict): Metrics for daily data, including mean, max, min, and standard deviation.
        timeframe_mapping (dict): Maps descriptive timeframes ('week', 'month', 'season', 'year') to resampling codes.
        season_names (dict): Maps season numbers (1-4) to names ('Winter', 'Spring', etc.).
    """

    def __init__(self, hourly_data, daily_data):
        """
        Initializes the WeatherAnalyzer with hourly and daily data.

        Args:
            hourly_data (DataFrame): Hourly weather data.
            daily_data (DataFrame): Daily weather data.
        """
        self.hourly_data = hourly_data
        self.daily_data = daily_data
        # Setting the metrics
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
            4: 'Autumn'
        }

    def aggregate_hourly(self, timeframe):
        """
        Aggregates hourly data based on the specified timeframe.

        Args:
            timeframe (str): Timeframe for aggregation ('week', 'month', 'season', 'year').

        Returns:
            DataFrame: Aggregated hourly data with specified metrics.
        """
        resample_code = self.timeframe_mapping.get(timeframe, timeframe)
        return self.hourly_data.resample(resample_code).agg(self.hourly_metrics)

    def aggregate_daily(self, timeframe):
        """
        Aggregates daily data based on the specified timeframe.

        Args:
            timeframe (str): Timeframe for aggregation ('week', 'month', 'season', 'year').

        Returns:
            DataFrame: Aggregated daily data with specified metrics.
        """
        resample_code = self.timeframe_mapping.get(timeframe, timeframe)
        return self.daily_data.resample(resample_code).agg(self.daily_metrics)

    def display_aggregated_data(self):
        """
        Generates aggregated data for weekly, monthly, seasonal, and yearly timeframes.

        Returns:
            dict: Dictionary containing aggregated data for different timeframes and metrics.
        """
        return {
            'weekly_hourly': self.aggregate_hourly('week'), 
            'weekly_daily': self.aggregate_daily('week'),
            'monthly_hourly': self.aggregate_hourly('month'),
            'monthly_daily': self.aggregate_daily('month'),
            'seasonal_hourly': self.aggregate_hourly('season'),
            'seasonal_daily': self.aggregate_daily('season'),
            'yearly_hourly': self.aggregate_hourly('year'),
            'yearly_daily': self.aggregate_daily('year')
        }

    def calculate_filter_variability(self, parameter, timeframe, threshold, variability_type):
        """
        Filters data based on variability threshold for a specified parameter.

        Args:
            parameter (str): Weather parameter to analyze.
            timeframe (str): Timeframe for aggregation.
            threshold (float): Variability threshold to filter data.
            variability_type (str): Type of variability ('above' or 'below').

        Returns:
            DataFrame: Filtered data based on specified variability criteria.
        """
        data = self.aggregate_hourly(timeframe) if timeframe in self.timeframe_mapping else None
        high_var = data[data[parameter]['std'] > threshold]
        low_var = data[data[parameter]['std'] < threshold]
        return high_var if variability_type == 'above' else low_var

    # generate month colors. 
    """This function generates colors for the following plots (for each month). I think this is not a crucial function to test since it's about visualization of the plots.
       Generate a color palette for each month.

    This method maps each month to a unique color for plot visualizations.
    Colors are generated using the 'hsv' palette, which provides a range of distinct colors.

    Parameters:
        data (DataFrame): Weather data with a datetime index containing month information.

    Returns:
        dict: A dictionary mapping each unique month name to a color.
    """    
    def generate_month_colors(self, data): # pragma: no cover
        unique_months = data.index.month_name().unique()  # Get unique month names from the index
        color_list = sns.color_palette("hsv", 12)
        self.month_colors = dict(zip(unique_months, color_list)) # merge months and colors together in a dict

    
    # generate season colors
    """This function generates colors for the following plots (for each season). I think this is not a crucial function to test since it's about visualization of the plots.
    Generate a color palette for each season.

        This method maps each season to a unique color for plot visualizations.
        Colors are generated using the 'hsv' palette.

        Parameters:
            data (DataFrame): Weather data with a datetime index containing season information.

        Returns:
            dict: A dictionary mapping each season name to a color.
        """
    def generate_season_colors(self, data): # pragma: no cover
        unique_seasons = data.index.quarter.unique()
        color_list = sns.color_palette("hsv", 4)
        self.season_colors = {self.season_names[season]: color for season, color in zip(unique_seasons, color_list)} # merge seasons and colors together in a dict
    
        
    # generate year_colors 
    """This function generates colors for the following plots (for each year). I think this is not a crucial function to test since it's about visualization of the plots.
    Generate a color palette for each year.

        This method maps each year to a unique color for plot visualizations.
        Colors are generated using the 'hsv' palette, with a maximum of 30 colors.

        Parameters:
            data (DataFrame): Weather data with a datetime index containing year information.

        Returns:
            dict: A dictionary mapping each unique year to a color.
        """
    def generate_year_colors(self, data): # pragma: no cover
        unique_years = data.index.year.unique()
        color_list = sns.color_palette("hsv", 30)
        self.year_colors = dict(zip(unique_years, color_list)) # merge years and colors together


    # plot variability
    """Since it's quite difficult to test actual graphs, I will exclude them from the testing.
    Plot weather data variability for specified timeframes.

        This method generates scatter plots showing high or low variability in a weather parameter 
        based on standard deviation thresholds. Plots are color-coded for months, seasons, or years.

        Parameters:
            parameter (str): The weather parameter to analyze (e.g., temperature).
            timeframe (str): The timeframe to aggregate data ('week', 'month', 'season', 'year').
            threshold (float): The standard deviation threshold for variability.
            variability_type (str): Type of variability to plot ('above' or 'under').

        Returns:
            PLOT
        """
    def plot_variability(self, parameter, timeframe, threshold, variability_type): # pragma: no cover
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
    """Not included in the testing. Plot yearly trends in weather data for weekly, monthly, seasonal, and yearly timeframes.

        This method generates trend plots, using heatmaps for weekly and monthly data,
        and line plots for seasonal and yearly data.

        Parameters:
            parameter (str): The weather parameter to analyze (e.g., temperature).
            timeframe (str): The timeframe for trend plotting ('week', 'month', 'season', 'year').

        Returns:
            PLOT
        """    
    def plot_trend(self, parameter, timeframe): # pragma: no cover
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

    # Boxplot weather variables distribution
        """Not included in the tests. 
        Generate seasonal boxplots for temperature, precipitation, and wind speed distributions.

        This method creates boxplots showing the distribution of weather parameters across different seasons.
        Useful for visualizing variability and comparing seasonal changes.

        Returns:
            PLOT
        """    
    def plot_seasonal_boxplots(self): # pragma: no cover
        # Add 'season' column to the daily data based on the quarter
        self.daily_data['season'] = self.daily_data.index.quarter.map(self.season_names)

        # Plot temperature box plot
        plt.figure(figsize=(15, 6))
        sns.boxplot(x='season', y='temperature_2m_mean_C', data=self.daily_data, palette='coolwarm')
        plt.title('Seasonal Temperature Distribution')
        plt.xlabel('Season')
        plt.ylabel('Mean Temperature (°C)')
        plt.show()

        # Plot precipitation box plot
        plt.figure(figsize=(15, 6))
        sns.boxplot(x='season', y='precipitation_sum_mm', data=self.daily_data, palette='Blues')
        plt.title('Seasonal Precipitation Distribution')
        plt.xlabel('Season')
        plt.ylabel('Total Precipitation (mm)')
        plt.show()

        # Plot wind speed box plot
        plt.figure(figsize=(15, 6))
        sns.boxplot(x='season', y='wind_speed_10m_max_kmh', data=self.daily_data, palette='viridis')
        plt.title('Seasonal Wind Speed Distribution')
        plt.xlabel('Season')
        plt.ylabel('Max Wind Speed (km/h)')
        plt.show()
                        
# through inheritance (powerful characteristic of classes in python (OOP language) we can inherit the parent class and create a child class)
# it will inherit functions(methods) like aggregate_daily / aggregate_hourly, or other variables!!!

class ExtremeWeatherAnalyzer(WeatherAnalyzer):
    """
    Analyzes extreme weather events by identifying, flagging, and calculating frequency of high and low extreme weather conditions.

    Inherits from:
        WeatherAnalyzer: A class for general weather data analysis and visualization.
    """
    def __init__(self, hourly_data, daily_data):
        # calling the constructor of the parent class
        """
        Initialize the ExtremeWeatherAnalyzer with hourly and daily weather data.

        Parameters:
            hourly_data (DataFrame): Hourly weather data.
            daily_data (DataFrame): Daily weather data.
        """
        super().__init__(hourly_data, daily_data)
    
    # Set fixed or percentile-based thresholds
    def define_thresholds(self):
        """
        Define thresholds for extreme weather events based on percentile values for temperature, precipitation, and wind speed.
        
        High and low extremes are set at the 95th and 5th percentiles of each parameter.
        """
        self.temperature_high = self.daily_data['temperature_2m_max_C'].quantile(0.95)
        self.temperature_low = self.daily_data['temperature_2m_min_C'].quantile(0.05)
        self.precipitation_high = self.daily_data['precipitation_sum_mm'].quantile(0.95)
        self.precipitation_low = self.daily_data['precipitation_sum_mm'].quantile(0.05)
        self.wind_speed_high = self.daily_data['wind_speed_10m_max_kmh'].quantile(0.95)
        self.wind_speed_low = self.daily_data['wind_speed_10m_max_kmh'].quantile(0.05)

    def flag_extreme_events(self):
        """
        Flag days with extreme weather events by setting indicators for high and low extremes of temperature, precipitation, and wind speed.

        Flags:
            - extreme_high_temp: Boolean flag for extreme high temperatures.
            - extreme_low_temp: Boolean flag for extreme low temperatures.
            - extreme_high_precipitation: Boolean flag for heavy precipitation days.
            - extreme_low_precipitation: Boolean flag for low precipitation days.
            - extreme_high_wind_speed: Boolean flag for high wind speed days.
            - extreme_low_wind_speed: Boolean flag for low wind speed days.
        """
        # Flag extreme high and low temperatures
        self.daily_data['extreme_high_temp'] = self.daily_data['temperature_2m_max_C'] > self.temperature_high
        self.daily_data['extreme_low_temp'] = self.daily_data['temperature_2m_min_C'] < self.temperature_low
        
        # Flag heavy precipitation days
        self.daily_data['extreme_high_precipitation'] = self.daily_data['precipitation_sum_mm'] > self.precipitation_high
        self.daily_data['extreme_low_precipitation'] = self.daily_data['precipitation_sum_mm'] < self.precipitation_low

        # Flag high wind speed days
        self.daily_data['extreme_high_wind_speed'] = self.daily_data['wind_speed_10m_max_kmh'] > self.wind_speed_high
        self.daily_data['extreme_low_wind_speed'] = self.daily_data['wind_speed_10m_max_kmh'] < self.wind_speed_low


    def calculate_frequency(self):
        """
        Calculate the frequency of extreme weather events by year.

        Returns:
            DataFrame: Frequency of each extreme weather event type by year.
        """
        # Calculate the frequency of extreme events by year
        extreme_events = self.daily_data.groupby(self.daily_data.index.year)[[
            'extreme_high_temp', 'extreme_low_temp', 'extreme_high_precipitation', 'extreme_low_precipitation', 
            'extreme_high_wind_speed', 'extreme_low_wind_speed']].sum()
        
        return extreme_events

    def plot_high_extreme_events(self, extreme_events): # pragma: no cover
        """
        Plot frequency of high extreme weather events over time, including high temperatures, precipitation, and wind speeds.

        Parameters:
            extreme_events (DataFrame): Frequency of extreme high events by year.

        Note:
            Excluded from testing as it generates plots.
        """
        plt.figure(figsize=(12, 8))

        # Scatter plot for extreme events (high)
        plt.scatter(extreme_events.index, extreme_events['extreme_high_temp'], label='Extreme High Temp', color='red')
        plt.scatter(extreme_events.index, extreme_events['extreme_high_precipitation'], label='Heavy Precipitation', color='green')
        plt.scatter(extreme_events.index, extreme_events['extreme_high_wind_speed'], label='High Wind Speed', color='purple')

        # Smoothed line for extreme high temperatures using a rolling mean
        extreme_events['extreme_high_temp'].rolling(window=3).mean().plot(
            linestyle='--', color='red', label='Smoothed High Temp', ax=plt.gca()
        )
        extreme_events['extreme_high_precipitation'].rolling(window=3).mean().plot(
            linestyle='--', color='green', label='Smoothed high precip', ax=plt.gca()
        )
        extreme_events['extreme_high_wind_speed'].rolling(window=3).mean().plot(
            linestyle='--', color='purple', label='Smoothed high wind speed', ax=plt.gca()
        )
        # Annotations for specific events
        plt.annotate(
            'Heatwave Year(2024)', xy=(2024, extreme_events['extreme_high_temp'].max()),
            xytext=(2024, 45), arrowprops=dict(facecolor='black', arrowstyle='->')
        )
        
        plt.annotate(
            'High wind speed Year(2023)', xy=(2023, extreme_events['extreme_high_wind_speed'].max()),
            xytext=(2023, 35), arrowprops=dict(facecolor='black', arrowstyle='->')
        )
        plt.annotate(
            f"Heavy precipitation year(2010)", xy=(2010, extreme_events['extreme_high_precipitation'].max()),
            xytext=(2010, 38), arrowprops=dict(facecolor='black', arrowstyle='->')
        )
        
        # Plot details
        plt.title('Frequency of High Extreme Weather Events Over Time')
        plt.xlabel('Year')
        plt.ylabel('Number of Extreme Events')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Events")
        plt.grid(True)
        plt.show()

    def plot_low_extreme_events(self, extreme_events): # pragma: no cover
        """
        Plot frequency of low extreme weather events over time, including low temperatures, precipitation, and wind speeds.

        Parameters:
            extreme_events (DataFrame): Frequency of extreme low events by year.

        Note:
            Excluded from testing as it generates plots.
        """
        plt.figure(figsize=(12, 8))

        # Scatter plot for extreme events (low)
        plt.scatter(extreme_events.index, extreme_events['extreme_low_temp'], label='Extreme Low Temp', color='blue')
        plt.scatter(extreme_events.index, extreme_events['extreme_low_precipitation'], label='Extreme low precipitation', color='black')
        plt.scatter(extreme_events.index, extreme_events['extreme_low_wind_speed'], label='Extreme low windspeed', color='purple')
        
        # Smoothed line for extreme high temperatures using a rolling mean
        extreme_events['extreme_low_temp'].rolling(window=3).mean().plot(
            linestyle='--', color='blue', label='Smoothed low Temp', ax=plt.gca()
        )
        extreme_events['extreme_low_precipitation'].rolling(window=3).mean().plot(
            linestyle='--', color='black', label='Smoothed low precip', ax=plt.gca()
        )
        extreme_events['extreme_low_wind_speed'].rolling(window=3).mean().plot(
            linestyle='--', color='purple', label='Smoothed low wind speed', ax=plt.gca()
        )
        # Annotations for specific events        
        plt.annotate(
            'Cold Wave Year(2003)', xy=(2003, extreme_events['extreme_low_temp'].max()),
            xytext=(2003, 37), arrowprops=dict(facecolor='black', arrowstyle='->')
        )
        plt.annotate(
            'Low precipitation year(all)', xy=(2010, extreme_events['extreme_low_precipitation'].max()),
            xytext=(2010, 2), arrowprops=dict(facecolor='black', arrowstyle='->')
        )
        plt.annotate(
            'Low speed wind year(2014)', xy=(2014, extreme_events['extreme_low_wind_speed'].max()),
            xytext=(2014, 40), arrowprops=dict(facecolor='black', arrowstyle='->')
        )

        # Plot details
        plt.title('Frequency of Low Extreme Weather Events Over Time')
        plt.xlabel('Year')
        plt.ylabel('Number of Extreme Events')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Events")
        plt.grid(True)
        plt.show()

    def calculate_average_values(self):
        """
        Calculate the average values for each type of extreme event.

        Returns:
            Variables like avg_high_temp, avg_low_temp, avg_high_precip, low_precip_data, avg_low_precip, avg_high_wind, avg_low_wind
        """
        # Calculate the average values for each extreme event
        avg_high_temp = self.daily_data[self.daily_data['extreme_high_temp']]['temperature_2m_max_C'].mean()
        avg_low_temp = self.daily_data[self.daily_data['extreme_low_temp']]['temperature_2m_min_C'].mean()
        avg_high_precip = self.daily_data[self.daily_data['extreme_high_precipitation']]['precipitation_sum_mm'].mean()
        low_precip_data = self.daily_data[self.daily_data['extreme_low_precipitation']]['precipitation_sum_mm']
        avg_low_precip = low_precip_data.mean() if not low_precip_data.empty else 0 
        avg_high_wind = self.daily_data[self.daily_data['extreme_high_wind_speed']]['wind_speed_10m_max_kmh'].mean()
        avg_low_wind = self.daily_data[self.daily_data['extreme_low_wind_speed']]['wind_speed_10m_max_kmh'].mean()
        # Print the average values
        print(f"Average High Temperature (Extreme Events): {avg_high_temp:.2f} °C")
        print(f"Average Low Temperature (Extreme Events): {avg_low_temp:.2f} °C")
        print(f"Average High Precipitation (Extreme Events): {avg_high_precip:.2f} mm")
        print(f"Average Low Precipitation (Extreme Events): {avg_low_precip:.2f} mm")
        print(f"Average High Wind Speed (Extreme Events): {avg_high_wind:.2f} km/h")
        print(f"Average Low Wind Speed (Extreme Events): {avg_low_wind:.2f} km/h")

## Usage
"""I will exclude the below block code because I individually tested the crucial functions above. This runs the script 
This script demonstrates how to use the `WeatherAnalyzer` and `ExtremeWeatherAnalyzer` classes
to analyze and visualize weather trends and extreme events. It runs specific functions for plotting 
trends, calculating variability, and analyzing extreme weather events.
Note:
The following code block is intended for demonstration purposes and should be excluded from testing 
because it includes extensive visualizations.
"""
if __name__ == '__main__': # pragma: no cover
    analyzer = WeatherAnalyzer()
    print("It works before defining the variable extreme_weather_analyzer to the ExtremeWeatherAnalyzer class...")
    extreme_weather_analyzer = ExtremeWeatherAnalyzer(hourly_df, daily_df)
    
    ## ***PLOTTING TRENDING***

    max_temp_week_trend = analyzer.plot_trend('temperature_2m_max_C', 'week')
    max_temp_month_trend = analyzer.plot_trend('temperature_2m_max_C', 'month')
    max_temp_season_trend = analyzer.plot_trend('temperature_2m_max_C', 'season')
    max_temp_year_trend = analyzer.plot_trend('temperature_2m_max_C', 'year')
    min_temp_week_trend = analyzer.plot_trend('temperature_2m_min_C', 'week')
    min_temp_month_trend = analyzer.plot_trend('temperature_2m_min_C', 'month')
    min_temp_season_trend = analyzer.plot_trend('temperature_2m_min_C', 'season')
    min_temp_year_trend = analyzer.plot_trend('temperature_2m_min_C', 'year')
    mean_temp_week_trend = analyzer.plot_trend('temperature_2m_mean_C', 'week')
    mean_temp_month_trend = analyzer.plot_trend('temperature_2m_mean_C', 'month')
    mean_temp_season_trend = analyzer.plot_trend('temperature_2m_mean_C', 'season')
    mean_temp_year_trend = analyzer.plot_trend('temperature_2m_mean_C', 'year')


    precipitation_week_trend = analyzer.plot_trend('precipitation_sum_mm', 'week')
    precipitation_month_trend = analyzer.plot_trend('precipitation_sum_mm', 'month')
    precipitation_season_trend = analyzer.plot_trend('precipitation_sum_mm', 'season')
    precipitation_year_trend = analyzer.plot_trend('precipitation_sum_mm', 'year')
    windspeed_week_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'week')
    windspeed_month_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'month')
    windspeed_season_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'season')
    windspeed_year_trend = analyzer.plot_trend('wind_speed_10m_max_kmh', 'year')
    windgust_week_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'week')
    windgust_month_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'month')
    windgust_season_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'season')
    windgust_year_trend = analyzer.plot_trend('wind_gusts_10m_max_kmh', 'year')


    ## ***PLOTTING VARIABILITY***

    # TEMPERATURE
    temp_high_variability_week = analyzer.plot_variability('temperature_2m_C', 'week', 5, 'above')
    temp_low_variability_week = analyzer.plot_variability('temperature_2m_C', 'week', 5, 'under')
    temp_high_variability_month = analyzer.plot_variability('temperature_2m_C', 'month', 5, 'above')
    temp_low_variability_month = analyzer.plot_variability('temperature_2m_C', 'month', 5, 'under')
    temp_high_variability_season = analyzer.plot_variability('temperature_2m_C', 'season', 5, 'above')
    temp_low_variability_season = analyzer.plot_variability('temperature_2m_C', 'season', 5, 'under')
    temp_high_variability_year = analyzer.plot_variability('temperature_2m_C', 'year', 5, 'above')
    temp_low_variability_year = analyzer.plot_variability('temperature_2m_C', 'year', 5, 'under')

    # RELATIVE HUMIDITY
    rel_humidity_high_variability_week = analyzer.plot_variability('relative_humidity_2m_percent', 'week', 5, 'above')
    rel_humidity_low_variability_week = analyzer.plot_variability('relative_humidity_2m_percent', 'week', 5, 'under')
    rel_humidity_high_variability_month = analyzer.plot_variability('relative_humidity_2m_percent', 'month', 5, 'above')
    rel_humidity_low_variability_month = analyzer.plot_variability('relative_humidity_2m_percent', 'month', 5, 'under')
    rel_humidity_high_variability_season = analyzer.plot_variability('relative_humidity_2m_percent', 'season', 5, 'above')
    rel_humidity_low_variability_season = analyzer.plot_variability('relative_humidity_2m_percent', 'season', 5, 'under')
    rel_humidity_high_variability_year = analyzer.plot_variability('relative_humidity_2m_percent', 'year', 5, 'above')
    rel_humidity_low_variability_year = analyzer.plot_variability('relative_humidity_2m_percent', 'year', 5, 'under')

    # PRECIPITATION
    precipitation_high_variability_week = analyzer.plot_variability('precipitation_mm', 'week', 5, 'above')
    precipitation_low_variability_week = analyzer.plot_variability('precipitation_mm', 'week', 5, 'under')
    precipitation_high_variability_month = analyzer.plot_variability('precipitation_mm', 'month', 5, 'above')
    precipitation_low_variability_month = analyzer.plot_variability('precipitation_mm', 'month', 5, 'under')
    precipitation_high_variability_season = analyzer.plot_variability('precipitation_mm', 'season', 5, 'above')
    precipitation_low_variability_season = analyzer.plot_variability('precipitation_mm', 'season', 5, 'under')
    precipitation_high_variability_year = analyzer.plot_variability('precipitation_mm', 'year', 5, 'above')
    precipitation_low_variability_year = analyzer.plot_variability('precipitation_mm', 'year', 5, 'under')

    # WIND SPEED
    windspeed_high_variability_week = analyzer.plot_variability('wind_speed_10m_kmh', 'week', 5, 'above')
    windspeed_low_variability_week = analyzer.plot_variability('wind_speed_10m_kmh', 'week', 5, 'under')
    windspeed_high_variability_month = analyzer.plot_variability('wind_speed_10m_kmh', 'month', 5, 'above')
    windspeed_low_variability_month = analyzer.plot_variability('wind_speed_10m_kmh', 'month', 5, 'under')
    windspeed_high_variability_season = analyzer.plot_variability('wind_speed_10m_kmh', 'season', 5, 'above')
    windspeed_low_variability_season = analyzer.plot_variability('wind_speed_10m_kmh', 'season', 5, 'under')
    windspeed_high_variability_year = analyzer.plot_variability('wind_speed_10m_kmh', 'year', 5, 'above')
    windspeed_low_variability_year = analyzer.plot_variability('wind_speed_10m_kmh', 'year', 5, 'under')

    # WIND GUSTS
    windgust_high_variability_week = analyzer.plot_variability('wind_gusts_10m_kmh', 'week', 5, 'above')
    windgust_low_variability_week = analyzer.plot_variability('wind_gusts_10m_kmh', 'week', 5, 'under')
    windgust_high_variability_month = analyzer.plot_variability('wind_gusts_10m_kmh', 'month', 5, 'above')
    windgust_low_variability_month = analyzer.plot_variability('wind_gusts_10m_kmh', 'month', 5, 'under')
    windgust_high_variability_season = analyzer.plot_variability('wind_gusts_10m_kmh', 'season', 5, 'above')
    windgust_low_variability_season = analyzer.plot_variability('wind_gusts_10m_kmh', 'season', 5, 'under')
    windgust_high_variability_year = analyzer.plot_variability('wind_gusts_10m_kmh', 'year', 5, 'above')
    windgust_low_variability_year = analyzer.plot_variability('wind_gusts_10m_kmh', 'year', 5, 'under')

    # WEATHER VARIABLES DISTRIBUTION
    analyzer.plot_seasonal_boxplots()

    # EXTREME WEATHER ANALYZER CLASS
    extreme_weather_analyzer.define_thresholds()
    extreme_weather_analyzer.flag_extreme_events()
    extreme_events = extreme_weather_analyzer.calculate_frequency()
    average_extreme_events = extreme_weather_analyzer.calculate_average_values()
    extreme_weather_analyzer.plot_high_extreme_events(extreme_events)
    extreme_weather_analyzer.plot_low_extreme_events(extreme_events)
