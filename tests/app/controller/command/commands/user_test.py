from app.controller.command.commands import UserCommand
from tests.memorydb import MemoryDB
from tests.util import create_test_admin
from flask import Flask
from interface.github import GithubInterface, GithubAPIException
from app.model import User, Team, Permissions
from unittest import mock, TestCase


class TestUserCommand(TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        self.u0 = User('U0G9QF9C6')
        self.u1 = User('Utheomadude')
        self.t0 = Team("BRS", "brs", "web")
        self.t1 = Team("OTEAM", "other team", "android")
        self.admin = create_test_admin('Uadmin')
        self.db = MemoryDB(users=[self.u0, self.u1, self.admin],
                           teams=[self.t0, self.t1])

        self.mock_github = mock.MagicMock(GithubInterface)
        self.testcommand = UserCommand(self.db, self.mock_github, None)
        self.maxDiff = None

    def test_get_help(self):
        """Test user command get_help method."""
        subcommands = list(self.testcommand.subparser.choices.keys())
        help_message = self.testcommand.get_help()
        self.assertEqual(len(subcommands), help_message.count("usage"))

    def test_get_subcommand_help(self):
        """Test user command get_help method for specific subcommands."""
        subcommands = list(self.testcommand.subparser.choices.keys())
        for subcommand in subcommands:
            help_message = self.testcommand.get_help(subcommand=subcommand)
            self.assertEqual(1, help_message.count("usage"))

    def test_get_invalid_subcommand_help(self):
        """Test user command get_help method for invalid subcommands."""
        self.assertEqual(self.testcommand.get_help(),
                         self.testcommand.get_help(subcommand="foo"))

    def test_handle_nosubs(self):
        """Test user with no sub-parsers."""
        self.assertEqual(self.testcommand.handle('user',
                                                 self.u0.slack_id),
                         (self.testcommand.help, 200))

    def test_handle_bad_args(self):
        """Test user with invalid arguments."""
        self.assertEqual(self.testcommand.handle('user geese',
                                                 self.u0.slack_id),
                         (self.testcommand.help, 200))

    def test_handle_add(self):
        """Test user command add method."""
        user_id = "U0G9QF9C7"
        user = User(user_id)
        self.assertTupleEqual(self.testcommand.handle('user add', user_id),
                              ('User added!', 200))
        retr = self.db.retrieve(User, user_id)
        self.assertEqual(user, retr)

    def test_handle_add_no_overwriting(self):
        """Test user command add method when user exists in db."""
        user = User(self.u0.slack_id)
        err_msg = 'User already exists; to overwrite user, add `-f`'
        resp = self.testcommand.handle('user add', user.slack_id)
        self.assertTupleEqual(resp, (err_msg, 200))

    def test_handle_add_with_force(self):
        ret = self.testcommand.handle('user add -f', self.u0.slack_id)
        self.assertEqual(ret, ('User added!', 200))

    def test_handle_view(self):
        user_attaches = [self.u0.get_attachment()]
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle('user view',
                                                 self.u0.slack_id)
            expect = {'attachments': user_attaches}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_view_other_user_by_slack(self):
        user = User("ABCDE8FA9")
        self.db.store(user)
        command = 'user view --username ' + user.slack_id
        user_attaches = [user.get_attachment()]
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle(command, self.u0.slack_id)
            expect = {'attachments': user_attaches}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_view_other_user_by_github(self):
        user = User("ABCDE8FA9")
        user.github_username = 'MYGITHUB'
        self.db.store(user)
        command = 'user view --github ' + user.github_username
        user_attaches = [user.get_attachment()]
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle(command, self.u0.slack_id)
            expect = {'attachments': user_attaches}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_view_other_user_by_email(self):
        user = User("ABCDE8FA9")
        user.email = 'me@email.com'
        self.db.store(user)
        command = 'user view --email ' + user.email
        user_attaches = [user.get_attachment()]
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle(command, self.u0.slack_id)
            expect = {'attachments': user_attaches}
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_view_multiple_users(self):
        user = User("ABCDE8FA9")
        user.email = 'me@email.com'
        self.db.store(user)
        user2 = User("ABCDE8FA0")
        user2.email = 'me@email.com'
        self.db.store(user2)
        command = 'user view --email ' + user.email
        user_attaches = [user.get_attachment(), user2.get_attachment()]
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle(command, self.u0.slack_id)
            expect = {
                'text': 'Warning - multiple users found!',
                'attachments': user_attaches,
            }
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_view_lookup_error(self):
        command = 'user view --username ABCDE8FA9'
        self.assertTupleEqual(self.testcommand.handle(command,
                                                      self.u0.slack_id),
                              (UserCommand.lookup_error, 200))

    def test_handle_help(self):
        self.assertEqual(self.testcommand.handle('user help',
                                                 self.u0.slack_id),
                         (self.testcommand.help, 200))

    def test_handle_delete(self):
        message = f'Deleted user with Slack ID: {self.u0.slack_id}'
        cmd = f'user delete {self.u0.slack_id}'
        self.assertEqual(self.testcommand.handle(cmd, self.admin.slack_id),
                         (message, 200))
        with self.assertRaises(LookupError):
            self.db.retrieve(User, self.u0.slack_id)

    def test_handle_delete_not_admin(self):
        cmd = f'user delete {self.u1.slack_id}'
        self.assertEqual(self.testcommand.handle(cmd, self.u0.slack_id),
                         (UserCommand.permission_error, 200))

    def test_handle_delete_callinguser_lookup_error(self):
        cmd = f'user delete {self.u1.slack_id}'
        self.assertEqual(self.testcommand.handle(cmd, 'rando.id'),
                         (UserCommand.lookup_error, 200))

    def test_handle_edit_name(self):
        with self.app.app_context():
            resp, code = self.testcommand.handle('user edit --name rob',
                                                 self.u0.slack_id)
            expect = {'title': 'Name', 'value': 'rob', 'short': True}
            self.assertIn(expect, resp['attachments'][0]['fields'])
            self.assertEqual(code, 200)

    def test_handle_edit_github(self):
        """Test that editing github username sends request to interface."""
        self.mock_github.org_add_member.return_value = "123"
        with self.app.app_context():
            resp, code = self.testcommand.handle("user edit --github rob",
                                                 self.u0.slack_id)
            expect0 = {'title': 'Github Username',
                       'value': 'rob',
                       'short': True}
            expect1 = {'title': 'Github ID', 'value': '123', 'short': True}
            self.assertIn(expect0, resp['attachments'][0]['fields'])
            self.assertIn(expect1, resp['attachments'][0]['fields'])
            self.assertEqual(code, 200)
        self.mock_github.org_add_member.assert_called_once_with("rob")

    def test_handle_edit_github_error(self):
        self.mock_github.org_add_member.side_effect = GithubAPIException("")

        with self.app.app_context():
            resp, code = self.testcommand.handle('user edit --github rob',
                                                 self.u0.slack_id)
            expect = {
                'attachments': [self.u0.get_attachment()],
                'text': '\nError adding user rob to GitHub organization'
            }

            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_edit_all_fields(self):
        user = User(self.u0.slack_id)
        user.name = 'rob'
        user.email = 'rob@rob.com'
        user.position = 'dev'
        user.github_username = 'rob'
        user.github_id = '123'
        user.major = 'Computer Science'
        user.biography = 'Im a human lol'
        user.permissions_level = Permissions.member
        expect = {'attachments': [user.get_attachment()]}
        self.mock_github.org_add_member.return_value = "123"
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "user edit "
                "--name rob "
                "--email <mailto:rob@rob.com|rob@rob.com> --pos dev --github"
                " rob --major 'Computer Science'"
                " --bio 'Im a human lol'",
                self.u0.slack_id)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_edit_not_admin(self):
        """Test user command with editor user that is not admin."""
        self.assertEqual(self.testcommand.handle(
            'user edit --username ' + self.u1.slack_id + ' '
            '--name rob '
            '--email <mailto:rob@rob.com|rob@rob.com> --pos dev --github'
            ' rob@.github.com --major \'Computer Science\''
            ' --bio \'Im a human\'',
            self.u0.slack_id),
            (UserCommand.permission_error, 200))

    def test_handle_edit_make_admin(self):
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                f"user edit --username {self.u0.slack_id} "
                "--permission admin",
                self.admin.slack_id)
            expect = {'title': 'Permissions Level',
                      'value': 'admin',
                      'short': True}
            self.assertIn(expect, resp['attachments'][0]['fields'])
            self.assertEqual(code, 200)

    def test_handle_edit_make_self_admin_no_perms(self):
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "user edit --permission admin", self.u0.slack_id)
            expect = {
                'attachments': [self.u0.get_attachment()],
                'text': "\nCannot change own permission: user isn't admin."
            }
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_edit_lookup_error_editee(self):
        self.assertEqual(self.testcommand.handle(
            "user edit --username random.something "
            "--name rob "
            "--email <mailto:rob@rob.com|rob@rob.com> --pos dev --github"
            " rob@.github.com --major 'Computer Science'"
            " --bio 'Im a human'",
            self.admin.slack_id),
            (UserCommand.lookup_error, 200))

    def test_handle_edit_lookup_error(self):
        """Test user command where user is not in database."""
        self.assertEqual(self.testcommand.handle('user edit --name rob',
                                                 'rando'),
                         (UserCommand.lookup_error, 200))

    def test_handle_command_help(self):
        ret, code = self.testcommand.handle('user help', self.u0.slack_id)
        self.assertEqual(ret, self.testcommand.get_help())
        self.assertEqual(code, 200)

    def test_handle_multiple_subcommands(self):
        """Test handling multiple observed subcommands."""
        ret, code = self.testcommand.handle('user edit view', self.u0.slack_id)
        self.assertEqual(ret, self.testcommand.get_help())
        self.assertEqual(code, 200)

    def test_handle_subcommand_help(self):
        subcommands = list(self.testcommand.subparser.choices.keys())
        for subcommand in subcommands:
            cmd_args = ['--help', '-h', '--invalid argument']
            for arg in cmd_args:
                command = f'user {subcommand} {arg}'
                ret, code = self.testcommand.handle(command, self.u0.slack_id)
                self.assertEqual(1, ret.count("usage"))
                self.assertIn(subcommand, ret)
                self.assertEqual(code, 200)

    def test_handle_deepdive(self):
        self.u0.name = 'John Peters'
        self.u0.email = 'john.peter@hotmail.com'
        self.u0.github_id = '328593'
        self.u0.github_username = 'some_user'
        self.t0.add_member(self.u0.github_id)
        self.t1.add_team_lead(self.u0.github_id)
        team_names = '\n'.join(
            ['- ' + t.github_team_name for t in [self.t0, self.t1]]
        )

        ret, code = self.testcommand.handle('user deepdive U0G9QF9C6',
                                            self.u1.slack_id)
        ret = ret['blocks'][0]['text']['text']
        self.assertIn(f'*Github name:* {self.u0.github_username}', ret)
        self.assertIn(f'*Name:* {self.u0.name}', ret)
        self.assertIn(f'*Email:* {self.u0.email}', ret)
        self.assertIn('*Permissions level:* member', ret)
        self.assertIn(f'*Membership in:*\n{team_names}', ret)
        self.assertIn(f'*Leading teams:*\n- {self.t1.github_team_name}', ret)

    def test_handle_deepdive_with_ghusername(self):
        self.u0.name = 'John Peters'
        self.u0.email = 'john.peter@hotmail.com'
        self.u0.github_id = '328593'
        self.u0.github_username = 'some_user'
        self.t0.add_member(self.u0.github_id)
        self.t1.add_team_lead(self.u0.github_id)
        team_names = '\n'.join(
            ['- ' + t.github_team_name for t in [self.t0, self.t1]]
        )

        ret, code = self.testcommand.handle('user deepdive some_user',
                                            self.u1.slack_id)
        ret = ret['blocks'][0]['text']['text']
        self.assertIn(f'*Github name:* {self.u0.github_username}', ret)
        self.assertIn(f'*Name:* {self.u0.name}', ret)
        self.assertIn(f'*Email:* {self.u0.email}', ret)
        self.assertIn('*Permissions level:* member', ret)
        self.assertIn(f'*Membership in:*\n{team_names}', ret)
        self.assertIn(f'*Leading teams:*\n- {self.t1.github_team_name}', ret)

    def test_handle_deepdive_user_no_exists(self):
        ret, code = self.testcommand.handle('user deepdive UXXXXXXXX',
                                            self.u1.slack_id)
        self.assertEqual(UserCommand.lookup_error, ret)

    def test_handle_deepdive_no_ghid(self):
        self.u0.name = 'John Peters'
        self.u0.email = 'john.peter@hotmail.com'

        ret, code = self.testcommand.handle('user deepdive U0G9QF9C6',
                                            self.u1.slack_id)
        ret = ret['blocks'][0]['text']['text']
        self.assertIn('*Github name:* n/a', ret)
        self.assertIn(f'*Name:* {self.u0.name}', ret)
        self.assertIn(f'*Email:* {self.u0.email}', ret)
        self.assertIn('*Permissions level:* member', ret)
        self.assertIn(UserCommand.noghid_deepdive, ret)
