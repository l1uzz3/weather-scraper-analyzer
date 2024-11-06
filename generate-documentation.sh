#!/bin/bash
sphinx-apidoc -o docs/source /../../src/br01_02_setup_api_store_data/fetch_weather/fetch_weather.py /../../src/br03_data_analysis/analyze_data.py
sphinx-build -b html docs/source docs
