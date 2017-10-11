#!flask/bin/python
import unittest
import os

from config import basedir
from app import app, db, bcrypt
from app.models import User, Player, Game

class Tests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_user(self, username, password, email):
        user = User(username=username, password=bcrypt.generate_password_hash(password), email=email)
        db.session.add(user)
        db.session.commit()
        return user

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
        self.testuser = self.register_user("testuser1", "testpassword1", "testuser1@example.com")
        self.login_user("testuser1", "testpassword1")
        self.testgame = Game(id=1, turn=0, phase="Preliminary")
        db.session.add(self.testgame)
        db.session.commit()

    def test_join_game(self):
        self.app.get('/joingame/1')
        db.session.add(self.testgame)
        self.assertIsNotNone(Player.query.filter_by(
            user_id = self.testuser.id, 
            game_id = self.testgame.id).first())
        #assert that player attributes are not null
    

if __name__ == '__main__':
    unittest.main(verbosity=2)
  

