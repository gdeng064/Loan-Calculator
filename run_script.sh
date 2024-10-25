#!/bin/bash

# Create and activate a virtual environment
mkdir -p virtual_env
cd virtual_env || exit 1
python3 -m venv virtual_env
source virtual_env/bin/activate

# Install required packages
pip install matplotlib cryptography pyperclip pyotp qrcode

# Go back to the previous directory
cd ..

# Find and run the Python file in the current directory
python3 *.py
