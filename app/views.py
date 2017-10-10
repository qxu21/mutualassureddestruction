from flask import render_template, flash, redirect, url_for, session, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, bcrypt
from .forms import LoginForm, RegisterForm
from .models import User, Player, Game #i think this imports from within the app
from itertools import islice

@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@app.route('/index')
def index():
    print('index page accessed')
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    #if g.user is not None and g.user.is_authenticated:
    #    return redirect(url_for('index')) #no double logins
    form=LoginForm()
    if form.validate_on_submit(): #so this is the backend processor, this'll be fun
        userdb = User.query.filter_by(username=form.username.data).first()
        if userdb and bcrypt.check_password_hash(userdb.password, form.password.data):
            login_user(userdb, remember = form.remember_me.data)
            return redirect(url_for('games'))
        else:
            flash("Username/password combo invalid!")
            return redirect(url_for('login'))
    return render_template('login.html',
            form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    #here goes nothin'
    print('beginning registration')
    form=RegisterForm()
    if form.validate_on_submit():
        print('form validated')
        #validate username
        #also validate email
        if User.query.filter_by(username=form.username.data).first():           
            #username was not unique, so bounce
            print('username or email not unique!')
            flash("This username already exists, pick a different one!")
            return redirect(url_for('register'))
        elif User.query.filter_by(email=form.email.data).first():
            #email not unique, bounce
            flash("This email is already in use!")
            return redirect(url_for('register'))
        else:
            print("user time!")
            print("Making user with username %s, email %s" % (form.username.data, form.email.data))
            newuser = User(username=form.username.data, email=form.email.data, password=bcrypt.generate_password_hash(form.password.data))
            db.session.add(newuser)
            db.session.commit()
            return redirect(url_for('login')) #potential for autologin: call login_user and redirectto games page
    print("rendering form")
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/games')
@login_required
def games():
    gamelist = []
    for player in current_user.players:
        gamelist.append(player.game)
    return render_template('games.html', games = gamelist)

@app.route('/joingames')
@login_required
def joingames():
    games = Game.query.all()
    return render_template('joingames.html', games=games)

@app.route('/game/<gameid>')
def gamepage(gameid):
    game = Game.query.get(int(gameid))
    #render chat or something
    return render_template('game.html', game=game)

#@app.route('/confirmjoin/<gameid>')
@login_required
def confirmjoin(gameid):
    #this function is currently unimplemented
    game = Game.query.get(int(gameid))
    if player in games.players:
        return redirect(url_for('gamepage', gameid = gameid))
    return render_template('confirmjoin.html', gameid = gameid)

@app.route('/joingame/<gameid>')
@login_required
def joingame(gameid):
    #if not g.join_confirmed:
    #    return redirect(url_for('confirmjoin', gameid=gameid))
    game = Game.query.get(int(gameid))
    if Player.query.filter_by(user_id=current_user.id, game_id=game.id).first():
        return redirect(url_for('game', gameid = game.id))
    newplayer = Player(user_id=current_user.id, game_id=int(gameid))
    game.players.append(newplayer)
    db.session.add(game)
    db.session.add(newplayer)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/console/<gameid>')
@login_required
def console(gameid):
    current_player = Player.query.filter_by(user_id = current_user.id, game_id = int(gameid)).first()
    game = Game.query.get(int(gameid))
    #oh god why do i have imports *here* is this even legal
    from flask_wtf import FlaskForm
    from wtforms import IntegerField
    class ConsoleForm(FlaskForm):
        #i need this to create a form for all players dynamically
        pass
    for player in game.players:
        #if player is current_player:
        #    setattr(ConsoleForm, "player_%s" % str(player.id), None) 
        setattr(ConsoleForm, "player_%s" % str(player.id), IntegerField("player_%s" % str(player.id)))
    #if i have to do this again, make it a function
    target_form = ConsoleForm()
    fire_form = ConsoleForm()
    target_form_fields = islice(target_form.__iter__(), 0, len(game.players))
    fire_form_fields = islice(fire_form.__iter__(), 0, len(game.players))
    player_table_target = zip(game.players, target_form_fields)
    player_table_fire = zip(game.players, fire_form_fields)
    print('test rendering player_table:')
    return render_template('console.html', player=current_player, game=game, target_form=target_form, fire_form = fire_form, player_table_target=player_table_target, player_table_fire = player_table_fire)

#so this registers a user loader with flask-login
@lm.user_loader
def load_user(id):
    return User.query.get(int(id)) #convert to int from str
