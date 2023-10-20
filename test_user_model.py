"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1=1111
        u1.id=uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2
    
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u2.following), 0)

        self.assertEqual(self.u2.followers[0].id, self.uid1)
        self.assertEqual(self.u1.following[0].id, self.uid2)

           
    def test_is_following(self):
        self.u1.following.append(self.u2) 
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.followers.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_followed_by(self.u2))
        self.assertFalse(self.u2.is_followed_by(self.u1))

    def test_valid_signup(self):
        u3 = User.signup("test3", "email3@email.com", "password", None)
        uid3=3333
        u3.id=uid3
        db.session.commit()

        u3 = User.query.get(uid3)
        self.assertIsNotNone(u3)
        self.assertEqual(u3.username, "test3")
        self.assertEqual(u3.email, "email3@email.com")
        self.assertNotEqual(u3.password, "password")
         # Bcrypt strings should start with $2b$
        self.assertTrue(u3.password.startswith("$2b$"))

    def test_invalid_username(self):
        invalid = User.signup(None, "email4@email.com", "password", None)
        uid=4444
        invalid.id=uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email(self):
        invalid = User.signup("TestName", None, "password", None)
        uid=4444
        invalid.id=uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        with self.assertRaises(ValueError) as context:
            User.signup("TestName", "Test@gmail.com", "", None)
      
        with self.assertRaises(ValueError) as context:
            User.signup("TestName", "Test@gmail.com", None, None)
    
    def test_duplicate_username(self):
        u1 = User.signup("Test", "email4@email.com", "password", None)
        uid=4444
        u1.id=uid
        db.session.commit()

        invalid = User.signup("Test", "emailtest@email.com", "password", None)
        uid=123
        invalid.id=uid

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_valid_authenticate(self):
        test_user = User.authenticate("test1", "password")
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate("test1", "badpassword"))
