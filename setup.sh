#!/bin/bash
#
# This script sets up the Python virtual environment and installs dependencies.

set -e

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Starting MkDocs live-reload server at http://127.0.0.1:8000/"
mkdocs serve

echo "Creating Python virtual environment in .venv..."
python3 -m venv .venv

echo "Activating the virtual environment and installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt

echo "Setup complete! To start the local server, run: source serve.sh"