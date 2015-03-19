from flask import jsonify, abort, request, make_response, render_template, redirect
from app import app, auth, db, models
from sqlalchemy.orm import aliased

BASE_URL = "http://www.dotabuff.com/"

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

@app.route('/open/match/<int:matchId>')
def openMatch(matchId):
    return redirect("%s/matches/%s" % (BASE_URL, matchId))

@app.route('/open/team/<int:teamId>')
def openTeam(teamId):
    return redirect("%s/esports/teams/%s" % (BASE_URL, teamId))

@app.route('/teams')
def getTeams():
    query = request.args['query']
    teams = [{'id':team.id, 'name': team.name} for team in models.Team.query.filter(models.Team.name.contains(query), models.Team.imageUrl != None).order_by('name').all()]
    return jsonify(items = teams)

@app.route('/<int:firstTeamId>/vs/<int:secondTeamId>')
def versus(firstTeamId, secondTeamId):
    if firstTeamId == secondTeamId:
        abort(404)
    firstTeam = models.Team.query.filter_by(id = firstTeamId).first_or_404()
    secondTeam = models.Team.query.filter_by(id = secondTeamId).first_or_404()

    p1alias = aliased(models.Participant)
    p2alias = aliased(models.Participant)

    matches = models.Match.query.\
        join(p1alias, models.Match.participants).\
        join(p2alias, models.Match.participants).\
        filter(p1alias.team_id == firstTeamId).\
        filter(p2alias.team_id == secondTeamId)
    return render_template('versus.html', matches = matches, firstTeam = firstTeam, secondTeam = secondTeam)
