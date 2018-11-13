"""Test user command parsing."""
from command.commands.user import UserCommand
from unittest import mock
from model.user import User
from db.facade import DBFacade
from model.permissions import Permissions
from bot.bot import Bot


def test_get_command_name():
    """Test user command get_name method."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.get_name() == "user"


def test_get_help():
    """Test user command get_help method."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.get_help() == UserCommand.help


def test_handle_nosubs():
    """Test user with no sub-parsers."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.handle('user', "U0G9QF9C6",
                              "C0LAN2Q65") == UserCommand.help


def test_handle_bad_args():
    """Test user with invalid arguments."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.handle('user geese',
                              "U0G9QF9C6", "C0LAN2Q65") == UserCommand.help


def test_handle_bad_optional_args():
    """Test user edit with invalid optional arguments."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.handle('user edit --biology stuff',
                              "U0G9QF9C6", "C0LAN2Q65") == UserCommand.help


def test_handle_view():
    """Test user command view parser and handle method."""
    mock_facade = mock.MagicMock(DBFacade)
    user_id = "U0G9QF9C6"
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.handle('user view --slack_id asd', user_id,
                              "C0LAN2Q65") == "asd"
    assert testcommand.handle('user view', user_id, "C0LAN2Q65") == "U0G9QF9C6"


def test_handle_help():
    """Test user command help parser."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.handle('user help', "U0G9QF9C6",
                              "C0LAN2Q65") == UserCommand.help


def test_handle_delete():
    """Test user command delete parser."""
    mock_bot = mock.MagicMock(Bot)
    mock_facade = mock.MagicMock(DBFacade)
    testcommand = UserCommand(mock_facade, mock_bot)
    user = User("ABCDEFG2F")
    user.set_permissions_level(Permissions.admin)
    mock_facade.retrieve_user.return_value = user
    message = "Deleted user with Slack ID: " + "U0G9QF9C6"
    testcommand.handle("user delete U0G9QF9C6", "ABCDEFG2F", "C0LAN2Q65")
    mock_facade.retrieve_user.assert_called_once_with("ABCDEFG2F")
    mock_facade.delete_user.assert_called_once_with("U0G9QF9C6")
    mock_bot.send_to_channel.assert_called_once_with(message, "C0LAN2Q65")


def test_handle_edit_name():
    """Test user command edit parser with one field."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.handle("user edit --name rob", "U0G9QF9C6",
                              "C0LAN2Q65") == "user edited: name: rob, "


def test_handle_edit():
    """Test user command edit parser with all fields."""
    result = "user edited: member: id, name: rob, email: rob@rob.com, " \
             "position: dev, github: rob@.github.com, major: Computer " \
             "Science, bio: Im a human"
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    testcommand = UserCommand(mock_facade, mock_bot)
    assert testcommand.handle("user edit --name rob --member id "
                              "--email rob@rob.com --pos "
                              "dev --github rob@.github.com "
                              "--major 'Computer Science' "
                              "--bio 'Im a human'",
                              "U0G9QF9C6", "C0LAN2Q65") == result
