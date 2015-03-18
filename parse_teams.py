#!env/bin/python
from app import db, models
import urllib2
import datetime, time
from bs4 import BeautifulSoup

url = "http://www.dotabuff.com/esports/teams"

def teamsSoup():
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    f = opener.open(url)
    html = f.read()
    f.close()
    return BeautifulSoup(html)

def parseTeams():
    soup = teamsSoup();
    for tr in soup.select('div[class~=tab-content]')[0]('tr')[1:]:
        if len(tr('td')) < 2 or tr('td')[1].a is None:
            continue
        teamId = int(tr('td')[1].a['href'].split('/')[-1])
        teamName = tr('td')[1].a.text.strip()
        imageUrl = tr('td')[0].img['src']

        team = models.Team.query.filter_by(id = teamId).first()
        if team is None:
            team = models.Team(id = teamId, name = teamName, imageUrl = imageUrl)
            db.session.add(team)
            db.session.commit()
            print 'Team added: %s' % teamName

if __name__ == "__main__":
    parseTeams()
