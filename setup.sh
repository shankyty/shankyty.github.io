#!/bin/bash
#
# This script sets up the Python virtual environment and installs dependencies.

set -e # Exit immediately if a command exits with a non-zero status.

echo "Creating Python virtual environment in .venv..."
python3 -m venv .venv

echo "Activating the virtual environment and installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

echo "Setup complete! To start the local server, run: source serve.sh"