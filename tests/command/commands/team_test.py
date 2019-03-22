"""Test team command parsing."""
from command.commands.team import TeamCommand
from unittest import TestCase, mock
from model.team import Team
from model.user import User
from model.permissions import Permissions
from interface.exceptions.github import GithubAPIException
from flask import jsonify, json, Flask

user = 'U123456789'
user2 = 'U234567891'


class TestTeamCommand(TestCase):
    """Test case for TeamCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.app = Flask(__name__)
        self.gh = mock.MagicMock()
        self.db = mock.MagicMock()
        self.sc = mock.MagicMock()
        self.testcommand = TeamCommand(self.db, self.gh, self.sc)
        self.help_text = self.testcommand.help
        self.maxDiff = None

    def test_get_name(self):
        """Test team command get_name method."""
        self.assertEqual(self.testcommand.get_name(), "team")

    def test_get_help(self):
        """Test team command get_help method."""
        print(f"\n{self.testcommand.get_help()}")
        self.assertEqual(self.testcommand.get_help(), self.help_text)

    def test_handle_help(self):
        """Test team command help parser."""
        self.assertTupleEqual(self.testcommand.handle('team help', user),
                              (self.help_text, 200))

    def test_handle_list(self):
        """Test team command list parser."""
        self.assertTupleEqual(self.testcommand.handle("team list", user),
                              ("listing all teams", 200))

    def test_handle_view(self):
        """Test team command view parser."""
        team = Team("BRS", "brs", "web")
        team_attach = [team.get_attachment()]
        self.db.retrieve.return_value = team
        with self.app.app_context():
            resp, code = self.testcommand.handle("team view brs", user)
            expect = json.loads(jsonify({'attachments': team_attach}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.db.retrieve.assert_called_once_with(Team, "brs")

    def test_handle_delete_not_admin(self):
        """Test team command delete parser with improper permission."""
        team = Team("BRS", "brs", "web")
        test_user = User("userid")
        self.db.retrieve.side_effect = [test_user, team]
        self.assertTupleEqual(self.testcommand.handle("team delete brs", user),
                              (self.testcommand.permission_error, 200))
        self.db.delete.assert_not_called()
        self.gh.org_delete_team.assert_not_called()

    def test_handle_delete_lookup_error(self):
        """Test team command delete parser with lookup error."""
        self.db.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle("team delete brs", user),
                              (self.testcommand.lookup_error, 200))
        self.db.delete.assert_not_called()
        self.gh.org_delete_team.assert_not_called()

    def test_handle_delete_github_error(self):
        """Test team command delete parser with Github error."""
        self.db.retrieve.side_effect = GithubAPIException("error")
        self.assertTupleEqual(self.testcommand.handle("team delete brs", user),
                              ("Team delete was unsuccessful with "
                               "the following error: "
                               "error", 200))
        self.db.delete.assert_not_called()
        self.gh.org_delete_team.assert_not_called()

    def test_handle_delete(self):
        """Test team command delete parser."""
        team = Team("BRS", "brs", "web")
        team.github_team_id = "githubid"
        test_user = User("userid")
        test_user.github_id = "1234"
        team.add_team_lead("1234")
        self.db.retrieve.side_effect = [test_user, team]
        self.assertTupleEqual(self.testcommand.handle("team delete brs", user),
                              (f"Team brs deleted", 200))
        self.db.delete.assert_called_once_with(Team, team)
        self.gh.org_delete_team.assert_called_once_with("githubid")

    def test_handle_create(self):
        """Test team command create parser."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        test_user.github_username = "githubuser"
        self.db.retrieve.return_value = test_user
        self.gh.org_create_team.return_value = "team_id"
        inputstring = "team create b-s --name 'B S'"
        outputstring = "New team created: b-s, name: B S, "
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
        inputstring += " --platform web"
        outputstring += "platform: web, "
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
        self.gh.org_create_team.assert_called()
        self.gh.add_team_member.assert_called_with('githubuser', 'team_id')
        inputstring += " --channel 'channelID'"
        outputstring += "added channel, "
        self.sc.get_channel_users.return_value = ['someID', 'otherID']
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
        self.sc.get_channel_users.assert_called_once_with("channelID")
        self.db.retrieve.assert_called_with(User, 'otherID')
        self.gh.add_team_member.assert_called()
        inputstring += " --lead 'someID'"
        outputstring += "added lead"
        self.gh.has_team_member.return_value = False
        print(self.testcommand.handle(inputstring, user))
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (outputstring, 200))
        self.db.store.assert_called()

    def test_handle_create_not_admin(self):
        """Test team command create parser with improper permission."""
        test_user = User("userid")
        test_user.github_username = "githubuser"
        self.db.retrieve.return_value = test_user
        self.gh.org_create_team.return_value = "team_id"
        inputstring = "team create b-s --name 'B S'"
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (self.testcommand.permission_error, 200))
        self.db.store.assert_not_called()

    def test_handle_create_github_error(self):
        """Test team command create parser with Github error."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        test_user.github_username = "githubuser"
        self.db.retrieve.return_value = test_user
        self.gh.org_create_team.return_value = "team_id"
        inputstring = "team create b-s --name 'B S'"
        self.gh.add_team_member.side_effect = GithubAPIException("error")
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              ("Team creation unsuccessful with the "
                               "following error: error", 200))
        self.db.store.assert_not_called()

    def test_handle_create_lookup_error(self):
        """Test team command create parser with Lookup error."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        test_user.github_username = "githubuser"
        self.db.retrieve.return_value = test_user
        self.gh.org_create_team.return_value = "team_id"
        inputstring = "team create b-s --name 'B S'"
        self.db.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle(inputstring, user),
                              (self.testcommand.lookup_error, 200))
        self.db.store.assert_not_called()

    def test_handle_add(self):
        """Test team command add parser."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        test_user.github_username = "githubuser"
        team = Team("BRS", "brs", "web")
        team.github_team_id = "githubid"
        add_user = User("anotheruser")
        add_user.github_username = "myuser"
        add_user.github_id = "otherID"
        self.db.retrieve.side_effect = [test_user, team, add_user]
        with self.app.app_context():
            resp, code = self.testcommand.handle("team add brs ID", user)
            team_attach = team.get_attachment()
            expect = json.loads(jsonify({'attachments': [team_attach],
                                         'text': 'Added User to brs'}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.db.store.assert_called_with(team)
        assert team.has_member("otherID")
        self.gh.add_team_member.assert_called_once_with("myuser", "githubid")

    def test_handle_add_not_admin(self):
        """Test team command add parser with insufficient permission."""
        test_user = User("userid")
        test_user.github_username = "githubuser"
        team = Team("BRS", "brs", "web")
        team.github_team_id = "githubid"
        self.db.retrieve.side_effect = [test_user, team]
        self.assertTupleEqual(self.testcommand.handle("team add brs ID", user),
                              (self.testcommand.permission_error, 200))
        self.db.store.assert_not_called()
        self.gh.add_team_member.assert_not_called()

    def test_handle_add_github_error(self):
        """Test team command add parser with Github Exception."""
        test_user = User("userid")
        test_user.github_username = "githubuser"
        test_user.permissions_level = Permissions.admin
        team = Team("BRS", "brs", "web")
        team.github_team_id = "githubid"
        add_user = User("anotheruser")
        add_user.github_username = "myuser"
        self.db.retrieve.side_effect = [test_user, team, add_user]
        self.gh.add_team_member.side_effect = GithubAPIException("error")
        self.assertTupleEqual(self.testcommand.handle("team add brs ID", user),
                              ("User added unsuccessfully with the"
                               " following error: error", 200))
        self.db.store.assert_not_called()

    def test_handle_add_lookup_error(self):
        """Test team command parser with lookup error."""
        self.db.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle("team add brs ID", user),
                              (self.testcommand.lookup_error, 200))
        self.db.store.assert_not_called()
        self.gh.add_team_member.assert_not_called()

    def test_handle_remove(self):
        """Test team command remove parser."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        test_user.github_username = "githubuser"
        team = Team("BRS", "brs", "web")
        team.github_team_id = "githubid"
        other_user = User("anotheruser")
        other_user.github_id = "githubID"
        other_user.github_username = "myuser"
        self.db.retrieve.side_effect = [test_user, team, other_user,
                                        test_user, team, other_user]
        team_attach = [team.get_attachment()]
        with self.app.app_context():
            self.testcommand.handle("team add brs ID", user)
            resp, code = self.testcommand.handle("team remove brs ID", user)
            expect = json.loads(jsonify({'attachments': team_attach,
                                         'text': 'Removed User from brs'}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.db.store.assert_called_with(team)
        self.gh.remove_team_member.assert_called_once_with("myuser", "githubid")

    def test_handle_remove_not_in_team(self):
        """Test team command remove parser when user is not in team."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        team = Team("BRS", "brs", "web")
        team.github_team_id = "githubid"
        other_user = User("anotheruser")
        other_user.github_id = "githubID"
        other_user.github_username = "myuser"
        self.db.retrieve.side_effect = [test_user, team, other_user]
        self.gh.has_team_member.return_value = False
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team remove brs ID", user),
                                  ("User not in team!", 200))
        self.gh.has_team_member.assert_called_once_with("myuser", "githubid")
        self.db.store.assert_not_called()
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_not_admin(self):
        """Test team command remove parser with insufficient permission."""
        test_user = User("userid")
        team = Team("BRS", "brs", "web")
        self.db.retrieve.side_effect = [test_user, team]
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team remove brs ID", user),
                                  (self.testcommand.permission_error, 200))
        self.db.store.assert_not_called()
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_lookup_error(self):
        """Test team command remove parser with lookup error."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        team = Team("BRS", "brs", "web")
        self.db.retrieve.side_effect = LookupError
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team remove brs ID", user),
                                  (self.testcommand.lookup_error, 200))
        self.db.store.assert_not_called()
        self.gh.remove_team_member.assert_not_called()

    def test_handle_remove_github_error(self):
        """Test team command remove parser with github error."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        team = Team("BRS", "brs", "web")
        other_user = User("anotheruser")
        other_user.github_id = "githubID"
        other_user.github_username = "myuser"
        self.db.retrieve.side_effect = [test_user, team, other_user]
        self.gh.has_team_member.side_effect = GithubAPIException("error")
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team remove brs ID", user),
                                  ("User removed unsuccessfully with the "
                                   "following error: error", 200))
        self.db.store.assert_not_called()
        self.gh.remove_team_member.assert_not_called()

    def test_handle_lead(self):
        """Test team command lead parser with add and remove options."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        test_user.github_username = "githubuser"
        team = Team("BRS", "brs", "web")
        team.github_team_id = "githubid"
        other_user = User("anotheruser")
        other_user.github_id = "githubID"
        other_user.github_username = "myuser"
        self.db.retrieve.side_effect = [test_user, team, other_user,
                                        test_user, team, other_user]
        team.add_member("githubID")
        team_before_attach = [team.get_attachment()]
        team.add_team_lead("githubID")
        team_attach = [team.get_attachment()]
        team.discard_member("githubID")
        with self.app.app_context():
            resp, code = self.testcommand.handle("team lead brs ID", user)
            expect = json.loads(jsonify({'attachments': team_attach,
                                         'text': 'User added as team lead to brs'}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
            assert team.has_member("githubID")
            self.gh.add_team_member.assert_called_once_with("myuser", "githubid")
            self.db.store.assert_called()
            resp, code = self.testcommand.handle("team lead  --remove brs ID", user)
            expect = json.loads(jsonify({'attachments': team_before_attach,
                                         'text': 'User removed as team lead'
                                                 ' from brs'}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
            assert not team.has_team_lead("githubID")
            self.db.store.assert_called()

    def test_handle_lead_not_admin(self):
        """Test team command lead parser with insufficient permission."""
        test_user = User("userid")
        team = Team("BRS", "brs", "web")
        self.db.retrieve.side_effect = [test_user, team]
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team lead brs ID", user),
                                  (self.testcommand.permission_error, 200))
        self.db.store.assert_not_called()

    def test_handle_lead_lookup_error(self):
        """Test team command laed parser with lookup error."""
        test_user = User("userid")
        team = Team("BRS", "brs", "web")
        self.db.retrieve.side_effect = LookupError
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team lead brs ID", user),
                                  (self.testcommand.lookup_error, 200))
        self.db.store.assert_not_called()

    def test_handle_lead_github_error(self):
        """Test team command lead parser with github error."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        team = Team("BRS", "brs", "web")
        self.db.retrieve.side_effect = [test_user, team, test_user]
        self.gh.add_team_member.side_effect = GithubAPIException("error")
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team lead brs ID", user),
                                  ("Edit team lead was unsuccessful with the "
                                   "following error: error", 200))
        self.db.store.assert_not_called()

    def test_handle_lead_user_error(self):
        """Test team command lead remove parser with user not in team."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        team = Team("BRS", "brs", "web")
        self.db.retrieve.side_effect = [test_user, team, test_user]
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team lead --remove brs ID", user),
                                  ("User not in team!", 200))
        self.db.store.assert_not_called()

    def test_handle_edit(self):
        """Test team command edit parser."""
        test_user = User("userid")
        test_user.permissions_level = Permissions.admin
        team = Team("BRS", "brs", "brS")
        team.platform = "web"
        team_attach = [team.get_attachment()]
        team.platform = "iOS"
        team.display_name = "b-s"
        self.db.retrieve.side_effect = [test_user, team]
        with self.app.app_context():
            resp, code = self.testcommand.handle("team edit brs "
                                                 "--name brS --platform web", user)
            expect = json.loads(jsonify({'attachments': team_attach,
                                         'text': 'Team edited: brs, '
                                                 'name: brS, platform: web'}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
            self.db.store.assert_called_once_with(team)

    def test_handle_edit_not_admin(self):
        """Test team command edit parser with insufficient permission."""
        test_user = User("userid")
        team = Team("BRS", "brs", "brS")
        self.db.retrieve.side_effect = [test_user, team]
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team edit brs", user),
                                  (self.testcommand.permission_error, 200))
        self.db.store.assert_not_called()

    def test_handle_edit_lookup_error(self):
        """Test team command edit parser with lookup error."""
        test_user = User("userid")
        team = Team("BRS", "brs", "brS")
        self.db.retrieve.side_effect = LookupError
        with self.app.app_context():
            self.assertTupleEqual(self.testcommand.handle("team edit brs", user),
                                  (self.testcommand.lookup_error, 200))
        self.db.store.assert_not_called()
