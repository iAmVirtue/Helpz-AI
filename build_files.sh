#!/bin/bash
# Install dependencies
python3.11 -m pip install -r requirements.txt
# Run collectstatic
python3.11 manage.py collectstatic --noinput --clear
