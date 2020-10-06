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
        self.t2 = Team("LEADS", "leads", "")
        self.t3 = Team("ADMIN", "admin", "")
        self.db = MemoryDB(
            users=[self.u0, self.u1, self.admin],
            teams=[self.t0, self.t1, self.t2, self.t3])

        self.sc = mock.MagicMock()
        self.cmd = TeamCommand(self.config, self.db, self.gh, self.sc)
        self.help_text = self.cmd.help
        self.maxDiff = None

        self.config.github_team_all = 'all'
        self.config.github_team_leads = 'leads'
        self.config.github_team_admin = 'admin'

    def test_get_help(self):
        subcommands = list(self.cmd.subparser.choices.keys())
        help_message = self.cmd.get_help()
        self.assertEqual(len(subcommands), help_message.count("usage"))

    def test_get_subcommand_help(self):
        subcommands = list(self.cmd.subparser.choices.keys())
        for subcommand in subcommands:
            help_message = self.cmd.get_help(subcommand=subcommand)
            self.assertEqual(1, help_message.count("usage"))

    def test_get_invalid_subcommand_help(self):
        """Test team command get_help method for invalid subcommands."""
        self.assertEqual(self.cmd.get_help(),
                         self.cmd.get_help(subcommand="foo"))

    def test_handle_help(self):
        ret, code = self.cmd.handle("team help", self.u0.slack_id)
        self.assertEqual(ret, self.cmd.get_help())
        self.assertEqual(code, 200)

    def test_handle_multiple_subcommands(self):
        """Test handling multiple observed subcommands."""
        ret, code = self.cmd.handle("team list edit",
                                    self.u0.slack_id)
        self.assertEqual(ret, self.cmd.get_help())
        self.assertEqual(code, 200)

    def test_handle_subcommand_help(self):
        """Test team subcommand help text."""
        subcommands = list(self.cmd.subparser.choices.keys())
        for subcommand in subcommands:
            for arg in ['--help', '-h', '--invalid argument']:
                command = f"team {subcommand} {arg}"
                ret, code = self.cmd.handle(command, self.u0.slack_id)
                self.assertEqual(1, ret.count("usage"))
                self.assertEqual(code, 200)

    def test_handle_list(self):
        attachments = [
            self.t0.get_basic_attachment(),
            self.t1.get_basic_attachment(),
            self.t2.get_basic_attachment(),
            self.t3.get_basic_attachment(),
        ]
        with self.app.app_context():
            resp, code = self.cmd.handle('team list', self.u0.slack_id)
            self.assertCountEqual(resp['attachments'], attachments)
            self.assertEqual(code, 200)

    def test_handle_list_no_teams(self):
        self.db.teams = {}
        self.assertTupleEqual(self.cmd.handle('team list',
                                              self.u0.slack_id),
                              ('No Teams Exist!', 200))

    def test_handle_view(self):
        with self.app.app_context():
            resp, code = self.cmd.handle('team view brs',
                                         self.u0.slack_id)
            expect = {'attachments': [self.t0.get_attachment()]}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_view_lookup_error(self):
        self.assertTupleEqual(self.cmd.handle('team view iesesebrs',
                                              self.u0.slack_id),
                              (self.cmd.lookup_error, 200))

    def test_handle_view_noleads(self):
        resp, code = self.cmd.handle('team view brs',
                                     self.u0.slack_id)
        self.assertDictEqual(resp['attachments'][0], self.t0.get_attachment())
        self.assertEqual(code, 200)

    def test_handle_delete_not_admin(self):
        self.assertTupleEqual(self.cmd.handle('team delete brs',
                                              self.u0.slack_id),
                              (self.cmd.permission_error, 200))
        self.gh.org_delete_team.assert_not_called()

    def test_handle_delete_lookup_error(self):
        self.assertTupleEqual(self.cmd.handle('team delete brs',
                                              'ioenairsetno'),
                              (self.cmd.lookup_error, 200))
        self.gh.org_delete_team.assert_not_called()

    def test_handle_delete_github_error(self):
        self.t0.github_team_id = '123452'
        self.gh.org_delete_team.side_effect = GithubAPIException('error')
        self.assertTupleEqual(self.cmd.handle('team delete brs',
                                              self.admin.slack_id),
                              ('Team delete was unsuccessful with '
                               'the following error: '
                               'error', 200))

    def test_handle_delete(self):
        self.t0.github_team_id = '12345'
        self.u0.github_id = '132432'
        self.u0.permissions_level = Permissions.team_lead
        self.t0.add_team_lead(self.u0.github_id)
        self.assertTupleEqual(self.cmd.handle('team delete brs',
                                              self.u0.slack_id),
                              ('Team brs deleted', 200))
        self.gh.org_delete_team.assert_called_once_with(int('12345'))

    def test_handle_create(self):
        inputstring = "team create b-s --name 'B S'"
        inputstring += ' --platform web'
        inputstring += " --channel 'channelID'"
        inputstring += f' --lead {self.u0.slack_id}'
        tid = '8934095'

        self.u0.github_id = '093293124'
        self.u0.github_username = 'someperson'

        self.sc.get_channel_users.return_value = [self.u0.slack_id]

        self.gh.org_create_team.return_value = int(tid)
        self.gh.has_team_member.return_value = False

        self.cmd.handle(inputstring, self.admin.slack_id)

        # The new team must be retrieved
        team: Team = self.db.retrieve(Team, tid)
        self.assertEqual(team.github_team_name, 'b-s')
        self.assertEqual(team.display_name, 'B S')
        self.assertEqual(team.platform, 'web')
        self.assertSetEqual(team.members, set([self.u0.github_id]))
        self.assertSetEqual(team.team_leads, set([self.u0.github_id]))

    def test_handle_create_no_gh_for_users_in_channel(self):
        self.gh.org_create_team.return_value = 8934095
        inputstring = "team create b-s --name 'B S'"

        self.gh.add_team_member.side_effect = GithubAPIException('bad')
        inputstring += " --channel 'channelID'"
        self.sc.get_channel_users.return_value = ['U123456789', 'U234567891']
        ret, code = self.cmd.handle(inputstring, self.admin.slack_id)
        self.assertIn('U123456789', ret)
        self.assertIn('U234567891', ret)

    def test_handle_create_not_admin(self):
        self.u0.github_username = 'githubuser'
        self.u0.github_id = '12'
        self.gh.org_create_team.return_value = 93048304
        inputstring = "team create b-s --name 'B S'"
        self.assertTupleEqual(self.cmd.handle(inputstring,
                                              self.u0.slack_id),
                              (self.cmd.permission_error, 200))

    def test_handle_create_not_ghuser(self):
        self.u0.permissions_level = Permissions.admin
        self.gh.org_create_team.return_value = 3930483
        s = 'team create someting'
        ret, val = self.cmd.handle(s, self.u0.slack_id)
        self.assertEqual(val, 200)
        self.assertIn('yet to register', ret)

    def test_handle_create_github_error(self):
        self.gh.org_create_team.return_value = 302084
        inputstring = "team create b-s --name 'B S'"
        self.gh.add_team_member.side_effect = GithubAPIException('error')
        self.assertTupleEqual(self.cmd.handle(inputstring,
                                              self.admin.slack_id),
                              ('Team creation unsuccessful with the '
                               'following error: error', 200))

    def test_handle_create_lookup_error(self):
        inputstring = "team create b-s --name 'B S'"
        self.assertTupleEqual(self.cmd.handle(inputstring, 'rando'),
                              (self.cmd.lookup_error, 200))

    def test_handle_add(self):
        self.t0.github_team_id = 'githubid'
        self.u0.github_username = 'myuser'
        self.u0.github_id = 'otherID'
        with self.app.app_context():
            resp, code = self.cmd.handle(
                f'team add brs {self.u0.slack_id}',
                self.admin.slack_id)
            expect = {'attachments': [self.t0.get_attachment()],
                      'text': 'Added User to brs'}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertTrue(self.t0.has_member("otherID"))
        self.gh.add_team_member.assert_called_once_with('myuser', 'githubid')

    def test_handle_add_but_forgot_githubid(self):
        self.t0.github_team_id = 'githubid'
        self.gh.add_team_member.side_effect = GithubAPIException('error')
        res = self.cmd.handle(f'team add brs {self.u0.slack_id}',
                              self.admin.slack_id)
        self.assertTupleEqual(res, (TeamCommand.no_ghusername_error, 200))

    def test_handle_add_not_admin(self):
        """Test team command add parser with insufficient permission."""
        self.t0.github_team_id = 'githubid'
        res = self.cmd.handle(f'team add brs {self.u1.slack_id}',
                              self.u0.slack_id)
        self.assertTupleEqual(res, (self.cmd.permission_error, 200))
        self.gh.add_team_member.assert_not_called()

    def test_handle_add_github_error(self):
        self.t0.github_team_id = 'githubid'
        self.u0.github_id = 'myuser'
        self.gh.add_team_member.side_effect = GithubAPIException('error')
        res = self.cmd.handle(f'team add brs {self.u0.slack_id}',
                              self.admin.slack_id)
        self.assertTupleEqual(res,
                              ('User added unsuccessfully with the'
                               ' following error: error', 200))

    def test_handle_add_lookup_error(self):
        res = self.cmd.handle('team add brs ID', 'randomID')
        self.assertTupleEqual(res, (self.cmd.lookup_error, 200))
        self.gh.add_team_member.assert_not_called()

    def test_handle_add_promote(self):
        self.u0.github_username = 'myuser'
        self.u0.github_id = 'otherID'
        self.t2.github_team_id = 'githubid'
        with self.app.app_context():
            resp, code = self.cmd.handle(
                f'team add leads {self.u0.slack_id}',
                self.admin.slack_id)
            expect_msg = 'Added User to leads and promoted user to team_lead'
            expect = {'attachments': [self.t2.get_attachment()],
                      'text': expect_msg}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertTrue(self.t2.has_member('otherID'))
        self.assertEqual(self.u0.permissions_level, Permissions.team_lead)
        self.gh.add_team_member.assert_called_once_with('myuser', 'githubid')

    def test_handle_add_promote_current_admin(self):
        self.u0.github_username = 'myuser'
        self.u0.github_id = 'otherID'
        self.t2.github_team_id = 'githubid'
        # existing admin member should not be "promoted" to lead
        self.u0.permissions_level = Permissions.admin
        self.t3.add_member(self.u0.github_id)
        with self.app.app_context():
            resp, code = self.cmd.handle(
                f'team add leads {self.u0.slack_id}',
                self.admin.slack_id)
            expect_msg = 'Added User to leads'
            expect = {'attachments': [self.t2.get_attachment()],
                      'text': expect_msg}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertTrue(self.t2.has_member('otherID'))
        self.assertEqual(self.u0.permissions_level, Permissions.admin)
        self.gh.add_team_member.assert_called_once_with('myuser', 'githubid')

    def test_handle_remove(self):
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        self.t0.add_member(self.u0.github_id)
        with self.app.app_context():
            resp, code = self.cmd.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                self.admin.slack_id)
            expect = {'attachments': [self.t0.get_attachment()],
                      'text': f'Removed User from {self.t0.github_team_name}'}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertFalse(self.t0.has_member(self.u0.github_id))
        self.gh.remove_team_member.assert_called_once_with(
            self.u0.github_username,
            self.t0.github_team_id)

    def test_handle_remove_user_not_in_team(self):
        """Test team command remove parser when user is not in team."""
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        self.gh.has_team_member.return_value = False
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                self.admin.slack_id),
                                  ('User not in team!', 200))
        self.gh.has_team_member.assert_called_once_with(
            self.u0.github_username,
            self.t0.github_team_id)
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_demote_team_lead_to_user(self):
        self.u0.github_username = 'myuser'
        self.u0.github_id = 'otherID'
        self.t2.add_member(self.u0.github_id)
        with self.app.app_context():
            resp, code = self.cmd.handle(
                f'team remove leads {self.u0.slack_id}',
                self.admin.slack_id)
            expect_msg = 'Removed User from leads and demoted user'
            expect = {'attachments': [self.t2.get_attachment()],
                      'text': expect_msg}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertEqual(self.u0.permissions_level, Permissions.member)
        self.gh.remove_team_member.assert_called_once_with(
            self.u0.github_username,
            self.t2.github_team_id)

    def test_handle_remove_demote_admin_to_team_lead(self):
        self.u0.github_username = 'myuser'
        self.u0.github_id = 'otherID'
        self.t2.add_member(self.u0.github_id)
        self.t3.add_member(self.u0.github_id)
        with self.app.app_context():
            resp, code = self.cmd.handle(
                f'team remove admin {self.u0.slack_id}',
                self.admin.slack_id)
            expect_msg = 'Removed User from admin and demoted user'
            expect = {'attachments': [self.t3.get_attachment()],
                      'text': expect_msg}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertEqual(self.u0.permissions_level, Permissions.team_lead)
        self.gh.remove_team_member.assert_called_once_with(
            self.u0.github_username,
            self.t3.github_team_id)

    def test_handle_remove_team_lead_but_user_is_admin(self):
        self.u0.github_username = 'myuser'
        self.u0.github_id = 'otherID'
        self.u0.permissions_level = Permissions.admin
        self.t2.add_member(self.u0.github_id)
        self.t3.add_member(self.u0.github_id)
        with self.app.app_context():
            # Leads member should not be demoted if they are also a admin
            # member
            resp, code = self.cmd.handle(
                f'team remove leads {self.u0.slack_id}',
                self.admin.slack_id)
            expect_msg = 'Removed User from leads'
            expect = {'attachments': [self.t2.get_attachment()],
                      'text': expect_msg}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.assertEqual(self.u0.permissions_level, Permissions.admin)
        self.gh.remove_team_member.assert_called_once_with(
            self.u0.github_username,
            self.t2.github_team_id)

    def test_handle_remove_not_admin(self):
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(
                f'team remove {self.t0.github_team_name} {self.u0.slack_id}',
                self.u1.slack_id),
                                  (self.cmd.permission_error, 200))
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_lookup_error(self):
        cmdtxt = f'team remove {self.t0.github_team_name} {self.u0.slack_id}'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, 'another.rando'),
                                  (self.cmd.lookup_error, 200))
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_github_error(self):
        cmdtxt = f'team remove {self.t0.github_team_name} {self.u0.slack_id}'
        self.gh.has_team_member.side_effect = GithubAPIException('error')
        with self.app.app_context():
            res = self.cmd.handle(cmdtxt, self.admin.slack_id)
            self.assertTupleEqual(res,
                                  ('User removed unsuccessfully with the '
                                   'following error: error', 200))
        self.gh.remove_team_member.assert_not_called()

    def test_handle_lead_add(self):
        cmdtxt = f'team lead {self.t0.github_team_name} {self.u0.slack_id}'
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        with self.app.app_context():
            _, code = self.cmd.handle(cmdtxt, self.admin.slack_id)
            self.assertEqual(code, 200)
            self.assertTrue(self.t0.has_team_lead(self.u0.github_id))
            self.assertTrue(self.t0.has_member(self.u0.github_id))
            self.gh.add_team_member.assert_called_once_with(
                self.u0.github_username,
                self.t0.github_team_id)

    def test_handle_lead_remove(self):
        cmdtxt = 'team lead --remove '
        cmdtxt += f'{self.t0.github_team_name} {self.u0.slack_id}'
        self.u0.github_id = 'githubID'
        self.u0.github_username = 'myuser'
        self.t0.add_member(self.u0.github_id)
        self.t0.add_team_lead(self.u0.github_id)
        with self.app.app_context():
            _, code = self.cmd.handle(cmdtxt, self.admin.slack_id)
            self.assertEqual(code, 200)
            self.assertFalse(self.t0.has_team_lead(self.u0.github_id))

    def test_handle_lead_not_admin(self):
        cmdtxt = f'team lead {self.t0.github_team_name} {self.u0.slack_id}'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, self.u1.slack_id),
                                  (self.cmd.permission_error, 200))

    def test_handle_lead_cannot_find_calling_user(self):
        cmdtxt = f'team lead {self.t0.github_team_name} {self.u0.slack_id}'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, 'rando.rand'),
                                  (self.cmd.lookup_error, 200))

    def test_handle_lead_github_error(self):
        cmdtxt = f'team lead {self.t0.github_team_name} {self.u0.slack_id}'
        self.gh.add_team_member.side_effect = GithubAPIException('error')
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, self.admin.slack_id),
                                  ('Edit team lead was unsuccessful with the '
                                   'following error: error', 200))

    def test_handle_lead_user_error(self):
        cmdtxt = 'team lead --remove '
        cmdtxt += f'{self.t0.github_team_name} {self.u0.slack_id}'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, self.admin.slack_id),
                                  ('User not in team!', 200))

    def test_handle_edit(self):
        cmdtxt = f'team edit {self.t0.github_team_name}'
        cmdtxt += ' --name brS --platform web'
        with self.app.app_context():
            _, code = self.cmd.handle(cmdtxt, self.admin.slack_id)
            self.assertEqual(self.t0.display_name, 'brS')
            self.assertEqual(self.t0.platform, 'web')
            self.assertEqual(code, 200)

    def test_handle_edit_not_admin(self):
        cmdtxt = f'team edit {self.t0.github_team_name}'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, self.u0.slack_id),
                                  (self.cmd.permission_error, 200))

    def test_handle_edit_lookup_error(self):
        cmdtxt = 'team edit rando.team'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, self.admin.slack_id),
                                  (self.cmd.lookup_error, 200))

    def test_handle_refresh_not_admin(self):
        cmdtxt = 'team refresh'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, self.u0.slack_id),
                                  (self.cmd.permission_error, 200))

    def test_handle_refresh_cannot_find_calling_user(self):
        cmdtxt = 'team refresh'
        with self.app.app_context():
            self.assertTupleEqual(self.cmd.handle(cmdtxt, 'rando.randy'),
                                  (self.cmd.lookup_error, 200))

    def test_handle_refresh_github_error(self):
        self.gh.org_get_teams.side_effect = GithubAPIException('error')
        with self.app.app_context():
            resp = self.cmd.handle('team refresh', self.admin.slack_id)
            self.assertTupleEqual(resp,
                                  ('Refresh teams was unsuccessful with '
                                   'the following error: error', 200))

    def test_handle_refresh_team_edited_on_github(self):
        team = Team('TeamID', 'TeamName', 'android')
        team_update = Team('TeamID', 'new team name', 'android')
        team_update.add_member(self.admin.github_id)
        team2 = Team('OTEAM', 'other team2', 'ios')

        self.db.teams = {}
        self.db.teams['TeamID'] = team
        self.db.teams['OTEAM'] = team2

        self.gh.org_get_teams.return_value = [team_update, team2]
        attachments = [team_update.get_attachment()]

        status = '1 teams changed, 0 added, 0 deleted. Wonderful.'
        with self.app.app_context():
            resp, code = self.cmd.handle('team refresh',
                                         self.admin.slack_id)
            self.assertCountEqual(resp['attachments'], attachments)
            self.assertEqual(resp['text'], status)
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
        attachments = [team.get_attachment(), team2.get_attachment()]

        status = '0 teams changed, 1 added, 1 deleted. Wonderful.'
        with self.app.app_context():
            resp, code = self.cmd.handle('team refresh',
                                         self.admin.slack_id)
            self.assertCountEqual(resp['attachments'], attachments)
            self.assertEqual(resp['text'], status)
            self.assertEqual(code, 200)
            self.assertEqual(len(self.db.teams), 2)
