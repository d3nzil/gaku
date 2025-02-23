#!/bin/env bash

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
  echo "requirements.txt not found!"
  exit 1
fi

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Virtual environment setup complete and dependencies installed."