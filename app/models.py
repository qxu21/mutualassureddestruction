from app import db

message_table = db.Table("message_table",
        db.Column("message_id", db.Integer, db.ForeignKey("message.id")),
        db.Column("player_id", db.Integer, db.ForeignKey("player.id")))

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
    inbox = db.relationship("Message",
            secondary=message_table,
            back_populates="dests")
    outbox = db.relationship("Message", back_populates="origin")
    def __repr__(self):
        return '<Player %r>' % (self.name)

class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    origin_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    dest_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    origin = db.relationship("Player", foreign_keys=origin_id)
    dest = db.relationship("Player", foreign_keys=dest_id)
    start_turn = db.Column(db.Integer)
    end_turn = db.Column(db.Integer)
    count = db.Column(db.Integer)
    special = db.Column(db.String) # contains json-dumped dicts

    def __repr__(self):
        return "Action #{}: \
                Type: {} \
                game_id: {} \
                origin: {} \
                dest: {} \
                start_turn: {} \
                end_turn: {} \
                count: {}".format(self.id, self.type,self.game_id,self.origin,self.dest,self.start_turn,self.end_turn,self.count)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    subject = db.Column(db.String(50))
    body = db.Column(db.String)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    origin_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    parent = db.relationship("Message") # no backrefs, that's not needed yet
    origin = db.relationship("Player", back_populates="outbox", foreign_keys=origin_id)
    blind = db.Column(db.Boolean)
    dests = db.relationship("Player",
            secondary=message_table,
            back_populates="inbox")
    game = db.relationship("Game", backref="messages")

