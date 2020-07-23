from unittest import TestCase
from uuid import uuid4
from typing import Dict
import random
from tests.memorydb import MemoryDB
from app.model import User  # , Team, Project, Permissions
import tests.util as util


def makeUsers(amount: int = 20) -> Dict[str, User]:
    r = {}
    for _ in range(amount):
        u = User(str(uuid4()))
        u.github_username = u.slack_id
        r[u.slack_id] = u
    return r


class TestMemoryDB(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = makeUsers(20)

    def setUp(self):
        self.admin = util.create_test_admin('Uadmin')
        self.db = MemoryDB(users=self.users)

    def testUsersDontAffectDB(self):
        """
        DB modifications shouldn't affect dict outside.

        Models themselves being modified are okay. But modifying the
        composition of the DB (which objects are in it) is not. This test makes
        sure that deleting a user from the DB does not delete it from the user
        dictionary.
        """
        slack_id = random.choice(list(self.users.keys()))
        self.db.users.pop(slack_id)
        self.assertIn(slack_id, self.users)

    def testStoreValidUser(self):
        u = User('u3')
        self.assertTrue(self.db.store(u))

    def testStoreInvalidUser(self):
        u = User('')
        self.assertFalse(self.db.store(u))

    def testRetrieveUsersRandomly(self):
        ks = list(self.users.keys())
        for _ in range(10):
            slack_id = random.choice(ks)
            u = self.db.retrieve(User, slack_id)
            self.assertEqual(u.github_username, slack_id)

    def testRetrieveNonexistantUser(self):
        with self.assertRaises(LookupError):
            self.db.retrieve(User, 'bad user bad bad')

    def testBulkRetrieve(self):
        selection = random.choices(list(self.users.keys()), k=10)
        us = self.db.bulk_retrieve(User, selection)
        self.assertEqual(len(us), 10)
        for u in us:
            self.assertEqual(u.github_username, u.slack_id)

    def testBulkRetrieveNothing(self):
        selection = [str(i) for i in range(100)]
        us = self.db.bulk_retrieve(User, selection)
        self.assertEqual(us, [])
