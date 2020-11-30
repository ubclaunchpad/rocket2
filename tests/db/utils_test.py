from db.utils import get_team_members, get_users_by_ghid, get_team_by_name
from tests.memorydb import MemoryDB
from app.model import User, Team
from unittest import TestCase


class TestDbUtils(TestCase):
    def setUp(self):
        self.u0 = User('U395474')
        self.u0.github_id = '321132'
        self.u1 = User('U85739')
        self.u1.github_id = '000584'
        self.u2 = User('U3048485')
        self.u2.github_id = '11121'
        self.t0 = Team('305738', 'some-team', 'Some Team')
        self.t0.add_member(self.u0.github_id)
        self.t0.add_member(self.u1.github_id)
        self.t1 = Team('305849', 'some-team', 'Some Team')
        self.db = MemoryDB(users=[self.u0, self.u1, self.u2],
                           teams=[self.t0])

    def test_get_users_by_ghid_empty_list(self):
        self.assertEqual(get_users_by_ghid(self.db, []), [])

    def test_get_team_members(self):
        self.assertCountEqual(get_team_members(self.db, self.t0),
                              [self.u0, self.u1])

    def test_get_team_by_name_lots_of_teams_same_name(self):
        db = MemoryDB(teams=[self.t0, self.t1])
        with self.assertRaises(RuntimeError):
            get_team_by_name(db, 'some-team')

    def test_get_team_by_name_no_team_name(self):
        with self.assertRaises(LookupError):
            get_team_by_name(self.db, 'random-team')

    def test_get_users_by_ghid(self):
        self.assertCountEqual(
            get_users_by_ghid(self.db, [self.u0.github_id,
                                        self.u1.github_id,
                                        self.u2.github_id]),
            [self.u0, self.u1, self.u2])
