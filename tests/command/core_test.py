"""Test the core event handler."""
from unittest import mock
from command.core import Core


def test_handle_invalid_mention():
    """Test the instance of handle_app_mention being called inappropriately."""
    event = {}
    event["token"] = "XXYYZZ"
    event["team_id"] = "TXXXXXXXX"
    event["api_app_id"] = "AXXXXXXXXX"
    inner_event = {}
    inner_event["type"] = "app_mention"
    inner_event["user"] = "U061F7AUR"
    inner_event["text"] = "hello world"
    inner_event["ts"] = "1515449522.000016"
    inner_event["channel"] = "C0LAN2Q65"
    inner_event["event_ts"] = "1515449522000016"
    event["event"] = inner_event
    event["type"] = "app_mention"
    event["authed_users"] = ["UXXXXXXX1", "UXXXXXXX2"]
    event["event_id"] = "Ev08MFMKH6"
    event["event_time"] = 1234567890
    core = Core()
    assert not core.handle_app_mention(event)


@mock.patch('command.core.UserCommand')
def test_handle_user_command(MockUserCommand):
    """Test that UserCommand.handle is called appropriately."""
    event = {}
    event["token"] = "XXYYZZ"
    event["team_id"] = "TXXXXXXXX"
    event["api_app_id"] = "AXXXXXXXXX"
    inner_event = {}
    inner_event["type"] = "app_mention"
    inner_event["user"] = "U061F7AUR"
    inner_event["text"] = "@rocket user name"
    inner_event["ts"] = "1515449522.000016"
    inner_event["channel"] = "C0LAN2Q65"
    inner_event["event_ts"] = "1515449522000016"
    event["event"] = inner_event
    event["type"] = "app_mention"
    event["authed_users"] = ["UXXXXXXX1", "UXXXXXXX2"]
    event["event_id"] = "Ev08MFMKH6"
    event["event_time"] = 1234567890
    core = Core()
    assert core.handle_app_mention(event)
    MockUserCommand.return_value.handle.assert_called_once_with("user name")
