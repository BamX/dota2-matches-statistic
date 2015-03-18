#!env/bin/python
from app import db, models
import sys
import urllib2
import datetime, time
from bs4 import BeautifulSoup

PAGES_COUNT = 50

url = "http://www.dotabuff.com/esports/matches?page=%s"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def matchesSoup(page):
    matchesUrl = url % (page)
    html = ""
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        f = opener.open(matchesUrl)
        html = f.read()
        f.close()
    except urllib2.HTTPError, err:
        if err.code == 429:
            print 'Requests limit. Please, wait for a hour or two'
            exit()
    return BeautifulSoup(html)

def parseTeamTD(td):
    teamId = None
    teamName = "Unknown"
    if td('span')[0].a:
        teamId = int(td('span')[0].a['href'].split('/')[-1])
        teamName = td.a.text
    heroes = []
    for a in td.div('a'):
        heroId = a['href'].split('/')[-1]
        heroes.append(heroId)

    return {
        'id' : teamId,
        'name' : teamName,
        'heroes' : heroes
    }

def gameTime(str):
    val = 0
    for s in str.split(':'):
        val = val * 60 + int(s)
    return val

def parseMatchTR(tr):
    matchId = tr('td')[0].a['href'].split('/')[-1]
    firstWon = tr('td')[2].a['class'][0] == 'radiant'
    length = gameTime(tr('td')[3].text)
    date = datetime.datetime.strptime(tr('td')[0].time['datetime'], "%Y-%m-%dT%H:%M:%S+00:00")

    firstTeam = parseTeamTD(tr('td')[4])
    secondTeam = parseTeamTD(tr('td')[5])

    return {
        'matchId' : matchId,
        'firstTeam' : firstTeam,
        'secondTeam' : secondTeam,
        'firstTeamWon' : firstWon,
        'length' : length, 
        'date' : date,
    }

def teamForParsedTeam(parsedTeam, allowAdd):
    team = models.Team.query.filter_by(id = parsedTeam['id']).first()
    if team is None and allowAdd:
        team = models.Team(id = parsedTeam['id'], name = parsedTeam['name'])
        db.session.add(team)
        print bcolors.WARNING + 'Team added: %s' % (team.name) + bcolors.ENDC

    return team

def participantForTeam(match, team, won, parsedTeam):
    heroes = map(lambda heroId: models.Hero.query.filter_by(id = heroId).first(), parsedTeam['heroes'])
    participant = models.Participant(team_id = team.id, match_id = match.id, won = won, heroes = heroes)
    return participant


def parsePage(page):
    soup = matchesSoup(page)
    existedMatchFound = False
    for parsedMatch in map(parseMatchTR, soup('tr')[1:]):
        vsStr = parsedMatch['firstTeam']['name'] + " vs " + parsedMatch['secondTeam']['name']
        match = models.Match.query.filter_by(id = parsedMatch['matchId']).first()
        if match:
            print 'Match exists: %s' % (vsStr)
            existedMatchFound = True
            continue

        if parsedMatch['firstTeam']['id'] is None or parsedMatch['secondTeam']['id'] is None:
            print 'Unknown team(s) skipped'
            continue

        firstTeam = teamForParsedTeam(parsedMatch['firstTeam'], False)
        secondTeam = teamForParsedTeam(parsedMatch['secondTeam'], False)

        if (firstTeam is None or firstTeam.imageUrl is None) and (secondTeam is None or secondTeam.imageUrl is None):
            print 'Not top team(s) skipped'
            continue

        if firstTeam is None:
            firstTeam = teamForParsedTeam(parsedMatch['firstTeam'], True)
        if secondTeam is None:
            secondTeam = teamForParsedTeam(parsedMatch['secondTeam'], True)

        match = models.Match(id = parsedMatch['matchId'], length = parsedMatch['length'], date = parsedMatch['date'])
        db.session.add(match)

        participant = participantForTeam(match, firstTeam, parsedMatch['firstTeamWon'], parsedMatch['firstTeam'])
        db.session.add(participant)
        opParticipant = participantForTeam(match, secondTeam, not parsedMatch['firstTeamWon'], parsedMatch['secondTeam'])
        db.session.add(opParticipant)
        db.session.commit()
        print bcolors.OKGREEN + 'Match added: %s vs %s' % (firstTeam.name, secondTeam.name) + bcolors.ENDC

    return not existedMatchFound

def parseLastMatches():
    currentPage = 1
    while currentPage <= PAGES_COUNT:
        if not parsePage(currentPage):
            break
        currentPage += 1

if __name__ == "__main__":
    print bcolors.HEADER + 'Updating last matches' + bcolors.ENDC
    parseLastMatches()
