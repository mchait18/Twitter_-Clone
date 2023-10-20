"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes

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

        db.session.commit()

        self.u1 = u1
        self.uid1 = uid1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="Message 1",
            user_id=self.uid1,
        )

        db.session.add(m)
        db.session.commit()

        # user should have 1 messgage
        self.assertEqual(len(self.u1.messages), 1)
        self.assertEqual(self.u1.messages[0].text, "Message 1")
        self.assertEqual(m.user, self.u1)
        
    def test_message_likes(self):
        """testing likes functionality"""
        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2=2222
        u2.id=uid2

        m = Message(text="Message 1", user_id=self.uid1)

        db.session.add(m)
        db.session.commit()
        u2.likes.append(m)
        db.session.commit()   
        
        l = Likes.query.filter(Likes.user_id == uid2).all()

        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m.id)
        