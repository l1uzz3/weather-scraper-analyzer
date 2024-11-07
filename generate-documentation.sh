#!/bin/bash

# Step 1: Clean up old generated documentation
echo "Cleaning up old documentation files..."
rm -rf docs/build/*

# Step 3: Build HTML documentation
echo "Building HTML documentation..."
sphinx-build -b html docs/source docs/build

echo "Documentation generated in docs/build"