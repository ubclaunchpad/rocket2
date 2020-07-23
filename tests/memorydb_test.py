from unittest import TestCase
from uuid import uuid4
from typing import Dict
import random
from tests.memorydb import MemoryDB
from app.model import User, Team  # , Project, Permissions
import tests.util as util


def makeUsers(amount: int = 20) -> Dict[str, User]:
    r = {}
    for _ in range(amount):
        u = User(str(uuid4()))
        u.github_username = u.slack_id
        r[u.slack_id] = u
    return r


def makeTeams() -> Dict[str, Team]:
    r = {}
    t0 = Team('t0', 'TZ', 'T Zero Blasters')
    t0.platform = 'iOS'
    t0.team_leads = set(['u0', 'u1', 'u2'])
    t0.members = set(['u0', 'u1', 'u2'])
    r['t0'] = t0
    t1 = Team('t1', 'T1', 'T 1 Blasters')
    t1.platform = 'iOS'
    t1.team_leads = set(['u0', 'u2'])
    t1.members = set(['u0', 'u2', 'u3'])
    r['t1'] = t1
    return r


class TestMemoryDB(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin = util.create_test_admin('Uadmin')
        self.users = makeUsers(20)
        self.users['Uadmin'] = self.admin
        self.teams = makeTeams()

    def setUp(self):
        self.db = MemoryDB(users=self.users, teams=self.teams)

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
            self.assertEqual(u.github_username,
                             self.users[slack_id].github_username)

    def testRetrieveNonexistantUser(self):
        with self.assertRaises(LookupError):
            self.db.retrieve(User, 'bad user bad bad')

    def testBulkRetrieve(self):
        selection = random.sample(list(self.users.keys()), k=10)
        us = self.db.bulk_retrieve(User, selection)
        self.assertEqual(len(us), 10)
        for u in us:
            self.assertEqual(u.github_username,
                             self.users[u.slack_id].github_username)

    def testBulkRetrieveNothing(self):
        selection = [str(i) for i in range(100)]
        us = self.db.bulk_retrieve(User, selection)
        self.assertEqual(us, [])

    def testQueryTeamName(self):
        ts = self.db.query(Team, [('github_team_name', 'T1')])
        self.assertEqual(len(ts), 1)
        self.assertEqual(ts[0], self.teams['t1'])

    def testQueryMultiParams(self):
        ts = self.db.query(
            Team,
            [('members', 'u0'), ('team_leads', 'u1')])
        self.assertEqual(len(ts), 1)
        self.assertEqual(ts[0], self.teams['t0'])

    def testQueryMultiTeams(self):
        ts = self.db.query(Team, [('members', 'u0')])
        self.assertCountEqual(ts, [self.teams['t0'], self.teams['t1']])

    def testScanQuery(self):
        us = self.db.query(User)
        self.assertCountEqual(us, list(self.users.values()))

    def testScanTeams(self):
        ts = self.db.query_or(Team)
        self.assertCountEqual(ts, list(self.teams.values()))

    def testBulkRetrieveUsingQuery(self):
        selection = random.sample(list(self.users.items()), k=10)
        rand_vals = [v for _, v in selection]
        q_string = [('slack_id', k) for k, _ in selection]
        us = self.db.query_or(User, q_string)
        self.assertCountEqual(us, rand_vals)
        self.assertEqual(len(us), 10)

    def testDeleteUser(self):
        slack_id = random.choice(list(self.users.keys()))
        self.db.delete(User, slack_id)
        with self.assertRaises(LookupError):
            self.db.retrieve(User, slack_id)
