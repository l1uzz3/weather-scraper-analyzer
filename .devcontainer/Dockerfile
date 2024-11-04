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
    # default-jdk if using java for spark 
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for better security
RUN useradd -m weather_project_user -s /bin/bash \
    && echo 'weather_project_user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

USER weather_project_user
WORKDIR /home/weather_project_user

# Download and unpack Apache Spark
# RUN wget https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz && \
#     tar -xvf spark-3.5.3-bin-hadoop3.tgz && \
#     mv spark-3.5.3-bin-hadoop3 spark && \
#     rm spark-3.5.3-bin-hadoop3.tgz

# Set up a Python virtual environment and install dependencies
RUN python3 -m pip install --user virtualenv \
    pytest pytest-cov sphinx sphinx-autodoc-typehints sphinx-rtd-theme \
    && python3 -m virtualenv venv \
    && echo "source ~/venv/bin/activate" >> ~/.bashrc

# Install necessary Python libraries for the project
RUN /home/weather_project_user/venv/bin/pip install \
    absl-py==2.1.0 \
    aiohappyeyeballs==2.4.3 \
    aiohttp==3.10.10 \
    aiosignal==1.3.1 \
    appdirs==1.4.4 \
    asttokens==2.4.1 \
    astunparse==1.6.3 \
    attrs==24.2.0 \
    beautifulsoup4==4.12.3 \
    blinker==1.8.2 \
    cattrs==24.1.2 \
    certifi==2024.8.30 \
    charset-normalizer==3.4.0 \
    click==8.1.7 \
    clikit==0.6.2 \
    cmdstanpy==1.2.4 \
    comm==0.2.2 \
    contourpy==1.3.0 \
    convertdate==2.4.0 \
    crashtest==0.3.1 \
    cycler==0.12.1 \
    Cython==3.0.11 \
    dash==2.18.1 \
    dash-core-components==2.0.0 \
    dash-html-components==2.0.0 \
    dash-table==5.0.0 \
    debugpy==1.8.7 \
    decorator==5.1.1 \
    executing==2.1.0 \
    Flask==3.0.3 \
    Flask-SQLAlchemy==3.1.1 \
    Flask-WTF==1.2.2 \
    flatbuffers==24.3.25 \
    fonttools==4.54.1 \
    frozenlist==1.5.0 \
    gast==0.6.0 \
    google-pasta==0.2.0 \
    greenlet==3.1.1 \
    grpcio==1.67.0 \
    gunicorn==23.0.0 \
    h5py==3.12.1 \
    holidays==0.59 \
    httpstan==4.13.0 \
    idna==3.10 \
    importlib_metadata==8.5.0 \
    importlib_resources==6.4.5 \
    ipykernel==6.29.5 \
    ipython==8.29.0 \
    ipywidgets==8.1.5 \
    itsdangerous==2.2.0 \
    jedi==0.19.1 \
    Jinja2==3.1.4 \
    joblib==1.4.2 \
    jupyter_client==8.6.3 \
    jupyter_core==5.7.2 \
    jupyterlab_widgets==3.0.13 \
    keras==3.6.0 \
    kiwisolver==1.4.7 \
    libclang==18.1.1 \
    lxml==5.3.0 \
    Markdown==3.7 \
    markdown-it-py==3.0.0 \
    MarkupSafe==3.0.2 \
    marshmallow==3.23.1 \
    matplotlib==3.9.2 \
    matplotlib-inline==0.1.7 \
    mdurl==0.1.2 \
    ml-dtypes==0.4.1 \
    multidict==6.1.0 \
    namex==0.0.8 \
    nest-asyncio==1.6.0 \
    numpy==2.0.2 \
    nvidia-nccl-cu12==2.23.4 \
    openmeteo_requests==1.3.0 \
    openmeteo_sdk==1.18.0 \
    opt_einsum==3.4.0 \
    optree==0.13.0 \
    packaging==24.1 \
    pandas==2.2.3 \
    parso==0.8.4 \
    pastel==0.2.1 \
    patsy==0.5.6 \
    pexpect==4.9.0 \
    pillow==11.0.0 \
    platformdirs==4.3.6 \
    plotly==5.24.1 \
    prompt_toolkit==3.0.48 \
    propcache==0.2.0 \
    prophet==1.1.6 \
    protobuf==5.28.3 \
    psutil==6.1.0 \
    ptyprocess==0.7.0 \
    pure_eval==0.2.3 \
    Pygments==2.18.0 \
    pylev==1.4.0 \
    PyMeeus==0.5.12 \
    # pyspark \
    pyparsing==3.2.0 \
    pysimdjson==6.0.2 \
    pystan==3.10.0 \
    python-dateutil==2.9.0.post0 \
    pytz==2024.2 \
    pyzmq==26.2.0 \
    requests==2.32.3 \
    requests-cache==1.2.1 \
    retry-requests==2.0.0 \
    retrying==1.3.4 \
    rich==13.9.3 \
    scikit-learn==1.5.2 \
    scipy==1.14.1 \
    seaborn==0.13.2 \
    setuptools==75.2.0 \
    six==1.16.0 \
    soupsieve==2.6 \
    SQLAlchemy==2.0.36 \
    stack-data==0.6.3 \
    stanio==0.5.1 \
    statsmodels==0.14.4 \
    tenacity==9.0.0 \
    tensorboard==2.18.0 \
    tensorboard-data-server==0.7.2 \
    tensorflow==2.18.0 \
    termcolor==2.5.0 \
    threadpoolctl==3.5.0 \
    tornado==6.4.1 \
    tqdm==4.66.6 \
    traitlets==5.14.3 \
    typing_extensions==4.12.2 \
    tzdata==2024.2 \
    url-normalize==1.4.3 \
    urllib3==2.2.3 \
    wcwidth==0.2.13 \
    webargs==8.6.0 \
    Werkzeug==3.0.6 \
    wheel==0.44.0 \
    widgetsnbextension==4.0.13 \
    wrapt==1.16.0 \
    WTForms==3.2.1 \
    xgboost==2.1.2 \
    yarl==1.17.1 \
    zipp==3.20.2 
    # h2o \
    # h2o_pysparkling_3.5 
    
# Set environment variables for Java and PySpark
ENV JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
ENV SPARK_HOME="/home/weather_project_user/spark"
ENV PATH="$SPARK_HOME/bin:$JAVA_HOME/bin:$PATH"

# Set the default shell to bash instead of sh
SHELL ["/bin/bash", "--login", "-c"]

# Expose any necessary ports
EXPOSE 8080

# Default command to keep the container running
CMD ["sleep", "infinity"]
