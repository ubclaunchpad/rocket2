"""Test the Slack events handler."""
from app.controller.webhook.slack import SlackEventsHandler
from db import DBFacade
from interface.slack import Bot, SlackAPIError
from unittest import mock


def test_handle_team_join_success():
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
    handler = SlackEventsHandler(mock_facade, mock_bot)
    handler.handle_team_join(event)
    welcome = "Welcome to UBC Launch Pad!" + \
              "Please type `/rocket user edit " + \
              "--github <YOUR GITHUB USERNAME>` " + \
              "to add yourself to the GitHub organization."
    id = "W012A3CDE"
    mock_bot.send_dm.assert_called_once_with(welcome, id)


def test_handle_team_join_slack_error():
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
    handler = SlackEventsHandler(mock_facade, mock_bot)
    handler.handle_team_join(event)
    welcome = "Welcome to UBC Launch Pad!" + \
              "Please type `/rocket user edit " + \
              "--github <YOUR GITHUB USERNAME>` " + \
              "to add yourself to the GitHub organization."
    id = "W012A3CDE"
    mock_bot.send_dm.assert_called_once_with(welcome, id)
