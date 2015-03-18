# Dota2 : Matches Statistic
Pro-matches statistic for **Dota 2**. 
It's small **Flask** app with a few **Python** scripts to parse matches data from web. 
It works with **SQLite** DB by default.

## Requirements
This app requres **Python 2.7**, **pip** and **virtualenv** to be installed.

## Installation
* Download or clone repository
* Run **./setup.sh** 
	* it inits enviroment
	* it creates DB
	* it parses heroes and top teams from web
* Run **./parse_matches.py** 
	* it parses all matches of top teams. **WARNING** *Affects Error 429*
	* you could skip this step by uing app.db from one of archives: https://yadi.sk/d/UmrAiZ4jfLBDz

## Usage
Run **./run.py** (it runs web server on 5000 port by default) and open http://127.0.0.1:5000.
To update matches DB use **./parse_last_matches.py** *(don't use it with empty db)*.
