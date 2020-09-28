from app.controller.command.commands import IQuitCommand
from app.model import User, Team, Permissions
from unittest import TestCase
from tests.memorydb import MemoryDB


def make_user(slack, gid, guser, perm):
    user = User(slack)
    user.github_id = gid
    user.github_username = guser
    user.permissions_level = perm
    return user


def make_team(ghid, leads_ghid, members_ghid):
    team = Team(ghid, 'COVID19', 'Crime Stoppers')
    team.team_leads = team.team_leads.union(leads_ghid)
    team.members = team.members.union(members_ghid)
    return team


class TestIQuitCommand(TestCase):
    def setUp(self):
        self.users = {
            'u1': make_user('u1', 'g1', 'G1', Permissions.admin),
            'u2': make_user('u2', 'g2', 'G2', Permissions.member),
            'u3': make_user('u3', 'g3', 'G3', Permissions.team_lead),
            'u4': make_user('u4', 'g4', 'G4', Permissions.team_lead),
            'u5': make_user('u5', 'g5', 'G5', Permissions.member),
            'u6': make_user('u6', 'g6', 'G6', Permissions.member)
        }
        self.teams = {
            't1': make_team('t1', [], []),
            't2': make_team('t2', ['g1', 'g3'], ['g1', 'g2', 'g3']),
            't3': make_team('t3', ['g1'], ['g1', 'g4', 'g2', 'g5', 'g6']),
            't4': make_team('t4', [], ['g6']),
            't6': make_team('t5', ['g4'], ['g5', 'g3'])
        }
        self.facade = MemoryDB(users=self.users.values(), teams=self.teams.values())
        self.cmd = IQuitCommand(self.facade)

    def test_get_no_duplicate_users(self):
        actual, resp = self.cmd.handle('', 'u2')
        self.assertEqual(actual.count('u1'), 1)
        self.assertEqual(actual.count('u3'), 1)

    def test_members_only_see_leads_n_admins(self):
        actual, resp = self.cmd.handle('', 'u6')
        self.assertEqual(actual.count('u1'), 1)
        self.assertNotEqual(actual.count('u2'), 1)
        self.assertNotEqual(actual.count('u3'), 1)
        self.assertNotEqual(actual.count('u6'), 1)

    def test_no_team_lead_so_return_nobody(self):
        actual, resp = self.cmd.handle('', 'u5')
        self.assertEqual(actual.count('u1'), 1)
        self.assertEqual(actual.count('u3'), 1)
        self.assertEqual(actual.count('u4'), 1)
        self.assertNotEqual(actual.count('u5'), 1)

    def test_cannot_find_caller(self):
        actual, resp = self.cmd.handle('', 'unknown user')
        self.assertEqual(actual, IQuitCommand.lookup_error)
        self.assertEqual(resp, 200)

    def test_call_as_team_lead(self):
        actual, resp = self.cmd.handle('', 'u4')
        self.assertTrue('replacing you with <@u5>' in actual or 'replacing you with <@u3>' in actual)
        self.assertEqual(actual.count('u1'), 1)
