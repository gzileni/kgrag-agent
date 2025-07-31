#!/bin/bash

echo "Inizializzazione dello script di deploy..."
rm -Rf dist/

echo "Building the Python package..."
python -m build

echo "Uploading the package to the repository..."
twine upload -r agent-server dist/*
