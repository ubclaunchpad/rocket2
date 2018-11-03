"""Test the core event handler."""
from unittest import mock
from command.core import Core


def test_handle_invalid_mention():
    """Test the instance of handle_app_mention being called inappropriately."""
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
    core = Core()
    assert core.handle_app_mention(event) == 0


def test_handle_invalid_command():
    """Test that invalid commands are being handled appropriately."""
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
    core = Core()
    assert core.handle_app_mention(event) == -1


@mock.patch('command.core.UserCommand')
def test_handle_user_command(MockUserCommand):
    """Test that UserCommand.handle is called appropriately."""
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
    core = Core()
    assert core.handle_app_mention(event) == 1
    MockUserCommand.return_value.handle.assert_called_once_with("user name", "U061F7AUR")
