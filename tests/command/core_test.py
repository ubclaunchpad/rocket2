"""Test the core event handler."""
from unittest import mock
from command.core import Core
from interface.slack import Bot, SlackAPIError
from interface.github import GithubInterface
from db.facade import DBFacade
from slackclient import SlackClient
from command.commands.user import UserCommand
import json


@mock.patch('command.core.logging')
def test_handle_invalid_mention(mock_logging):
    """Test the instance of handle_app_command being called inappropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    core = Core(mock_facade, mock_bot, mock_gh)
    core.handle_app_command('hello world', 'U061F7AUR')
    expected_log_message = "app command triggered incorrectly"
    mock_logging.error.assert_called_once_with(expected_log_message)


@mock.patch('command.core.UserCommand')
@mock.patch('command.core.logging')
def test_handle_invalid_command(mock_logging, mock_usercommand):
    """Test that invalid commands are being handled appropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_usercommand.handle.side_effect = KeyError
    user = 'U061F7AUR'
    core = Core(mock_facade, mock_bot, mock_gh)
    core.handle_app_command('fake command', user)
    error_txt = "Please enter a valid command."


@mock.patch('command.core.logging')
def test_handle_help(mock_logging,):
    """Test that a '/rocket help' brings up help"""
    mock_usercommand = mock.MagicMock(UserCommand)
    mock_usercommand.get_name.return_value = "user"
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    core = Core(mock_facade, mock_bot, mock_gh)
    reply, code = core.handle_app_command("help", "U061F7AUR")
    expect = json.dumps({
        "text": "Displaying all available commands. To read about"
                "a specific command, use `/rocket COMMAND help`\n",
        "mrkdwn": "true",
        "attachments": [{"text": ["*[USER]*\n\nCommands for editing",
                                  "users."], "mrkdwn_in": ["text"]}]})
    assert reply == expect


@mock.patch('command.core.UserCommand')
@mock.patch('command.core.logging')
def test_handle_user_command(mock_logging, mock_usercommand):
    """Test that UserCommand.handle is called appropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    core = Core(mock_facade, mock_bot, mock_gh)
    core.handle_app_command('user name', 'U061F7AUR')
    mock_usercommand.\
        return_value.handle.\
        assert_called_once_with("user name", "U061F7AUR")


@mock.patch('command.core.logging')
def test_handle_team_join_success(mock_logging):
    """Test that the join handler adds users to the db successfully."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    event = {
        "token": "XXYYZZ",
        "team_id": "TXXXXXXXX",
        "api_app_id": "AXXXXXXXXX",
        "event": {
            "type": "team_join",
            "user": {
                "id": "W012A3CDE",
                "team_id": "T012AB3C4",
                "name": "spengler",
                "deleted": False,
                "color": "9f69e7",
                "real_name": "Egon Spengler",
                "tz": "America/Los_Angeles",
                "tz_label": "Pacific Daylight Time",
                "tz_offset": -25200,
                "profile": {
                    "avatar_hash": "ge3b51ca72de",
                    "status_text": "Print is dead",
                    "status_emoji": ":books:",
                    "status_expiration": 1502138999,
                    "real_name": "Egon Spengler",
                    "display_name": "spengler",
                    "real_name_normalized": "Egon Spengler",
                    "display_name_normalized": "spengler",
                    "email": "spengler@ghostbusters.example.com",
                    "image_24": "https://.../avatar/hello.jpg",
                    "image_32": "https://.../avatar/hello.jpg",
                    "image_48": "https://.../avatar/hello.jpg",
                    "image_72": "https://.../avatar/hello.jpg",
                    "image_192": "https://.../avatar/hello.jpg",
                    "image_512": "https://.../avatar/hello.jpg",
                    "team": "T012AB3C4"
                },
                "is_admin": True,
                "is_owner": False,
                "is_primary_owner": False,
                "is_restricted": False,
                "is_ultra_restricted": False,
                "is_bot": False,
                "is_stranger": False,
                "updated": 1502138686,
                "is_app_user": False,
                "has_2fa": False,
                "locale": "en-US"
            }
        },
        "type": "app_mention",
        "authed_users": ["UXXXXXXX1", "UXXXXXXX2"],
        "event_id": "Ev08MFMKH6",
        "event_time": 1234567890
    }
    core = Core(mock_facade, mock_bot, mock_gh)
    core.handle_team_join(event)
    welcome = 'Welcome to UBC Launch Pad!'
    id = "W012A3CDE"
    mock_bot.send_dm.assert_called_once_with(welcome, id)
    expected_log_message = ("W012A3CDE added to database - "
                            "user notified")
    mock_logging.info.assert_called_once_with(expected_log_message)


@mock.patch('command.core.logging')
def test_handle_team_join_slack_error(mock_logging):
    """Test that the join handler handles Slack API errors."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_gh = mock.MagicMock(GithubInterface)
    mock_bot.send_dm.side_effect = SlackAPIError(None)
    event = {
        "token": "XXYYZZ",
        "team_id": "TXXXXXXXX",
        "api_app_id": "AXXXXXXXXX",
        "event": {
            "type": "team_join",
            "user": {
                "id": "W012A3CDE",
                "team_id": "T012AB3C4",
                "name": "spengler",
                "deleted": False,
                "color": "9f69e7",
                "real_name": "Egon Spengler",
                "tz": "America/Los_Angeles",
                "tz_label": "Pacific Daylight Time",
                "tz_offset": -25200,
                "profile": {
                    "avatar_hash": "ge3b51ca72de",
                    "status_text": "Print is dead",
                    "status_emoji": ":books:",
                    "status_expiration": 1502138999,
                    "real_name": "Egon Spengler",
                    "display_name": "spengler",
                    "real_name_normalized": "Egon Spengler",
                    "display_name_normalized": "spengler",
                    "email": "spengler@ghostbusters.example.com",
                    "image_24": "https://.../avatar/hello.jpg",
                    "image_32": "https://.../avatar/hello.jpg",
                    "image_48": "https://.../avatar/hello.jpg",
                    "image_72": "https://.../avatar/hello.jpg",
                    "image_192": "https://.../avatar/hello.jpg",
                    "image_512": "https://.../avatar/hello.jpg",
                    "team": "T012AB3C4"
                },
                "is_admin": True,
                "is_owner": False,
                "is_primary_owner": False,
                "is_restricted": False,
                "is_ultra_restricted": False,
                "is_bot": False,
                "is_stranger": False,
                "updated": 1502138686,
                "is_app_user": False,
                "has_2fa": False,
                "locale": "en-US"
            }
        },
        "type": "app_mention",
        "authed_users": ["UXXXXXXX1", "UXXXXXXX2"],
        "event_id": "Ev08MFMKH6",
        "event_time": 1234567890
    }
    core = Core(mock_facade, mock_bot, mock_gh)
    core.handle_team_join(event)
    welcome = 'Welcome to UBC Launch Pad!'
    id = "W012A3CDE"
    mock_bot.send_dm.assert_called_once_with(welcome, id)
    expected_log_message = ("W012A3CDE added to database - "
                            "user not notified")
    mock_logging.error.assert_called_once_with(expected_log_message)
