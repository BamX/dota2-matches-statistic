#!/bin/bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
./dbcreate.py
./parse_heroes.py
./parse_teams.py
