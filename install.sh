#!/bin/bash
pip install virtualenv
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cp .env-example .env
