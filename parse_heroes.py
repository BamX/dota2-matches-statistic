#!env/bin/python
from app import db, models
import urllib2
import re
from bs4 import BeautifulSoup

url = "http://www.dotabuff.com/heroes"

iconUrlRe = re.compile('background: url\(([^\)]*)\)')

def heroesSoup():
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    f = opener.open(url)
    html = f.read()
    f.close()
    return BeautifulSoup(html)

def parseHeroes():
    soup = heroesSoup();
    for div in soup.select('div[class~=hero]'):
        heroId = div.parent['href'].split('/')[-1]
        name = div.select('div[class~=name]')[0].text
        iconUrl = iconUrlRe.findall(div['style'])[0]
        hero = models.Hero.query.filter_by(id = heroId).first()
        if hero is None:
            hero = models.Hero(id = heroId, name = name, imageUrl = iconUrl)
            db.session.add(hero)
            db.session.commit()
            print 'Hero added: %s' % name

if __name__ == "__main__":
    parseHeroes()
