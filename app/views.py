from flask import abort, make_response, render_template
from app import app, auth, db, models

@app.errorhandler(404)
def not_found(error):
    return render_template('not-found.html')

@app.route('/')
def index():
	return render_template('index.html')
