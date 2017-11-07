import logging
from app import models, db
from app.models import User, Player, Game, Action

#this is where the call stuff goes

def minor_update():
    # this will be primarily for espisonage powers who can see missiles in the air or targets
    # currently, just does a refresh to Defense phase
    for game in Game.query.all():
        game.phase = "Defense"
        for player in game.players:
            player.committed = False
            db.session.add(player)
        db.session.add(game)
    db.session.commit()

def major_update():
    for game in Game.query.all():
        logger = logging.getLogger('update_logger_{}'.format(game.id))
        logger.setLevel(logging.DEBUG) #change to INFO on release
        handler = logging.FileHandler('game_log_{}.txt'.format(game.id))
        handler.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter('UPDATE {}: %(message)s'.format(game.turn))
        handler.setFormatter(log_formatter)
        logger.addHandler(handler)
        # now we can log with logger.info()
        game.turn += 1
        if game.turn == 1:
            game.phase = "Attack"
            db.session.add(game)
            continue
        for fire_action in Action.query.filter_by(game_id=game.id, type="fire", end_turn=game.turn).all():
            logger.info('{} launched {} missiles at {}.'.format(fire_action.origin.name, fire_action.count, fire_action.dest.name))
            potential_shields =  Action.query.filter_by(game_id=game.id,type="shield", dest=fire_action.dest, end_turn=game.turn)
            shield_total = 0
            for shield_action in potential_shields:
                logger.info('{} deployed {} shields to protect {}.'.format(
                    shield_action.origin.name,
                    shield_action.count,
                    shield_action.dest.name))
                shield_total += shield_action.count
            strike_total = fire_action.count
            logger.info('In total, {} shields were deployed to protect {} from {}.'.format(shield_total, fire_action.dest.name, fire_action.origin.name))
            strike_total -= shield_total
            if strike_total < 0:
                strike_total = 0
            logger.info('{} landed {} missile strikes on {}.'.format(fire_action.origin.name, strike_total, fire_action.dest.name))
            fire_action.dest.destruction += strike_total
            db.session.add(fire_action.dest)
        # reset to next turn and Attack phase
        for player in game.players:
            player.committed = False
            db.session.add(player)
        game.phase = "Attack"
        db.session.add(game)
    db.session.commit()

