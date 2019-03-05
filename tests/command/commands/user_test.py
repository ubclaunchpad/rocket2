"""Test user command parsing."""
from flask import jsonify, json, Flask
from command.commands.user import UserCommand
from unittest import mock, TestCase
from model.user import User
from db.facade import DBFacade
from model.permissions import Permissions
from interface.slack import Bot
from interface.github import GithubInterface, GithubAPIException


class TestUserCommand(TestCase):
    """Test Case for UserCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.app = Flask(__name__)
        self.mock_facade = mock.MagicMock(DBFacade)
        self.mock_github = mock.MagicMock(GithubInterface)
        self.testcommand = UserCommand(self.mock_facade, self.mock_github)
        self.maxDiff = None

    def test_get_command_name(self):
        """Test user command get_name method."""
        assert self.testcommand.get_name() == "user"

    def test_get_help(self):
        """Test user command get_help method."""
        assert self.testcommand.get_help() == self.testcommand.help

    def test_handle_nosubs(self):
        """Test user with no sub-parsers."""
        self.assertEqual(self.testcommand.handle('user', "U0G9QF9C6"),
                         (self.testcommand.help, 200))

    def test_handle_bad_args(self):
        """Test user with invalid arguments."""
        self.assertEqual(self.testcommand.handle('user geese', "U0G9QF9C6"),
                         (self.testcommand.help, 200))

    def test_handle_bad_optional_args(self):
        """Test user edit with invalid optional arguments."""
        self.assertEqual(self.testcommand.handle('user edit --biology stuff',
                                                 "U0G9QF9C6"),
                         (self.testcommand.help, 200))

    def test_handle_add(self):
        """Test user command add method."""
        user_id = "U0G9QF9C6"
        user = User(user_id)
        lookup_error = LookupError('User "{}" not found'.format(user_id))
        self.mock_facade.retrieve.side_effect = lookup_error
        self.assertTupleEqual(self.testcommand.handle('user add', user_id),
                              ('User added!', 200))
        self.mock_facade.store.assert_called_once_with(user)

    def test_handle_add_no_overwriting(self):
        """Test user command add method when user exists in db."""
        user_id = "U0G9QF9C6"
        user = User(user_id)
        self.mock_facade.retrieve.return_value = user

        # Since the user exists, we don't call store_user()
        err_msg = 'User already exists; to overwrite user, add `-f`'
        resp = self.testcommand.handle('user add', user_id)
        self.assertTupleEqual(resp, (err_msg, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, user_id)
        self.mock_facade.store.assert_not_called()

    def test_handle_add_overwriting(self):
        """Test user command add method when user exists in db."""
        user_id = "U0G9QF9C6"
        user2_id = "U0G9QF9C69"
        user = User(user_id)
        user2 = User(user2_id)

        self.testcommand.handle('user add -f', user_id)
        self.mock_facade.store.assert_called_with(user)
        self.testcommand.handle('user add --force', user2_id)
        self.mock_facade.store.assert_called_with(user2)
        self.mock_facade.retrieve.assert_not_called()

    def test_handle_view(self):
        """Test user command view parser and handle method."""
        user_id = "U0G9QF9C6"
        user = User(user_id)
        self.mock_facade.retrieve.return_value = user
        user_attaches = [user.get_attachment()]
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle('user view', user_id)
            expect = json.loads(jsonify({'attachments': user_attaches}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")

    def test_handle_view_other_user(self):
        """Test user command view handle with slack_id parameter."""
        user_id = "U0G9QF9C6"
        user = User("ABCDE8FA9")
        command = 'user view --slack_id ' + user.slack_id
        self.mock_facade.retrieve.return_value = user
        user_attaches = [user.get_attachment()]
        with self.app.app_context():
            # jsonify requires translating the byte-string
            resp, code = self.testcommand.handle(command, user_id)
            expect = json.loads(jsonify({'attachments': user_attaches}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.\
            assert_called_once_with(User, "ABCDE8FA9")

    def test_handle_view_lookup_error(self):
        """Test user command view handle with user not in database."""
        user_id = "U0G9QF9C6"
        command = 'user view --slack_id ABCDE8FA9'
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertTupleEqual(self.testcommand.handle(command, user_id),
                              (UserCommand.lookup_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "ABCDE8FA9")

    def test_handle_help(self):
        """Test user command help parser."""
        self.assertEqual(self.testcommand.handle('user help', "U0G9QF9C6"),
                         (self.testcommand.help, 200))

    def test_handle_delete(self):
        """Test user command delete parser."""
        user = User("ABCDEFG2F")
        user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.return_value = user
        message = "Deleted user with Slack ID: " + "U0G9QF9C6"
        self.assertEqual(self.testcommand.handle("user delete U0G9QF9C6",
                                                 "ABCDEFG2F"),
                         (message, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "ABCDEFG2F")
        self.mock_facade.delete.assert_called_once_with(User, "U0G9QF9C6")

    def test_handle_delete_not_admin(self):
        """Test user command delete where user is not admin."""
        user = User("ABCDEFG2F")
        user.permissions_level = Permissions.member
        self.mock_facade.retrieve.return_value = user
        self.assertEqual(self.testcommand.handle("user delete U0G9QF9C6",
                                                 "ABCDEFG2F"),
                         (UserCommand.permission_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "ABCDEFG2F")
        self.mock_facade.delete.assert_not_called()

    def test_handle_delete_lookup_error(self):
        """Test user command delete parser."""
        user = User("ABCDEFG2F")
        user.permissions_level = Permissions.admin
        self.mock_facade.retrieve.return_value = user
        self.mock_facade.delete.side_effect = LookupError
        self.assertEqual(self.testcommand.handle("user delete U0G9QF9C6",
                                                 "ABCDEFG2F"),
                         (UserCommand.lookup_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "ABCDEFG2F")
        self.mock_facade.delete.assert_called_once_with(User, "U0G9QF9C6")

    def test_handle_edit_name(self):
        """Test user command edit parser with one field."""
        user = User("U0G9QF9C6")
        user.name = "rob"
        user_attaches = [user.get_attachment()]
        self.mock_facade.retrieve.return_value = user
        with self.app.app_context():
            resp, code = self.testcommand.handle("user edit --name rob",
                                                 "U0G9QF9C6")
            expect = json.loads(jsonify({'attachments': user_attaches}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")
        self.mock_facade.store.assert_called_once_with(user)

    def test_handle_edit_github(self):
        """Test that editing github username sends request to interface."""
        user = User("U0G9QF9C6")
        user.github_username = "rob"
        user_attaches = [user.get_attachment()]
        self.mock_facade.retrieve.return_value = user
        with self.app.app_context():
            resp, code = self.testcommand.handle("user edit --github rob",
                                                 "U0G9QF9C6")
            expect = json.loads(jsonify({'attachments': user_attaches}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")
        self.mock_facade.store.assert_called_once_with(user)
        self.mock_github.org_add_member.assert_called_once_with("rob")

    def test_handle_edit_github_error(self):
        """Test that editing github username sends request to interface."""
        user = User("U0G9QF9C6")
        self.mock_facade.retrieve.return_value = user
        self.mock_github.org_add_member.side_effect = GithubAPIException("")
        user_attaches = [user.get_attachment()]
        with self.app.app_context():
            resp, code = self.testcommand.handle("user edit --github rob",
                                                 "U0G9QF9C6")
            expect = {
                'attachments': user_attaches,
                'text': "\nError adding user rob to GitHub organization"
            }
            expect = json.loads(jsonify(expect).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")
        self.mock_facade.store.assert_called_once_with(user)

    def test_handle_edit_github_error(self):
        """Test that editing github username sends request to interface."""
        user = User("U0G9QF9C6")
        self.mock_facade.retrieve.return_value = user
        self.mock_github.org_add_member.side_effect = GithubAPIException("")
        user_attaches = [user.get_attachment()]

        with self.app.app_context():
            resp, code = self.testcommand.handle('user edit --github rob',
                                                 'U0G9QF9C6')
            expect = {
                'attachments': user_attaches,
                'text': '\nError adding user rob to GitHub organization'
            }

            expect = json.loads(jsonify(expect).data)
            resp = json.loads(resp.data)

            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")
        self.mock_facade.store.assert_called_once_with(user)

    def test_handle_edit_other_user(self):
        """Test user command edit parser with all fields."""
        user = User("ABCDE89JK")
        user.name = "rob"
        user.email = "rob@rob.com"
        user.position = "dev"
        user.github_username = "rob@.github.com"
        user.major = "Computer Science"
        user.biography = "Im a human"
        user.permissions_level = Permissions.admin
        user_attaches = [user.get_attachment()]
        self.mock_facade.retrieve.return_value = user
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "user edit --member U0G9QF9C6 "
                "--name rob "
                "--email rob@rob.com --pos dev --github"
                " rob@.github.com --major 'Computer Science'"
                " --bio 'Im a human'",
                "U0G9QF9C6")
            expect = json.loads(jsonify({'attachments': user_attaches}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)
        self.mock_facade.retrieve.assert_any_call(User, "U0G9QF9C6")
        self.mock_facade.store.assert_called_once_with(user)

    def test_handle_edit_not_admin(self):
        """Test user command with editor user that is not admin."""
        user_editor = User("U0G9QF9C6")
        user_editor.permissions_level = Permissions.member
        self.mock_facade.retrieve.return_value = user_editor
        self.assertEqual(self.testcommand.handle(
            "user edit --member ABCDE89JK "
            "--name rob "
            "--email rob@rob.com --pos dev --github"
            " rob@.github.com --major 'Computer Science'"
            " --bio 'Im a human'",
            "U0G9QF9C6"),
            (UserCommand.permission_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")
        self.mock_facade.store.assert_not_called()

    def test_handle_edit_make_admin(self):
        """Test user command with editor that is admin and user who's not."""
        editor = User("a1")
        editee = User("arst")
        rets = [editor, editee]
        editor.permissions_level = Permissions.admin
        editee.permissions_level = Permissions.admin
        self.mock_facade.retrieve.side_effect = rets
        editee_attaches = [editee.get_attachment()]
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "user edit --member arst "
                "--permission admin",
                "a1")
            expect = json.loads(jsonify({'attachments': editee_attaches}).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_edit_make_admin_no_perms(self):
        """Test user command with editor that isn't admin."""
        editor = User("a1")
        editor_attaches = [editor.get_attachment()]
        self.mock_facade.retrieve.return_value = editor
        with self.app.app_context():
            resp, code = self.testcommand.handle(
                "user edit --permission admin", "a1")
            expect = {
                'attachments': editor_attaches,
                'text': "\nCannot change own permission: user isn't admin."
            }
            expect = json.loads(jsonify(expect).data)
            resp = json.loads(resp.data)
            self.assertDictEqual(resp, expect)
            self.assertEqual(code, 200)

    def test_handle_edit_lookup_error_editor(self):
        """Test user command where user editor is not in database."""
        user_editor = User("U0G9QF9C6")
        self.mock_facade.retrieve.return_value = user_editor
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertEqual(self.testcommand.handle(
            "user edit --member ABCDE89JK "
            "--name rob "
            "--email rob@rob.com --pos dev --github"
            " rob@.github.com --major 'Computer Science'"
            " --bio 'Im a human'",
            "U0G9QF9C6"),
            (UserCommand.lookup_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")
        self.mock_facade.store.assert_not_called()

    def test_handle_edit_lookup_error(self):
        """Test user command where user is not in database."""
        user = User("U0G9QF9C6")
        self.mock_facade.retrieve.return_value = user
        self.mock_facade.retrieve.side_effect = LookupError
        self.assertEqual(self.testcommand.handle("user edit --name rob",
                                                 "U0G9QF9C6"),
                         (UserCommand.lookup_error, 200))
        self.mock_facade.retrieve.assert_called_once_with(User, "U0G9QF9C6")
        self.mock_facade.store.assert_not_called()
