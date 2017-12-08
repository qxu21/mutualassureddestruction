import logging
from app import app, models, db
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
        if app.config['TESTING'] == True:
            num = 't{}'.format(game.id)
        else:
            num = game.id
        logger = logging.getLogger('update_logger_{}'.format(num))
        logger.setLevel(logging.DEBUG) #change to INFO on release
        handler = logging.FileHandler('game_log_{}.txt'.format(num))
        handler.setLevel(logging.DEBUG)
        log_formatter = logging.Formatter('UPDATE {}: %(message)s'.format(game.turn))
        handler.setFormatter(log_formatter)
        logger.addHandler(handler)
        rlogger = logging.getLogger('robotic_update_logger_{}'.format(num))
        rlogger.setLevel(logging.DEBUG) #change to INFO on release
        rhandler = logging.FileHandler('robotic_game_log_{}.txt'.format(num))
        rhandler.setLevel(logging.DEBUG)
        rlog_formatter = logging.Formatter('UPDATE {}: %(message)s'.format(game.turn))
        rhandler.setFormatter(rlog_formatter)
        rlogger.addHandler(rhandler)
        # now we can log with logger.info()
        game.turn += 1
        if game.turn == 1:
            game.phase = "Attack"
            db.session.add(game)
            continue
        shield_dict = {}
        for shield_action in Action.query.filter_by(game_id=game.id, type="shield", end_turn=game.turn).all():
            logger.info('{} deployed {} shields to protect {}'.format(
                shield_action.origin.name,
                shield_action.count,
                shield_action.dest.name))
            rlogger.info('{}x {} -| {}'.format(
                shield_action.count,
                shield_action.origin.name,
                shield_action.dest.name))
            if shield_action.dest_id not in shield_dict:
                shield_dict[shield_action.dest_id] = shield_action.count
            else:
                shield_dict[shield_action.dest_id] += shield_action.count
        rlogger.info("---")
        for plr in game.players:
            # this is getting out of hand, i'm doing too much logging, h e l p
            if plr.id not in shield_dict:
                rlogger.info('0x {} ||'.format(plr.name))
            else:
                rlogger.info('{}x {} ||'.format(shield_dict[plr.id], plr.name))
        rlogger.info("---")
        for fire_action in Action.query.filter_by(game_id=game.id, type="fire", end_turn=game.turn).all():
            logger.info('{} launched {} missiles at {}.'.format(
                fire_action.origin.name,
                fire_action.count,
                fire_action.dest.name))
            rlogger.info('{}x {} -> {}'.format(
                fire_action.count,
                fire_action.origin.name,
                fire_action.dest.name))
            if fire_action.dest_id not in shield_dict or shield_dict[fire_action.dest_id] <= 0: # < is protection against overflow
                # no shields or all shields depleted
                logger.info('No shields are protecting {} from {}: {} strikes were landed.'.format(
                    fire_action.dest.name,
                    fire_action.origin.name,
                    fire_action.count))
                rlogger.info('0x {} ||'.format(
                    fire_action.dest.name))
                rlogger.info('{}x {} -X {}'.format(
                    fire_action.count,
                    fire_action.origin.name,
                    fire_action.dest.name))
                fire_action.dest.destruction += fire_action.count
            elif shield_dict[fire_action.dest_id] >= fire_action.count:
                # enough shields to completely block attack
                rlogger.info('{}x {} ||'.format(
                    shield_dict[fire_action.dest_id],
                    fire_action.dest.name))
                shield_dict[fire_action.dest_id] -= fire_action.count
                logger.info('All the missiles that {} fired at {} were blocked by shields. {} shields remain on {}.'.format(
                    fire_action.origin.name,
                    fire_action.dest.name,
                    shield_dict[fire_action.dest_id],
                    fire_action.dest.name))
                rlogger.info('0x {} -X {}'.format(
                    fire_action.origin.name,
                    fire_action.dest.name))
                # rlogger wants to log before & after shieldcount, plus difference for fun
                rlogger.info('{}x {} -( {}'.format(
                    fire_action.count,
                    fire_action.origin.name,
                    fire_action.dest.name))
                rlogger.info('{}x {} ||'.format(
                    shield_dict[fire_action.dest_id],
                    fire_action.dest.name))
            elif shield_dict[fire_action.dest_id] < fire_action.count:
                # some shields, but not enough to block attack
                logger.info('{} of the missiles shot at {} by {} were blocked by shields. {} strikes were landed.'.format(
                    shield_dict[fire_action.dest_id],
                    fire_action.dest.name,
                    fire_action.origin.name,
                    fire_action.count - shield_dict[fire_action.dest_id]))
                rlogger.info('{}x {} ||'.format(
                    shield_dict[fire_action.dest_id],
                    fire_action.dest.name))
                rlogger.info('{}x {} -( {}'.format(
                    shield_dict[fire_action.dest_id],
                    fire_action.origin.name,
                    fire_action.dest.name))
                rlogger.info('{}x {} -X {}'.format(
                    fire_action.count - shield_dict[fire_action.dest_id],
                    fire_action.origin.name,
                    fire_action.dest.name))
                fire_action.dest.destruction += (fire_action.count - shield_dict[fire_action.dest_id])
                del shield_dict[fire_action.dest_id]
            rlogger.info('---')
            db.session.add(fire_action.dest)
        # reset to next turn and Attack phase
        for player in game.players:
            player.committed = False
            db.session.add(player)
        game.phase = "Attack"
        db.session.add(game)
    db.session.commit()

