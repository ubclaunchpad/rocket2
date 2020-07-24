from app.controller.command.commands import TeamCommand
from unittest import TestCase, mock
from app.model import User, Team, Permissions
from tests.memorydb import MemoryDB
from tests.util import create_test_admin
from interface.exceptions.github import GithubAPIException
from flask import Flask


class TestTeamCommand(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.config = mock.MagicMock()
        self.gh = mock.MagicMock()

        self.u0 = User('U123456789')
        self.u1 = User('U234567891')
        self.admin = create_test_admin('Uadmin')
        self.t0 = Team("BRS", "brs", "web")
        self.t1 = Team("OTEAM", "other team", "android")
        self.db = MemoryDB(
            users=[self.u0, self.u1, self.admin],
            teams=[self.t0, self.t1])

        self.sc = mock.MagicMock()
        self.testcommand = TeamCommand(self.config, self.db, self.gh, self.sc)
        self.help_text = self.testcommand.help
        self.maxDiff = None

        self.config.github_team_all = 'all'

    def test_get_help(self):
        subcommands = list(self.testcommand.subparser.choices.keys())
        help_message = self.testcommand.get_help()
        self.assertEqual(len(subcommands), help_message.count("usage"))

    def test_get_subcommand_help(self):
        subcommands = list(self.testcommand.subparser.choices.keys())
        for subcommand in subcommands:
            help_message = self.testcommand.get_help(subcommand=subcommand)
            self.assertEqual(1, help_message.count("usage"))

    def test_get_invalid_subcommand_help(self):
        """Test team command get_help method for invalid subcommands."""
        self.assertEqual(self.testcommand.get_help(),
                         self.testcommand.get_help(subcommand="foo"))

    def test_handle_help(self):
        ret, code = self.testcommand.handle("team help", self.u0.slack_id)
        self.assertEqual(ret, self.testcommand.get_help())
        self.assertEqual(code, 200)

    def test_handle_multiple_subcommands(self):
        """Test handling multiple observed subcommands."""
        ret, code = self.testcommand.handle("team list edit",
                                            self.u0.slack_id)
        self.assertEqual(ret, self.testcommand.get_help())
        self.assertEqual(code, 200)

    def test_handle_subcommand_help(self):
        """Test team subcommand help text."""
        subcommands = list(self.testcommand.subparser.choices.keys())
        for subcommand in subcommands:
            for arg in ['--help', '-h', '--invalid argument']:
                command = f"team {subcommand} {arg}"
                ret, code = self.testcommand.handle(command, self.u0.slack_id)
                self.assertEqual(1, ret.count("usage"))
                self.assertEqual(code, 200)

    def test_handle_list(self):
        attachment = [
            self.t0.get_basic_attachment(),
            self.t1.get_basic_attachment()
        ]
        with self.app.app_context():
            resp, code = self.testcommand.handle('team list', self.u0.slack_id)
            expect = {'attachments': attachment}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_list_no_teams(self):
        self.db.teams = {}
        self.assertTupleEqual(self.testcommand.handle('team list',
                                                      self.u0.slack_id),
                              ('No Teams Exist!', 200))

    def test_handle_view(self):
        with self.app.app_context():
            resp, code = self.testcommand.handle('team view brs',
                                                 self.u0.slack_id)
            expect = {'attachments': [self.t0.get_attachment()]}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_view_lookup_error(self):
        self.assertTupleEqual(self.testcommand.handle('team view iesesebrs',
                                                      self.u0.slack_id),
                              (self.testcommand.lookup_error, 200))

    def test_handle_view_noleads(self):
        resp, code = self.testcommand.handle('team view brs',
                                             self.u0.slack_id)
        self.assertDictEqual(resp['attachments'][0], self.t0.get_attachment())
        self.assertEqual(code, 200)

    def test_handle_delete_not_admin(self):
        self.assertTupleEqual(self.testcommand.handle('team delete brs',
                                                      self.u0.slack_id),
                              (self.testcommand.permission_error, 200))
        self.gh.org_delete_team.assert_not_called()

    def test_handle_delete_lookup_error(self):
        self.assertTupleEqual(self.testcommand.handle('team delete brs',
                                                      'ioenairsetno'),
                              (self.testcommand.lookup_error, 200))
        self.gh.org_delete_team.assert_not_called()

    def test_handle_delete_github_error(self):
        self.t0.github_team_id = '123452'
        self.gh.org_delete_team.side_effect = GithubAPIException('error')
        self.assertTupleEqual(self.testcommand.handle('team delete brs',
                                                      self.admin.slack_id),
                              ('Team delete was unsuccessful with '
                               'the following error: '
                               'error', 200))

    def test_handle_delete(self):
        self.t0.github_team_id = '12345'
        self.u0.github_id = '132432'
        self.u0.permissions_level = Permissions.team_lead
        self.t0.add_team_lead(self.u0.github_id)
        self.assertTupleEqual(self.testcommand.handle('team delete brs',
                                                      self.u0.slack_id),
                              ('Team brs deleted', 200))
        self.gh.org_delete_team.assert_called_once_with(int('12345'))

    def test_handle_create(self):
        self.gh.org_create_team.return_value = '8934095'
        inputstring = "team create b-s --name 'B S'"
        outputstring = 'New team created: b-s, name: B S, '
        self.assertTupleEqual(self.testcommand.handle(inputstring,
                                                      self.admin.slack_id),
                              (outputstring, 200))
        inputstring += ' --platform web'
        outputstring += 'platform: web, '
        self.assertTupleEqual(self.testcommand.handle(inputstring,
                                                      self.admin.slack_id),
                              (outputstring, 200))
        self.gh.org_create_team.assert_called()
        self.gh.add_team_member.assert_called_with(
            self.admin.github_username,
            '8934095')

        inputstring += " --channel 'channelID'"
        outputstring += "added channel, "
        self.sc.get_channel_users.return_value = ['someID', 'otherID']
        self.assertTupleEqual(self.testcommand.handle(inputstring,
                                                      self.admin.slack_id),
                              (outputstring, 200))
        self.sc.get_channel_users.assert_called_once_with('channelID')
        self.gh.add_team_member.assert_called()
        inputstring += f' --lead {self.u0.slack_id}'
        outputstring += 'added lead'
        self.gh.has_team_member.return_value = False
        self.assertTupleEqual(self.testcommand.handle(inputstring,
                                                      self.admin.slack_id),
                              (outputstring, 200))

    def test_handle_create_not_admin(self):
        self.u0.github_username = 'githubuser'
        self.u0.github_id = '12'
        self.gh.org_create_team.return_value = 'team_id'
        inputstring = "team create b-s --name 'B S'"
        self.assertTupleEqual(self.testcommand.handle(inputstring,
                                                      self.u0.slack_id),
                              (self.testcommand.permission_error, 200))

    def test_handle_create_not_ghuser(self):
        self.u0.permissions_level = Permissions.admin
        self.gh.org_create_team.return_value = 'team_id'
        s = 'team create someting'
        ret, val = self.testcommand.handle(s, self.u0.slack_id)
        self.assertEqual(val, 200)
        self.assertIn('yet to register', ret)

    def test_handle_create_github_error(self):
        self.gh.org_create_team.return_value = 'team_id'
        inputstring = "team create b-s --name 'B S'"
        self.gh.add_team_member.side_effect = GithubAPIException('error')
        self.assertTupleEqual(self.testcommand.handle(inputstring,
                                                      self.admin.slack_id),
                              ('Team creation unsuccessful with the '
                               'following error: error', 200))

    def test_handle_create_lookup_error(self):
        inputstring = "team create b-s --name 'B S'"
        self.assertTupleEqual(self.testcommand.handle(inputstring, 'rando'),
                              (self.testcommand.lookup_error, 200))

    def test_handle_add(self):
        self.t0.github_team_id = 'githubid'
        self.u0.github_username = 'myuser'
        self.u0.github_id = 'otherID'
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                f'team add brs {self.u0.slack_id}',
                self.admin.slack_id)
            expect = {'attachments': [self.t0.get_attachment()],
                      'text': 'Added User to brs'}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertTrue(self.t0.has_member("otherID"))
        self.gh.add_team_member.assert_called_once_with('myuser', 'githubid')

    def test_handle_add_not_admin(self):
        """Test team command add parser with insufficient permission."""
        self.t0.github_team_id = 'githubid'
        self.assertTupleEqual(self.testcommand.handle(
            f'team add brs {self.u1.slack_id}',
            self.u0.slack_id),
                              (self.testcommand.permission_error, 200))
        self.gh.add_team_member.assert_not_called()

    def test_handle_add_github_error(self):
        self.t0.github_team_id = 'githubid'
        self.u0.github_username = 'myuser'
        self.gh.add_team_member.side_effect = GithubAPIException('error')
        self.assertTupleEqual(self.testcommand.handle(
            f'team add brs {self.u0.slack_id}',
            self.admin.slack_id),
                              ('User added unsuccessfully with the'
                               ' following error: error', 200))

    def test_handle_add_lookup_error(self):
        self.assertTupleEqual(self.testcommand.handle('team add brs ID',
                                                      'rando'),
                              (self.testcommand.lookup_error, 200))
        self.gh.add_team_member.assert_not_called()

    def test_handle_remove(self):
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        self.t0.add_member(self.u0.github_id)
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                self.admin.slack_id)
            expect = {'attachments': [self.t0.get_attachment()],
                      'text': f'Removed User from {self.t0.github_team_name}'}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.gh.remove_team_member.assert_called_once_with(
            self.u0.github_username,
            self.t0.github_team_id)

    def test_handle_remove_user_not_in_team(self):
        """Test team command remove parser when user is not in team."""
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        self.gh.has_team_member.return_value = False
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                self.admin.slack_id),
                                  ("User not in team!", 200))
        self.gh.has_team_member.assert_called_once_with(
            self.u0.github_username,
            self.t0.github_team_id)
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_not_admin(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                self.u1.slack_id),
                                  (self.testcommand.permission_error, 200))
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_lookup_error(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                'another.rando'),
                                  (self.testcommand.lookup_error, 200))
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_github_error(self):
        self.gh.has_team_member.side_effect = GithubAPIException('error')
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                self.admin.slack_id),
                                  ('User removed unsuccessfully with the '
                                   'following error: error', 200))
        self.gh.remove_team_member.assert_not_called()

    def test_handle_lead_add(self):
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        with self.app.app_context():
            self.assertFalse(self.t0.has_team_lead(self.u0.github_id))
            self.assertFalse(self.t0.has_member(self.u0.github_id))
            _, code = self.testcommand.handle(
                f'team lead {self.t0.github_team_name} {self.u0.slack_id}',
                self.admin.slack_id)
            self.assertEqual(code, 200)
            self.assertTrue(self.t0.has_team_lead(self.u0.github_id))
            self.assertTrue(self.t0.has_member(self.u0.github_id))
            self.gh.add_team_member.assert_called_once_with(
                self.u0.github_username,
                self.t0.github_team_id)

    def test_handle_lead_remove(self):
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        self.t0.add_member(self.u0.github_id)
        self.t0.add_team_lead(self.u0.github_id)
        with self.app.app_context():
            self.assertTrue(self.t0.has_team_lead(self.u0.github_id))
            _, code = self.testcommand.handle(
                f'team lead --remove {self.t0.github_team_name}'
                f' {self.u0.slack_id}',
                self.admin.slack_id)
            self.assertEqual(code, 200)
            self.assertFalse(self.t0.has_team_lead(self.u0.github_id))

    def test_handle_lead_not_admin(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team lead {self.t0.github_team_name} {self.u0.slack_id}',
                self.u1.slack_id),
                                  (self.testcommand.permission_error, 200))

    def test_handle_lead_lookup_error(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team lead {self.t0.github_team_name} {self.u0.slack_id}',
                'rando.rand'),
                                  (self.testcommand.lookup_error, 200))

    def test_handle_lead_github_error(self):
        self.gh.add_team_member.side_effect = GithubAPIException('error')
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team lead {self.t0.github_team_name} {self.u0.slack_id}',
                self.admin.slack_id),
                                  ('Edit team lead was unsuccessful with the '
                                   'following error: error', 200))

    def test_handle_lead_user_error(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team lead --remove {self.t0.github_team_name}'
                f' {self.u0.slack_id}',
                self.admin.slack_id),
                                  ('User not in team!', 200))

    def test_handle_edit(self):
        with self.app.app_context():
            _, code = self.testcommand.handle(
                f'team edit {self.t0.github_team_name}'
                ' --name brS --platform web',
                self.admin.slack_id)
            self.assertEqual(self.t0.display_name, 'brS')
            self.assertEqual(self.t0.platform, 'web')
            self.assertEqual(code, 200)

    def test_handle_edit_not_admin(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                f'team edit {self.t0.github_team_name}',
                self.u0.slack_id),
                                  (self.testcommand.permission_error, 200))

    def test_handle_edit_lookup_error(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle(
                'team edit rando.team',
                self.admin.slack_id),
                                  (self.testcommand.lookup_error, 200))

    def test_handle_refresh_not_admin(self):
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle('team refresh',
                                                          self.u0.slack_id),
                                  (self.testcommand.permission_error, 200))

    def test_handle_refresh_lookup_error(self):
        """Test team command refresh parser with lookup error."""
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle('team refresh',
                                                          'rando.randy'),
                                  (self.testcommand.lookup_error, 200))

    def test_handle_refresh_github_error(self):
        self.gh.org_get_teams.side_effect = GithubAPIException('error')
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle('team refresh',
                                                          self.admin.slack_id),
                                  ('Refresh teams was unsuccessful with '
                                   'the following error: error', 200))

    def test_handle_refresh_changed(self):
        """Test team command refresh parser if team edited in github."""
        team = Team('TeamID', 'TeamName', 'android')
        team_update = Team('TeamID', 'new team name', 'android')
        team_update.add_member(self.admin.github_id)
        team2 = Team('OTEAM', 'other team2', 'ios')

        self.db.teams = {}
        self.db.teams['TeamID'] = team
        self.db.teams['OTEAM'] = team2

        self.gh.org_get_teams.return_value = [team_update, team2]
        attach = team_update.get_attachment()

        status = '1 teams changed, 0 added, 0 deleted. Wonderful.'
        with self.app.app_context():
            resp, code = self.testcommand.handle('team refresh',
                                                 self.admin.slack_id)
            expect = {'attachments': [attach], 'text': status}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
            self.assertEqual(team, team_update)

    def test_handle_refresh_addition_and_deletion(self):
        """Test team command refresh parser if local differs from github."""
        team = Team('TeamID', 'TeamName', '')
        team2 = Team('OTEAM', 'other team', 'android')

        self.db.teams = {}
        self.db.teams['OTEAM'] = team2

        # In this case, github does not have team2!
        self.gh.org_get_teams.return_value = [team]
        self.gh.org_create_team.return_value = 12345
        attach = team.get_attachment()
        attach2 = team2.get_attachment()

        status = '0 teams changed, 1 added, 1 deleted. Wonderful.'
        with self.app.app_context():
            resp, code = self.testcommand.handle('team refresh',
                                                 self.admin.slack_id)
            expect = {'attachments': [attach2, attach], 'text': status}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
            self.assertEqual(len(self.db.teams), 2)
