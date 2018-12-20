"""Test the core event handler."""
from unittest import mock
from command.core import Core
from bot.bot import Bot, SlackAPIError
from db.facade import DBFacade
from slackclient import SlackClient


@mock.patch('command.core.logging')
def test_handle_invalid_mention(mock_logging):
    """Test the instance of handle_app_mention being called inappropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    event = {
        "token": "XXYYZZ",
        "team_id": "TXXXXXXXX",
        "api_app_id": "AXXXXXXXXX",
        "event": {
            "type": "app_mention",
            "user": "U061F7AUR",
            "text": "hello world",
            "ts": "1515449522.000016",
            "channel": "C0LAN2Q65",
            "event_ts": "1515449522000016"
        },
        "type": "app_mention",
        "authed_users": ["UXXXXXXX1", "UXXXXXXX2"],
        "event_id": "Ev08MFMKH6",
        "event_time": 1234567890
    }
    core = Core(mock_bot, mock_facade)
    core.handle_app_mention(event)
    expected_log_message = "app mention event triggered incorrectly"
    mock_logging.error.assert_called_once_with(expected_log_message)


@mock.patch('command.core.UserCommand')
@mock.patch('command.core.logging')
def test_handle_invalid_command(mock_logging, mock_usercommand):
    """Test that invalid commands are being handled appropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    mock_usercommand.handle.side_effect = KeyError
    event = {
        "token": "XXYYZZ",
        "team_id": "TXXXXXXXX",
        "api_app_id": "AXXXXXXXXX",
        "event": {
            "type": "app_mention",
            "user": "U061F7AUR",
            "text": "@rocket fake command",
            "ts": "1515449522.000016",
            "channel": "C0LAN2Q65",
            "event_ts": "1515449522000016"
        },
        "type": "app_mention",
        "authed_users": ["UXXXXXXX1", "UXXXXXXX2"],
        "event_id": "Ev08MFMKH6",
        "event_time": 123456789
    }
    core = Core(mock_facade, mock_bot)
    core.handle_app_mention(event)
    error_dm = "Please enter a valid command."
    user = event["event"]["user"]
    mock_bot.send_dm.assert_called_once_with(error_dm, user)
    event_text = event["event"]["text"]
    expected_log_message = ("@rocket mention - "
                            "invalid request: ") + event_text
    mock_logging.info.assert_called_once_with(expected_log_message)


@mock.patch('command.core.UserCommand')
@mock.patch('command.core.logging')
def test_handle_user_command(mock_logging, mock_usercommand):
    """Test that UserCommand.handle is called appropriately."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
    event = {
        "token": "XXYYZZ",
        "team_id": "TXXXXXXXX",
        "api_app_id": "AXXXXXXXXX",
        "event": {
            "type": "app_mention",
            "user": "U061F7AUR",
            "text": "@rocket user name",
            "ts": "1515449522.000016",
            "channel": "C0LAN2Q65",
            "event_ts": "1515449522000016"
        },
        "type": "app_mention",
        "authed_users": ["UXXXXXXX1", "UXXXXXXX2"],
        "event_id": "Ev08MFMKH6",
        "event_time": 1234567890
    }
    core = Core(mock_facade, mock_bot)
    core.handle_app_mention(event)
    mock_usercommand.\
        return_value.handle.\
        assert_called_once_with("user name", "U061F7AUR", "C0LAN2Q65")
    event_text = event["event"]["text"]
    expected_log_message = ("@rocket mention - "
                            "successfully handled request: ") + event_text
    mock_logging.info.assert_called_once_with(expected_log_message)


@mock.patch('command.core.logging')
def test_handle_team_join_success(mock_logging):
    """Test that the join handler adds users to the db successfully."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_bot = mock.MagicMock(Bot)
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
    core = Core(mock_facade, mock_bot)
    core.handle_team_join(event)
    welcome = 'Welcome to Lauchpad!'
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
    core = Core(mock_facade, mock_bot)
    core.handle_team_join(event)
    welcome = 'Welcome to Lauchpad!'
    id = "W012A3CDE"
    mock_bot.send_dm.assert_called_once_with(welcome, id)
    expected_log_message = ("W012A3CDE added to database - "
                            "user not notified")
    mock_logging.error.assert_called_once_with(expected_log_message)
