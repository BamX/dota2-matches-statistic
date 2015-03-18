from app import db

class Hero(db.Model):
    id = db.Column(db.String, primary_key = True)
    name = db.Column(db.String, index = True)
    imageUrl = db.Column(db.String)
    
    def __repr__(self):
        return '<Hero %r>' % (self.name)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, index = True)
    imageUrl = db.Column(db.String)
    participants = db.relationship('Participant', backref = 'team', lazy = 'dynamic')
    
    def __repr__(self):
        return '<Team %r>' % (self.name)

heroes = db.Table('heroes',
    db.Column('hero_id', db.String, db.ForeignKey('hero.id')),
    db.Column('match_participation_id', db.Integer, db.ForeignKey('participant.id'))
)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    heroes = db.relationship('Hero', secondary=heroes, backref=db.backref('participants', lazy='dynamic'))
    won = db.Column(db.Boolean)
    
    def __repr__(self):
        return '<Participant %r>' % (self.team_id)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    length = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    participants = db.relationship('Participant', backref = 'match', lazy = 'dynamic')

    def __repr__(self):
        return '<Match %r>' % (self.date)
