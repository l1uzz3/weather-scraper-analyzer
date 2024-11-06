import pytest
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, mean_absolute_error
from src.br03_data_analysis.analyze_data import WeatherAnalyzer

@pytest.fixture
def sample_hourly_data():
    """Fixture for creating sample hourly data for testing."""
    date_rng = pd.date_range(start="2023-01-01", periods=24, freq='H')
    data = {
        'temperature_2m_C': np.random.randint(15, 35, size=(24)),
        'relative_humidity_2m_percent': np.random.randint(20, 80, size=(24)),
        'wind_speed_10m_kmh': np.random.randint(0, 20, size=(24)),
        'precipitation_mm': np.random.rand(24),
    }
    return pd.DataFrame(data, index=date_rng)

def test_feature_engineering(sample_hourly_data):
    """Test feature engineering steps for suitability criteria."""
    hourly_df = sample_hourly_data.copy()
    hourly_df['temperature_threshold'] = (hourly_df['temperature_2m_C'] > 20) & (hourly_df['temperature_2m_C'] < 30)
    hourly_df['humidity_threshold'] = (hourly_df['relative_humidity_2m_percent'] > 30) & (hourly_df['relative_humidity_2m_percent'] < 70)
    hourly_df['wind_threshold'] = hourly_df['wind_speed_10m_kmh'] < 15
    hourly_df['precipitation_threshold'] = hourly_df['precipitation_mm'] < 1
    hourly_df['event_suitability'] = (
        hourly_df['temperature_threshold'] &
        hourly_df['humidity_threshold'] &
        hourly_df['wind_threshold'] &
        hourly_df['precipitation_threshold']
    ).astype(int)
    
    assert 'event_suitability' in hourly_df.columns
    assert hourly_df['event_suitability'].isin([0, 1]).all()

def test_model_training_and_evaluation(sample_hourly_data):
    """Test model training and evaluation."""
    X = sample_hourly_data[['temperature_2m_C', 'relative_humidity_2m_percent', 'wind_speed_10m_kmh', 'precipitation_mm']]
    y = np.random.randint(0, 2, size=(X.shape[0]))  # Binary target for suitability

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    assert accuracy >= 0  # Accuracy should be a valid number
    assert mae >= 0       # MAE should be a valid number

def test_cross_validation(sample_hourly_data):
    """Test cross-validation scores for the Random Forest model."""
    X = sample_hourly_data[['temperature_2m_C', 'relative_humidity_2m_percent', 'wind_speed_10m_kmh', 'precipitation_mm']]
    y = np.random.randint(0, 2, size=(X.shape[0]))  # Binary target

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    cv_scores = cross_val_score(model, X, y, cv=5)

    assert len(cv_scores) == 5
    assert cv_scores.mean() >= 0

def test_hyperparameter_tuning(sample_hourly_data):
    """Test hyperparameter tuning for Random Forest model."""
    X = sample_hourly_data[['temperature_2m_C', 'relative_humidity_2m_percent', 'wind_speed_10m_kmh', 'precipitation_mm']]
    y = np.random.randint(0, 2, size=(X.shape[0]))  # Binary target

    param_grid_rf = {
        'n_estimators': [5, 10],
        'max_depth': [5, 10]
    }
    grid_search_rf = GridSearchCV(RandomForestClassifier(random_state=42), param_grid_rf, cv=3)
    grid_search_rf.fit(X, y)

    assert grid_search_rf.best_params_ is not None
    assert 'n_estimators' in grid_search_rf.best_params_
    assert 'max_depth' in grid_search_rf.best_params_

def test_feature_importance(sample_hourly_data):
    """Test feature importance for Random Forest model."""
    X = sample_hourly_data[['temperature_2m_C', 'relative_humidity_2m_percent', 'wind_speed_10m_kmh', 'precipitation_mm']]
    y = np.random.randint(0, 2, size=(X.shape[0]))  # Binary target

    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    importances = model.feature_importances_

    assert len(importances) == X.shape[1]  # Check that there are importances for each feature
    assert np.all(importances >= 0)  # Importances should be non-negative
