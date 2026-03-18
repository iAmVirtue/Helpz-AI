#!/bin/bash
echo "BUILD START"

# Use python3 instead of python3.9 to avoid "command not found" on different Vercel server racks
python3 -m pip install -r requirements.txt

# Force Django to put the files in the staticfiles folder
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"