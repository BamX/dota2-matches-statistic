#!env/bin/python
from app import db, models
import sys
import urllib2
import datetime, time
from bs4 import BeautifulSoup

ONCE = False

url = "http://www.dotabuff.com/esports/teams/%s/matches?page=%s"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def teamSoup(teamId, page):
    teamUrl = url % (teamId, page)
    html = ""
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        f = opener.open(teamUrl)
        html = f.read()
        f.close()
    except urllib2.HTTPError, err:
        if err.code == 429:
            print 'Requests limit. Please, wait for a hour or two'
            exit()
    return BeautifulSoup(html)

def gameTime(str):
    val = 0
    for s in str.split(':'):
        val = val * 60 + int(s)
    return val

def heroesFromTD(td):
    heroes = []
    for img in td.find_all('img'):
        heroName = img['title']
        heroes.append(heroName)
    return heroes

def parseMatchTR(tr):
    matchId = tr.find_all('td')[0].a['href'].split('/')[-1]
    won = tr.a['class'][0] == u'won'    
    length = gameTime(tr.find_all('td')[2].text)
    date = datetime.datetime.strptime(tr.find_all('td')[0].time['datetime'], "%Y-%m-%dT%H:%M:%S+00:00")

    otherTeamId = None
    otherTeamName = None
    if tr.find_all('td')[1].a:
        otherTeamId = tr.find_all('td')[1].a['href'].split('/')[-1]
        otherTeamName = tr.find_all('td')[1].a.text

    heroes = heroesFromTD(tr.find_all('td')[3])
    opHeroes = heroesFromTD(tr.find_all('td')[4])

    return {
        'matchId' : matchId,
        'won' : won, 
        'otherTeamId' : otherTeamId, 
        'otherTeamName' : otherTeamName, 
        'length' : length, 
        'date' : date, 
        'heroes' : heroes, 
        'opHeroes' : opHeroes
    }

def parseMatches(teamId, page):
    soup = teamSoup(teamId, page)
    return map(parseMatchTR, soup.find_all('tr')[1:])

def parseTeam(currentTeamId, once):
    team = models.Team.query.filter_by(id = currentTeamId).first()
    pagesCount = 1
    if team:
        soup = teamSoup(currentTeamId, 0)
        if soup.select("span[class~=last]"):
            pagesCount = int(soup.select("span[class~=last]")[0].a['href'].split('=')[-1])

        repeatFinded = False
        for page in range(1, pagesCount + 1):
            for parsedMatch in parseMatches(currentTeamId, page):
                match = models.Match.query.filter_by(id = parsedMatch['matchId']).first()
                if match:
                    print '[%s] Match exists: %s vs %s' % (currentTeamId, team.name, parsedMatch['otherTeamName'])
                    repeatFinded = True
                    if once:
                        break
                    continue
                otherTeamId = parsedMatch['otherTeamId']
                otherTeam = models.Team.query.filter_by(id = otherTeamId).first()
                if otherTeam is None:
                    if otherTeamId is None:
                        print '[%s] Unknown team skipped' % (currentTeamId)
                        continue
                    otherTeam = models.Team(id = otherTeamId, name = parsedMatch['otherTeamName'])
                    db.session.add(otherTeam)
                    print bcolors.WARNING + '[%s] Team added: %s' % (currentTeamId, otherTeam.name) + bcolors.ENDC
                match = models.Match(id = parsedMatch['matchId'], length = parsedMatch['length'], date = parsedMatch['date'])
                db.session.add(match)
                heroes = map(lambda heroName: models.Hero.query.filter_by(name = heroName).first(),parsedMatch['heroes'])
                opHeroes = map(lambda heroName: models.Hero.query.filter_by(name = heroName).first(),parsedMatch['opHeroes'])

                participant = models.Participant(team_id = team.id, match_id = match.id, won = parsedMatch['won'], heroes = heroes)
                db.session.add(participant)
                opParticipant = models.Participant(team_id = otherTeam.id, match_id = match.id, won = not parsedMatch['won'], heroes = opHeroes)
                db.session.add(opParticipant)
                db.session.commit()
                print bcolors.OKGREEN + '[%s] Match added: %s vs %s' % (currentTeamId, team.name, otherTeam.name) + bcolors.ENDC
            if repeatFinded and once:
                break

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == 'update':
            print bcolors.HEADER + 'Updating last matches' + bcolors.ENDC
            for team in models.Team.query.filter(models.Team.imageUrl != None).all():
                parseTeam(team.id, True)
        else:
            print bcolors.HEADER + 'Parsing team %s' % (sys.argv[1]) + bcolors.ENDC
            parseTeam(sys.argv[1], ONCE)
    elif len(sys.argv) == 3:
        if (sys.argv[1] == 'from'):
            print bcolors.HEADER + 'Parsing teams from %s' % (sys.argv[2]) + bcolors.ENDC
            for team in models.Team.query.filter(models.Team.imageUrl != None, models.Team.id >= int(sys.argv[2])).all():
                parseTeam(team.id, ONCE)
    else:
        print bcolors.HEADER + 'Parsing all teams' + bcolors.ENDC
        for team in models.Team.query.filter(models.Team.imageUrl != None).all():
            parseTeam(team.id, ONCE)
