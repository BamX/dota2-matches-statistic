#!env/bin/python
from app import db, models
import sys
import urllib2
import datetime, time
from bs4 import BeautifulSoup

ONCE = False

url = "http://www.dotabuff.com/esports/teams/%s/matches?page=%s"

def teamSoup(teamId, page):
    teamUrl = url % (teamId, page)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    f = opener.open(teamUrl)
    html = f.read()
    f.close()
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

def parseTeam(currentTeamId):
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
                    repeatFinded = True
                    if ONCE:
                        break
                    continue
                otherTeamId = parsedMatch['otherTeamId']
                otherTeam = models.Team.query.filter_by(id = otherTeamId).first()
                if otherTeam is None:
                    if otherTeamId is None:
                        print 'Unknown team skipped'
                        continue
                    otherTeam = models.Team(id = otherTeamId, name = parsedMatch['otherTeamName'])
                    db.session.add(otherTeam)
                    print 'Team added: %s' % (otherTeam.name)
                match = models.Match(id = parsedMatch['matchId'], length = parsedMatch['length'], date = parsedMatch['date'])
                db.session.add(match)
                heroes = map(lambda heroName: models.Hero.query.filter_by(name = heroName).first(),parsedMatch['heroes'])
                opHeroes = map(lambda heroName: models.Hero.query.filter_by(name = heroName).first(),parsedMatch['opHeroes'])

                participant = models.Participant(team_id = team.id, match_id = match.id, won = parsedMatch['won'], heroes = heroes)
                db.session.add(participant)
                opParticipant = models.Participant(team_id = otherTeam.id, match_id = match.id, won = not parsedMatch['won'], heroes = opHeroes)
                db.session.add(opParticipant)
                db.session.commit()
                print 'Match added: %s vs %s' % (team.name, otherTeam.name)
            if repeatFinded and ONCE:
                break

if __name__ == "__main__":
    if len(sys.argv) == 2:
        parseTeam(sys.argv[1])
    else:
        for team in models.Team.query.filter(models.Team.imageUrl != None).all():
            parseTeam(team.id)





