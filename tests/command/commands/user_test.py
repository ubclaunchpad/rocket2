"""Test user command parsing."""
from command.commands.user import UserCommand
from unittest import mock, TestCase
from model.user import User
from db.facade import DBFacade
from model.permissions import Permissions
from bot.bot import Bot


class TestUserCommand(TestCase):
    """Test Case for UserCommand class."""

    def setUp(self):
        """Set up the test case environment."""
        self.mock_facade = mock.MagicMock(DBFacade)
        self.mock_bot = mock.MagicMock(Bot)
        self.testcommand = UserCommand(self.mock_facade, self.mock_bot)

    def test_get_command_name(self):
        """Test user command get_name method."""
        assert self.testcommand.get_name() == "user"

    def test_get_help(self):
        """Test user command get_help method."""
        assert self.testcommand.get_help() == UserCommand.help

    def test_handle_nosubs(self):
        """Test user with no sub-parsers."""
        self.testcommand.handle('user', "U0G9QF9C6", "C0LAN2Q65")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(UserCommand.help, "C0LAN2Q65")

    def test_handle_bad_args(self):
        """Test user with invalid arguments."""
        self.testcommand.handle('user geese', "U0G9QF9C6", "C0LAN2Q65")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(UserCommand.help, "C0LAN2Q65")

    def test_handle_bad_optional_args(self):
        """Test user edit with invalid optional arguments."""
        self.testcommand.handle('user edit --biology stuff',
                                "U0G9QF9C6", "C0LAN2Q65")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(UserCommand.help, "C0LAN2Q65")

    def test_handle_view(self):
        """Test user command view parser and handle method."""
        user_id = "U0G9QF9C6"
        user = User(user_id)
        self.mock_facade.retrieve_user.return_value = user
        self.testcommand.handle('user view', user_id, "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("U0G9QF9C6")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(user.get_md_table(), "C0LAN2Q65")

    def test_handle_view_other_user(self):
        """Test user command view handle with slack_id parameter."""
        user_id = "U0G9QF9C6"
        user = User("ABCDE8FA9")
        self.mock_facade.retrieve_user.return_value = user
        self.testcommand.handle('user view --slack_id ABCDE8FA9',
                                user_id, "C0LAN2Q65")
        self.mock_facade.retrieve_user.\
            assert_called_once_with("ABCDE8FA9")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(user.get_md_table(), "C0LAN2Q65")

    def test_handle_view_lookup_error(self):
        """Test user command view handle with user not in database."""
        user_id = "U0G9QF9C6"
        self.mock_facade.retrieve_user.side_effect = LookupError
        self.testcommand.handle('user view --slack_id ABCDE8FA9',
                                user_id, "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("ABCDE8FA9")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(UserCommand.lookup_error, "C0LAN2Q65")

    def test_handle_help(self):
        """Test user command help parser."""
        self.testcommand.handle('user help', "U0G9QF9C6", "C0LAN2Q65")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(UserCommand.help, "C0LAN2Q65")

    def test_handle_delete(self):
        """Test user command delete parser."""
        user = User("ABCDEFG2F")
        user.set_permissions_level(Permissions.admin)
        self.mock_facade.retrieve_user.return_value = user
        message = "Deleted user with Slack ID: " + "U0G9QF9C6"
        self.testcommand.handle("user delete U0G9QF9C6",
                                "ABCDEFG2F", "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("ABCDEFG2F")
        self.mock_facade.delete_user.assert_called_once_with("U0G9QF9C6")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(message, "C0LAN2Q65")

    def test_handle_delete_not_admin(self):
        """Test user command delete where user is not admin."""
        user = User("ABCDEFG2F")
        user.set_permissions_level(Permissions.member)
        self.mock_facade.retrieve_user.return_value = user
        self.testcommand.handle("user delete U0G9QF9C6",
                                "ABCDEFG2F", "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("ABCDEFG2F")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(UserCommand.permission_error, "C0LAN2Q65")
        self.mock_facade.delete_user.assert_not_called()

    def test_handle_delete_lookup_error(self):
        """Test user command delete parser."""
        user = User("ABCDEFG2F")
        user.set_permissions_level(Permissions.admin)
        self.mock_facade.retrieve_user.return_value = user
        self.mock_facade.delete_user.side_effect = LookupError
        self.testcommand.handle("user delete U0G9QF9C6",
                                "ABCDEFG2F", "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("ABCDEFG2F")
        self.mock_facade.delete_user.assert_called_once_with("U0G9QF9C6")
        self.mock_bot.send_to_channel.\
            assert_called_once_with(UserCommand.lookup_error, "C0LAN2Q65")

    def test_handle_edit_name(self):
        """Test user command edit parser with one field."""
        user = User("U0G9QF9C6")
        self.mock_facade.retrieve_user.return_value = user
        self.testcommand.handle("user edit --name rob", "U0G9QF9C6",
                                "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("U0G9QF9C6")
        user.set_name("rob")
        self.mock_facade.store_user.assert_called_once_with(user)
        self.mock_bot.send_to_channel.\
            assert_called_once_with("User edited: " + str(user), "C0LAN2Q65")

    def test_handle_edit_other_user(self):
        """Test user command edit parser with all fields."""
        user = User("ABCDE89JK")
        user.set_permissions_level(Permissions.admin)
        self.mock_facade.retrieve_user.return_value = user
        self.testcommand.handle("user edit --member U0G9QF9C6 "
                                "--name rob "
                                "--email rob@rob.com --pos dev --github"
                                " rob@.github.com --major 'Computer Science'"
                                " --bio 'Im a human'",
                                "U0G9QF9C6", "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_any_call("U0G9QF9C6")
        self.mock_facade.retrieve_user.assert_any_call("U0G9QF9C6")
        user.set_name("rob")
        user.set_email("rob@rob.com")
        user.set_position("dev")
        user.set_github_username("rob@.github.com")
        user.set_major("Computer Science")
        user.set_biography("Im a human")
        self.mock_facade.store_user.assert_called_once_with(user)
        self.mock_bot.send_to_channel.\
            assert_called_once_with("User edited: " + str(user), "C0LAN2Q65")

    def test_handle_edit_not_admin(self):
        """Test user command with editor user that is not admin."""
        user_editor = User("U0G9QF9C6")
        user_editor.set_permissions_level(Permissions.member)
        self.mock_facade.retrieve_user.return_value = user_editor
        self.testcommand.handle("user edit --member ABCDE89JK "
                                "--name rob "
                                "--email rob@rob.com --pos dev --github"
                                " rob@.github.com --major 'Computer Science'"
                                " --bio 'Im a human'",
                                "U0G9QF9C6", "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("U0G9QF9C6")
        self.mock_bot.send_to_channel. \
            assert_called_once_with(UserCommand.permission_error, "C0LAN2Q65")
        self.mock_facade.store_user.assert_not_called()

    def test_handle_edit_lookup_error_editor(self):
        """Test user command where user editor is not in database."""
        user_editor = User("U0G9QF9C6")
        self.mock_facade.retrieve_user.return_value = user_editor
        self.mock_facade.retrieve_user.side_effect = LookupError
        self.testcommand.handle("user edit --member ABCDE89JK "
                                "--name rob "
                                "--email rob@rob.com --pos dev --github"
                                " rob@.github.com --major 'Computer Science'"
                                " --bio 'Im a human'",
                                "U0G9QF9C6", "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("U0G9QF9C6")
        self.mock_bot.send_to_channel. \
            assert_called_once_with(UserCommand.lookup_error, "C0LAN2Q65")
        self.mock_facade.store_user.assert_not_called()

    def test_handle_edit_lookup_error(self):
        """Test user command where user is not in database."""
        user = User("U0G9QF9C6")
        self.mock_facade.retrieve_user.return_value = user
        self.mock_facade.retrieve_user.side_effect = LookupError
        self.testcommand.handle("user edit --name rob", "U0G9QF9C6",
                                "C0LAN2Q65")
        self.mock_facade.retrieve_user.assert_called_once_with("U0G9QF9C6")
        self.mock_bot.send_to_channel. \
            assert_called_once_with(UserCommand.lookup_error, "C0LAN2Q65")
        self.mock_facade.store_user.assert_not_called()
