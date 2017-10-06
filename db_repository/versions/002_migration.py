from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=64)),
    Column('email', String(length=120)),
)

player = Table('player', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('username', VARCHAR(length=64)),
    Column('email', VARCHAR(length=120)),
)

player = Table('player', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('type', Integer),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].create()
    pre_meta.tables['player'].columns['email'].drop()
    pre_meta.tables['player'].columns['username'].drop()
    post_meta.tables['player'].columns['type'].create()
    post_meta.tables['player'].columns['user_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].drop()
    pre_meta.tables['player'].columns['email'].create()
    pre_meta.tables['player'].columns['username'].create()
    post_meta.tables['player'].columns['type'].drop()
    post_meta.tables['player'].columns['user_id'].drop()
