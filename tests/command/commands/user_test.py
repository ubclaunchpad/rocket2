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
            assert_called_once_with('', "C0LAN2Q65", [user.get_attachment()])

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
            assert_called_once_with('', "C0LAN2Q65", [user.get_attachment()])

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
        message = "You do not have the sufficient " \
                  "permission level for this command!"
        self.mock_bot.send_to_channel.\
            assert_called_once_with(message, "C0LAN2Q65")
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
        assert self.testcommand.handle("user edit --name rob", "U0G9QF9C6",
                                       "C0LAN2Q65") == \
            "user edited: name: rob, "

    def test_handle_edit(self):
        """Test user command edit parser with all fields."""
        result = "user edited: member: id, name: rob, email: rob@rob.com, " \
                 "position: dev, github: rob@.github.com, major: Computer " \
                 "Science, bio: Im a human"
        assert self.testcommand.handle(
                                  "user edit --name rob --member id "
                                  "--email rob@rob.com --pos "
                                  "dev --github rob@.github.com "
                                  "--major 'Computer Science' "
                                  "--bio 'Im a human'",
                                  "U0G9QF9C6", "C0LAN2Q65") == result
