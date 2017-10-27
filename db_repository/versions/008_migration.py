from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
action = Table('action', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('type', String),
    Column('origin', Integer),
    Column('dest', Integer),
    Column('start_turn', Integer),
    Column('end_turn', Integer),
    Column('count', Integer),
    Column('special', String(length='500')),
)

player = Table('player', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('type', Integer),
    Column('user_id', Integer),
    Column('game_id', Integer),
    Column('attackpower', Integer),
    Column('defensepower', Integer),
    Column('destruction', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['action'].create()
    post_meta.tables['player'].columns['attackpower'].create()
    post_meta.tables['player'].columns['defensepower'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['action'].drop()
    post_meta.tables['player'].columns['attackpower'].drop()
    post_meta.tables['player'].columns['defensepower'].drop()
