#!/bin/bash
echo "BUILD START"

# 1. Install dependencies using the universal python3 command
python3 -m pip install -r requirements.txt

# 2. Force create the directories (This prevents the Vercel "No Output Directory" crash)
mkdir -p static
mkdir -p staticfiles_build/static
mkdir -p staticfiles

# 3. Run collectstatic and print any hidden errors to the screen
python3 manage.py collectstatic --noinput --clear

echo "BUILD END"