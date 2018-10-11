"""Test the data model for a Slack Event."""
import json
from model.slackevent import SlackEvent


testevent = """
        {
        "token": "z26uFbvR1xHJEdHE1OQiO6t8",
        "team_id": "T061EG9RZ",
        "api_app_id": "A0FFV41KK",
        "event": {
                "type": "reaction_added",
                "user": "U061F1EUR",
                "item": {
                        "type": "message",
                        "channel": "C061EG9SL",
                        "ts": "1464196127.000002"
                        },
                "reaction": "slightly_smiling_face",
                "item_user": "U0M4RL1NY",
                "event_ts": "1465244570.336841"
                 },
        "type": "event_callback",
        "authed_users": [
                "U061F7AUR"
                        ],
        "event_id": "Ev9UQ52YNA",
        "event_time": 1234567890
      }
      """


def test_deserialize():
    """Test the SlackEvent class method deserialize()."""
    event = SlackEvent(testevent)
    assert event.deserialize() == testevent


def test_get_token():
    """Test the SlackEvent class method get_token()."""
    event = SlackEvent(testevent)
    assert event.get_token() == "z26uFbvR1xHJEdHE1OQiO6t8"


def test_get_team_id():
    """Test the SlackEvent class method get_team_id()."""
    event = SlackEvent(testevent)
    assert event.get_team_id() == "T061EG9RZ"


def test_get_api_app_id():
    """Test the SlackEvent class method get_api_app_id()."""
    event = SlackEvent(testevent)
    assert event.get_api_app_id() == "A0FFV41KK"


def test_get_type():
    """Test the SlackEvent class method get_type()."""
    event = SlackEvent(testevent)
    assert event.get_type() == "event_callback"


def test_get_authed_users():
    """Test the SlackEvent class method get_authed_users()."""
    event = SlackEvent(testevent)
    assert event.get_authed_users() == ["U061F7AUR"]


def test_get_event_id():
    """Test the SlackEvent class method get_event_id()."""
    event = SlackEvent(testevent)
    assert event.get_event_id() == "Ev9UQ52YNA"


def test_get_event_time():
    """Test the SlackEvent class method get_event_time()."""
    event = SlackEvent(testevent)
    assert event.get_event_time() == 1234567890


def test_get_event_obj():
    """Test the SlackEvent class method get_event_obj()."""
    event = SlackEvent(testevent)
    dictionary = {
                "type": "reaction_added",
                "user": "U061F1EUR",
                "item": {
                        "type": "message",
                        "channel": "C061EG9SL",
                        "ts": "1464196127.000002"
                        },
                "reaction": "slightly_smiling_face",
                "item_user": "U0M4RL1NY",
                "event_ts": "1465244570.336841"
                 }
    assert event.get_event_obj() == dictionary


def test_get_event_attr():
    """Test the SlackEvent class method get_event_attr()."""
    event = SlackEvent(testevent)
    assert event.get_event_attr("type") == "reaction_added"
    assert event.get_event_attr("user") == "U061F1EUR"
    assert event.get_event_attr("reaction") == "slightly_smiling_face"
    assert event.get_event_attr("item_user") == "U0M4RL1NY"
    assert event.get_event_attr("event_ts") == "1465244570.336841"
    t = {"type": "message", "channel": "C061EG9SL", "ts": "1464196127.000002"}
    assert event.get_event_attr("item") == t
