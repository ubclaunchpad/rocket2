from unittest import TestCase
from uuid import uuid4
from typing import List
import random
from tests.memorydb import MemoryDB, field_to_attr
from app.model import User, Team
import tests.util as util


def makeUsers(amount: int = 20) -> List[User]:
    r = []
    for _ in range(amount):
        u = User(str(uuid4()))
        u.github_username = u.slack_id
        r.append(u)
    return r


def makeTeams() -> List[Team]:
    t0 = Team('t0', 'TZ', 'T Zero Blasters')
    t0.platform = 'iOS'
    t0.team_leads = set(['u0', 'u1', 'u2'])
    t0.members = set(['u0', 'u1', 'u2'])
    t1 = Team('t1', 'T1', 'T 1 Blasters')
    t1.platform = 'iOS'
    t1.team_leads = set(['u0', 'u2'])
    t1.members = set(['u0', 'u2', 'u3'])
    return [t0, t1]


class TestFieldToAttr(TestCase):
    def test_field_case(self):
        self.assertEqual(field_to_attr(TestFieldToAttr, 'some'),
                         'some')


class TestMemoryDB(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin = util.create_test_admin('Uadmin')
        self.users = {u.slack_id: u for u in makeUsers(20)}
        self.users['Uadmin'] = self.admin
        self.teams = {t.github_team_id: t for t in makeTeams()}

    def setUp(self):
        self.db = MemoryDB(users=list(self.users.values()),
                           teams=list(self.teams.values()))

    def test_get_db_lookup_error(self):
        with self.assertRaises(LookupError):
            self.db.get_db(TestMemoryDB)

    def test_users_dont_affect_DB(self):
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

    def test_store_valid_user(self):
        u = User('u3')
        self.assertTrue(self.db.store(u))

    def test_store_invalid_user(self):
        u = User('')
        self.assertFalse(self.db.store(u))

    def test_retrieve_users_randomly(self):
        ks = list(self.users.keys())
        for _ in range(10):
            slack_id = random.choice(ks)
            u = self.db.retrieve(User, slack_id)
            self.assertEqual(u.github_username,
                             self.users[slack_id].github_username)

    def test_retrieve_nonexistant_user(self):
        with self.assertRaises(LookupError):
            self.db.retrieve(User, 'bad user bad bad')

    def test_bulk_retrieve(self):
        selection = random.sample(list(self.users.keys()), k=10)
        us = self.db.bulk_retrieve(User, selection)
        self.assertEqual(len(us), 10)
        for u in us:
            self.assertEqual(u.github_username,
                             self.users[u.slack_id].github_username)

    def test_bulk_retrieve_nothing(self):
        selection = [str(i) for i in range(100)]
        us = self.db.bulk_retrieve(User, selection)
        self.assertEqual(us, [])

    def test_query_team_name(self):
        ts = self.db.query(Team, [('github_team_name', 'T1')])
        self.assertEqual(len(ts), 1)
        self.assertEqual(ts[0], self.teams['t1'])

    def test_query_multi_params(self):
        ts = self.db.query(
            Team,
            [('members', 'u0'), ('team_leads', 'u1')])
        self.assertEqual(len(ts), 1)
        self.assertEqual(ts[0], self.teams['t0'])

    def test_query_multi_teams(self):
        ts = self.db.query(Team, [('members', 'u0')])
        self.assertCountEqual(ts, [self.teams['t0'], self.teams['t1']])

    def test_scan_query(self):
        us = self.db.query(User)
        self.assertCountEqual(us, list(self.users.values()))

    def test_query_all_admins(self):
        admins = self.db.query(User, [('permission_level', 'admin')])
        self.assertIn(self.admin, admins)

    def test_scan_teams(self):
        ts = self.db.query_or(Team)
        self.assertCountEqual(ts, list(self.teams.values()))

    def test_bulk_retrieve_using_query(self):
        selection = random.sample(list(self.users.items()), k=10)
        rand_vals = [v for _, v in selection]
        q_string = [('slack_id', k) for k, _ in selection]
        us = self.db.query_or(User, q_string)
        self.assertCountEqual(us, rand_vals)
        self.assertEqual(len(us), 10)

    def test_delete_user(self):
        slack_id = random.choice(list(self.users.keys()))
        self.db.delete(User, slack_id)
        with self.assertRaises(LookupError):
            self.db.retrieve(User, slack_id)
