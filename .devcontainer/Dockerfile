# Use Ubuntu 20.04 LTS as the base image
FROM ubuntu:20.04

# Avoid prompts from apt to hang the build
ARG DEBIAN_FRONTEND=noninteractive

# Update the package repository and install necessary packages
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
       sudo \
       python3-pip \
       python3-dev \
       git \
       vim \
       curl \
       wget \
       bash-completion \
       build-essential \
       sqlite3 \
       libxml2-dev libxslt1-dev python3-lxml \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a new user 'weather_project_user' and give them sudo access
RUN useradd -m weather_project_user -s /bin/bash \
    && echo 'weather_project_user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# Switch to user 'weather_project_user'
USER weather_project_user
WORKDIR /home/weather_project_user

# Set up a Python virtual environment and activate it in .bashrc
RUN python3 -m pip install --user virtualenv \
    && python3 -m virtualenv venv \
    && echo "source ~/venv/bin/activate" >> ~/.bashrc

# Install essential Python packages for the project
RUN /home/weather_project_user/venv/bin/pip install requests pandas numpy matplotlib seaborn scikit-learn statsmodels beautifulsoup4 lxml

# Set the default shell to bash instead of sh
SHELL ["/bin/bash", "--login", "-c"]

# Expose any necessary ports (adjust as needed)
EXPOSE 8080

# Default command to keep the container running
CMD ["sleep", "infinity"]
