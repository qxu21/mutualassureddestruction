#!flask/bin/python
import unittest
import os

from config import basedir
from app import app, db, bcrypt
from app.models import User, Player, Game, Action
from update import minor_update, major_update

class Tests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mutualassureddestruction_test'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self, username, password, email):
        return self.app.post('/register', data=dict(
            username = username,
            password=password,
            email=email))

    def login_user(self, username, password):
        return self.app.post('/login', data=dict(
            username = username,
            password = password), follow_redirects=True)

class RegisterTest(Tests):
    def test_user_creation(self):
        registerattempt = self.app.post('/register', data=dict(
            username = "testuser1",
            password = "testpassword1",
            email = "testuser1@example.com"), follow_redirects=True)
        testuser1 = User.query.filter_by(username="testuser1").first()
        self.assertIsNotNone(testuser1) # assert uername existence
        self.assertEqual(testuser1.email, "testuser1@example.com") # assert email existence
        self.assertTrue(bcrypt.check_password_hash(testuser1.password, "testpassword1")) # assert password existence

class LoginTest(Tests):
    def test_user_login(self):
        self.register_user("testuser1", "testpassword1", "testuser1@example.com")
        loginattempt = self.login_user("testuser1", "testpassword1")
        self.assertIn(b'Hello, testuser1', loginattempt.data) #is there a better way to assert this?

class UserTests(Tests):
    def setUp(self):
        super().setUp()
        self.register_user("testuser1", "testpassword1", "testuser1@example.com")
        self.login_user("testuser1", "testpassword1")

    def test_new_and_join_game(self):
        self.app.post('/newgame', data=dict(
            name = "testgame1",
            gametype="beta"))
        self.assertIsNotNone(Game.query.first())
        self.app.post('/joingame/1', data=dict(
            playername = "testplayer1"))
        player = Player.query.first()
        self.assertIsNotNone(player)
        self.assertEqual(player.name, "testplayer1")
        self.assertEqual(player.user.username, "testuser1")
        #assert that player attributes are not null
    
class ConsoleTests(Tests):
    def setUp(self):
        super().setUp()
        for x in range(1,5):
            self.register_user("testuser{}".format(x), "testpassword{}".format(x), "testuser{}@example.com".format(x))
        self.login_user("testuser1", "testpassword1")
        self.app.post('/newgame', data=dict(
            name="testgame1",
            gametype="beta"))
        self.app.get('/logout')
        for x in range(1,5):
            self.login_user("testuser{}".format(x), "testpassword{}".format(x))
            self.app.post('/joingame/1', data=dict(
                playername = "testplayer{}".format(x)))
            self.app.get('/logout')
        game = Game.query.first()
        game.phase = "Attack"
        db.session.add(game)
        db.session.commit()
        self.login_user("testuser1", "testpassword1")

    def test_noninteger_input(self):
        submission = self.app.post('/console/1', data=dict(
            target_player_1="x"), follow_redirects=True)
        self.assertIn(b'Positive integer needed!', submission.data)
        submission2 = self.app.post('/console/1', data=dict(
            fire_player_2="x"), follow_redirects=True)
        self.assertIn(b'Positive integer needed!', submission2.data)
        

    def test_high_input(self):
        submission = self.app.post('/console/1', data=dict(
            target_player_2="10000"), follow_redirects=True)
        self.assertIn(b'You tried to set 10000 targets', submission.data)
        submission2 = self.app.post('/console/1', data=dict(
            fire_player_2="10000"), follow_redirects=True)
        self.assertIn(b'You tried to fire 10000 missiles', submission2.data)

    def test_attack_commit(self):
        submission = self.app.post('/console/1', data=dict(
            target_player_1="1",
            target_player_2="1",
            fire_player_1="1",
            fire_player_2="1"), follow_redirects=True)
        for action in Action.query.all():
            if action.type in ("fire", "target"):
                self.assertEqual(action.origin.name, "testplayer1")
                self.assertEqual(action.count, 1)
                self.assertEqual(action.start_turn, 0)
                self.assertEqual(action.end_turn, 1)
                self.assertIn(action.dest.name, ("testplayer1", "testplayer2"))

class UpdateTests(Tests):
    def setUp(self):
        super().setUp()
        for w in range(1, 5):
            db.session.add(User(
                id=w,
                username="testuser{}".format(w),
                email="testuser{}@example.com".format(w)))
            # beware, they have no passwords, don't try logging in
        db.session.commit()
        for x in range(1, 3):
            game = Game(
                id=x,
                name="testgame{}".format(x),
                type="Beta",
                turn=0,
                phase="Preliminary")
            db.session.add(game)
            db.session.commit()
            for y in range(1, 5):
                user = User.query.filter_by(username="testuser{}".format(y)).first()
                self.assertIsNotNone(user)
                player = Player(
                    number=y,
                    name="testplayer{}".format(y),
                    committed=False,
                    user_id=user.id,
                    game_id=game.id,
                    type="Power",
                    attackpower = 2,
                    defensepower = 2,
                    destruction = 0)
                game.players.append(player)
                db.session.add(player)
            db.session.add(game)
            db.session.commit()

    def test_one_turn(self):
        game = Game.query.get(1)
        # no use testing targets since those are taken care of by the console
        # 2x 1 -> 2
        # 2x 3 -> 2
        # 2x 2 -> 3
        # 2x 1 -| 2
        # 1x 3 -| 2
        # ->
        # 1x -X 2
        # 2x -X 3
        # hey look this helped me write rlogger
        game.turn = 1
        db.session.add(game)
        db.session.add(Action(
            type="fire",
            game_id=1,
            origin_id=1,
            dest_id=2,
            start_turn=game.turn,
            end_turn=game.turn+1,
            count=2))
        db.session.add(Action(
            type="fire",
            game_id=1,
            origin_id=3,
            dest_id=2,
            start_turn=game.turn,
            end_turn=game.turn+1,
            count=2))
        db.session.add(Action(
            type="fire",
            game_id=1,
            origin_id=2,
            dest_id=3,
            start_turn=game.turn,
            end_turn=game.turn+1,
            count=2))
        db.session.add(Action(
            type="shield",
            game_id=1,
            origin_id=1,
            dest_id=2,
            start_turn=game.turn,
            end_turn=game.turn + 1,
            count=2))
        db.session.add(Action(
            type="shield",
            game_id=1,
            origin_id=3,
            dest_id=2,
            start_turn=game.turn,
            end_turn=game.turn + 1,
            count=1))
        db.session.commit()
        major_update()
        self.assertEqual(Player.query.get(2).destruction, 1)
        self.assertEqual(Player.query.get(3).destruction, 2)



                







if __name__ == '__main__':
    unittest.main(verbosity=2)
  

