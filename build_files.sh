#!/bin/bash
set -e

# The Vercel build image's Python is externally managed (PEP 668), so install
# our dependencies into an isolated virtualenv and use it for the build steps.
python3 -m venv .venv_build
. .venv_build/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py seed_demo
