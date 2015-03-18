from flask import jsonify, abort, request, make_response, render_template
from app import app, auth, db, models

def allTeams(fameous):
	query = models.Team.query
	if fameous:
		query = query.filter(models.Team.imageUrl != None)
	return query.all()

@app.errorhandler(404)
def not_found(error):
    return render_template('not-found.html')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/teams')
def getTeams():
	query = request.args['query']
	teams = [{'id':team.id, 'name': team.name} for team in models.Team.query.filter(models.Team.name.contains(query), models.Team.imageUrl != None).order_by('name').all()]
	return jsonify(items = teams)
