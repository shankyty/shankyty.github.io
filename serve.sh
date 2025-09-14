#!/bin/bash
#
# This script activates the virtual environment and starts the MkDocs server.

set -e

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Starting MkDocs live-reload server at http://127.0.0.1:8000/"
mkdocs serve