from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.LargeBinary)
    email = db.Column(db.String(120), index=True, unique=True)
    players = db.relationship('Player', backref='user', lazy=True)

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
    
    #for fake users that can't login
    @property
    def is_anonymous(self):
        return False
    
    #return an id
    def get_id(self):
        try:
            return unicode(self.id) #i need this for py2
        except NameError:
            return str(self.id)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    name = db.Column(db.String(20))
    players = db.relationship('Player', backref='game', lazy=True)
    turn = db.Column(db.Integer)
    phase = db.Column(db.String(20))
    actions = db.relationship('Action', backref='game', lazy=True)

    def __repr__(self):
        return '<Game %r>' % (self.id)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    name = db.Column(db.String(30))
    type = db.Column(db.String(20))
    committed = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    attackpower = db.Column(db.Integer)
    defensepower = db.Column(db.Integer)
    destruction = db.Column(db.Integer) #maybe constrain to >= 100?
    def __repr__(self):
        return '<Player %r>' % (self.id)

#is this the best way to do this?
class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    origin = db.Column(db.Integer, db.ForeignKey('player.id'))
    dest = db.Column(db.Integer, db.ForeignKey('player.id'))
    start_turn = db.Column(db.Integer)
    end_turn = db.Column(db.Integer)
    count = db.Column(db.Integer)
    special = db.Column(db.String(200)) #contains json-dumped dicts, also remove constraint upon next change
