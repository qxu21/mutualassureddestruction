from flask import render_template, flash, redirect, url_for, session, request, g, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm #for the dynamic generation in console()
from wtforms import IntegerField
from app import app, db, lm, bcrypt
from .forms import LoginForm, RegisterForm, NewGameForm, JoinGameForm, ComposeMessageForm, StringField, IsInteger
from .models import User, Player, Game, Action, Message #i think this imports from within the app
from .helperfunctions import *
from itertools import islice
from datetime import datetime #these should probably go over flask imports

@app.before_request
def before_request():
    g.user = current_user

def int_404(p):
    try:
        return int(p)
    except:
        abort(404)

@app.route('/')
@app.route('/index')
def index():
    games = Game.query.all()
    return render_template('index.html', games=games)

@app.route('/login', methods=['GET','POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('games')) #no double logins
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
    form=RegisterForm()
    if form.validate_on_submit():
        #validate username
        #also validate email
        if User.query.filter_by(username=form.username.data).first():           
            #username was not unique, so bounce
            flash("This username already exists, pick a different one!")
            return redirect(url_for('register'))
        elif User.query.filter_by(email=form.email.data).first():
            #email not unique, bounce
            flash("This email is already in use!")
            return redirect(url_for('register'))
        else:
            newuser = User(username=form.username.data, email=form.email.data, password=bcrypt.generate_password_hash(form.password.data))
            db.session.add(newuser)
            db.session.commit()
            return redirect(url_for('login')) #potential for autologin: call login_user and redirectto games page
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
        gamelist.append((player.game, player))
    return render_template('games.html', games = gamelist)

@app.route('/joingames')
@login_required
def joingames():
    games = Game.query.all()
    return render_template('joingames.html', games=games)

@app.route('/game/<gameid>')
def gamepage(gameid):
    game_id = int_404(gameid)
    game = Game.query.get(game_id)
    player_in_game = Player.query.filter_by(user_id=current_user.id,
            game_id=game_id).first()
    #render chat or something
    return render_template('game.html', game=game, player_in_game = player_in_game)

@app.route('/joingame/<gameid>', methods=["GET","POST"])
@login_required
def joingame(gameid):
    game_id = int_404(gameid)
    form = JoinGameForm()
    if Player.query.filter_by(user_id=current_user.id, game_id=game_id).first():
        return redirect(url_for('gamepage', gameid = gameid))
    if form.validate_on_submit():
        game = Game.query.get(game_id)
        if Player.query.filter_by(user_id=current_user.id, game_id=game_id).first():
            return redirect(url_for('gamepage', gameid = game.id))
        newplayer = Player(
                number=len(game.players),
                name = form.playername.data, #scan for obscenities
                committed = False,
                user_id=current_user.id,
                game_id=game_id,
                type="Power",
                attackpower = 2,
                defensepower = 2,
                destruction = 0)
        game.players.append(newplayer)
        db.session.add(game)
        db.session.add(newplayer)
        db.session.commit()
        return redirect(url_for('gamepage', gameid=game.id))
    return render_template('joingame.html', form=form)

@app.route('/newgame', methods=["GET","POST"])
@login_required
def newgame():
    if current_user.username not in ("admin", "testuser1"):
        flash("Only the admin can make new games at this point.")
        return redirect(url_for('index'))
    form = NewGameForm()
    if form.validate_on_submit():
        if form.name.data in ("", None):
            name = "unnamed"
        else:
            name = form.name.data
        newgame = Game(
            name=name,
            type=form.gametype.data,
            turn=0,
            phase="Preliminary")
        db.session.add(newgame)
        db.session.commit()
        if form.nojoin.data == True and current_user.username == "admin":
            return redirect(url_for('joingames'))
        joingame(newgame.id) #oh boy I hope this works UPDATE: surprise surprise it failed
        return redirect(url_for('gamepage', gameid=newgame.id))
    return render_template('newgame.html', form=form)

@app.route('/messages/<gameid>', methods=["GET","POST"])
@login_required
def messages(gameid):
    game_id = int_404(gameid)
    game = Game.query.get(game_id)
    if game is None:
        abort(404)
    player = Player.query.filter_by(user_id = current_user.id, game_id = game_id).first()
    messages = player.inbox
    form = ComposeMessageForm()
    if form.validate_on_submit():
        destnames_wspace = form.dests.data.split(',')
        dests = []
        fail_name = None
        for x in destnames_wspace:
            potential_dest_name = x.strip() #strip whitespace
            potential_dest = Player.query.filter_by(name=potential_dest_name).first()
            if potential_dest is None:
                fail_name = potential_dest_name
            else:
                dests.append(potential_dest)
        if fail_name is not None:
            # redirects may wipe message bodies, so I'm going to deal with this later
            flash("{} is an invalid destination!".format(fail_name))
            return render_template('messages.html', game=game, player=player, messages=messages, form=form)
        message = Message(
                origin=player,
                origin_id=player.id,
                subject=(form.subject.data if form.subject.data not in ("", None) else "No Subject"),
                game_id=game.id,
                blind=form.blind.data,
                game=game,
                dests=dests,
                body=form.body.data)
        db.session.add(message)
        db.session.commit()
        flash("Message delivered!")
        return redirect(url_for("messages", gameid=gameid))
    return render_template('messages.html', game=game, player=player, messages=messages[::-1], form=form)
            



@app.route('/console/<gameid>', methods=["GET","POST"])
@login_required
def console(gameid):
    game_id = int_404(gameid)
    game = Game.query.get(game_id)
    if game is None:
        abort(404)
    player = Player.query.filter_by(game_id = game_id, user_id = current_user.id).first()
    if player is None or player not in game.players or player.committed == True:
        return redirect(url_for('gamepage', gameid=gameid))
    from flask_wtf import FlaskForm
    class ConsoleForm(FlaskForm):
        #i need this to create a form for all players dynamically
        #if a bunch of preconfigged stuff should go in here, drop it in forms.py and then inherit from it here
        pass
    for temp_player in game.players: #this may cause problems if a new player is added while the form is submitted. UPDATE: that's a nonissue sinece new players are added before console opens
        setattr(ConsoleForm, "target_player_%s" % str(temp_player.id), StringField("target_player_%s" % str(temp_player.id), validators=[IsInteger()]))
        setattr(ConsoleForm, "fire_player_%s" % str(temp_player.id), StringField("fire_player_%s" % str(temp_player.id), validators=[IsInteger()]))
    #if i have to do this again, make it a function
    form = ConsoleForm()
    if game.phase == "Attack" and form.validate_on_submit():
        #verify that the player has enough attack power and target power to support their commit
        target_total = 0
        fire_total = 0
        target_dict = {}
        fire_dict = {}
        for field in form:
            if field.name.startswith("target"):
                if field.data is "":
                    target_dict[int(field.name[-1])] = 0
                else:
                    target_dict[int(field.name[-1])] = int(field.data)
            elif field.name.startswith("fire"):
                if field.data is "":
                    fire_dict[int(field.name[-1])] = 0
                else:
                    fire_dict[int(field.name[-1])] = int(field.data)
        for value in target_dict.values():
            target_total += value
        for value in fire_dict.values():
            fire_total += value
        if target_total > player.attackpower * 1.5:
            flash("You tried to set %s targets but you can only set %s!" % (target_total, player.attackpower * 1.5))
            return redirect(url_for('console', gameid=gameid))
        if fire_total > player.attackpower:
            flash("You tried to fire %s missiles but you can only fire %s!" % (fire_total, player.attackpower))
            return redirect(url_for('console', gameid=gameid))
        #verify that all attacks were targeted last turn, unless it's turn 1
        for key, value in fire_dict.items():
            if value == 0:
                continue
            player_targeted = Player.query.get(key)
            potential_target = Action.query.filter_by(
                    origin_id = player.id,
                    dest_id = key,
                    origin = player,
                    dest = player_targeted,
                    end_turn = game.turn, #this will have to be made more complex if i ever support targets lasting for several turns
                    type = "target").first() #will have to change if target Actions ever start stacking for whatever reason
            if game.turn > 1 and (potential_target == None or potential_target.count <= 0):
                flash("You tried to fire missiles at {}, but you didn't set any targets on them last turn!".format(player_targeted.name))
                return redirect(url_for('console', gameid=gameid))
            if game.turn > 1 and potential_target.count < value:
                flash("You tried to fire {} missiles at {}, but you only set {} targets on them last turn!".format(value, player_targeted, potential_target.count))
                return redirect(url_for('console', gameid=gameid))
            #this is only for validating, the targets are swept later on
        #now it's time to create some Actions and commit them
        for key, value in target_dict.items():
            if value is not 0:
                db.session.add(Action(
                    type="target",
                    game_id=game.id,
                    origin_id=player.id,
                    dest_id=key,
                    origin=player,
                    dest=Player.query.get(key),
                    start_turn = game.turn,
                    end_turn = game.turn + 1,
                    count=value))
        for key, value in fire_dict.items():
            if value is not 0:
                db.session.add(Action(
                    type="fire",
                    game_id=game.id,
                    origin_id=player.id,
                    dest_id=key,
                    origin=player,
                    dest=Player.query.get(key),
                    start_turn = game.turn,
                    end_turn = game.turn + 1,
                    count=value))
        player.committed = True
        db.session.commit()
        flash("Your orders have been sent to the appropriate departments.")
        return redirect(url_for('gamepage', gameid = game_id))
        #unused targets will be swept by the update
    elif game.phase == "Defense" and form.validate_on_submit():
        #in this case, target_form holds shield fires
        shield_total = 0
        shield_dict = {}
        for field in form:
            if field.name.startswith("target"):
                if field.data is "":
                    shield_dict[int(field.name[-1])] = 0
                else:
                    shield_dict[int(field.name[-1])] = int(field.data)
        if shield_total > player.defensepower:
            flash("You tried to use {} shields, but you can only use {}!".format(shield_total, player.defensepower))
            return redirect(url_for('console'))
        for key, value in shield_dict.items():
            if value is not 0:
                db.session.add(Action(
                    type="shield",
                    game_id=game_id,
                    origin_id=player.id,
                    dest_id=key,
                    origin=player,
                    dest=Player.query.get(key),
                    start_turn=game.turn,
                    end_turn=game.turn + 1,
                    count=value))
        #wait, is that all i have to do for defense?!
        player.committed = True
        db.session.commit()
        return redirect(url_for('gamepage', gameid = game_id))
    target_form_fields = []
    fire_form_fields = []
    target_form_info = []
    fire_form_info = []
    for field in form:
        if field.name.startswith("target"):
            target_form_fields.append(field)
            target_form_info.append(None) # can be used to display stuff next to powers in the console
        elif field.name.startswith("fire"):
            fire_form_fields.append(field)
            potential_target = Action.query.filter_by(
                type="target",
                origin=player,
                dest_id=field.name[-1],
                end_turn=game.turn).first()
            fire_form_info.append("{} Targets".format((potential_target.count if potential_target is not None else 0))) 
    #target_form_fields = islice(target_form.__iter__(), 0, len(game.players))
    #fire_form_fields = islice(fire_form.__iter__(), 0, len(game.players))
    player_table_target = zip(game.players, target_form_fields, target_form_info)
    player_table_fire = zip(game.players, fire_form_fields, fire_form_info)
    return render_template('console.html', console_form=form, player=player, game=game, player_table_target=player_table_target, player_table_fire = player_table_fire)


@app.errorhandler(404)
def error_404(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def error_500(error):
    db.session.rollback()
    return render_template('500.html'), 500
#so this registers a user loader with flask-login
@lm.user_loader
def load_user(id):
    return User.query.get(int(id)) #convert to int from str
