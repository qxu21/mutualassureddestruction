from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    players = db.relationship('Player', backref='user', lazy='dynamic')
    def __repr__(self):
        return '<User %r>' % (self.username)

    #is the user allowed to authenticate?
    @property
    def is_authenticated(self):
        return True
    
    #is the user active and unbanned?
    @property
    def is_active(self):
        return True
    
    #so apparently this is for fake users that can't login?
    @property
    def is_anonymous(self):
        return False
    
    #return an id
    def get_id(self):
        try:
            return unicode(self.id) #apparently i need this for py2
        except NameError:
            return str(self.id)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    players = db.relationship('Player', backref='game', lazy=True)
    turn = db.Column(db.Integer)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    def __repr__(self):
        return '<Player %r>' % (self.id)
