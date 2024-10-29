# Use a lightweight Python 3.12 image
FROM python:3.12-slim

# Install essential system libraries (only if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    git \
    vim \
    curl \
    wget \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for better security
RUN useradd -m weather_project_user -s /bin/bash \
    && echo 'weather_project_user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

USER weather_project_user
WORKDIR /home/weather_project_user

# Set up a Python virtual environment and install dependencies
RUN python3 -m pip install --user virtualenv \
    pytest pytest-cov sphinx sphinx-autodoc-typehints sphinx-rtd-theme \
    && python3 -m virtualenv venv \
    && echo "source ~/venv/bin/activate" >> ~/.bashrc

# Install necessary Python libraries for the project
RUN /home/weather_project_user/venv/bin/pip install \
    requests pandas numpy matplotlib seaborn scikit-learn statsmodels beautifulsoup4 lxml ipykernel requests_cache openmeteo_requests retry_requests \
    sqlalchemy xgboost joblib tensorflow flask flask_sqlalchemy gunicorn dash plotly flask_wtf wtforms

# Set the default shell to bash instead of sh
SHELL ["/bin/bash", "--login", "-c"]

# Expose any necessary ports
EXPOSE 8080

# Default command to keep the container running
CMD ["sleep", "infinity"]
