"""Test the handler for GitHub membership events."""
import pytest

from db import DBFacade
from app.model import User, Team
from unittest import mock
from app.controller.webhook.github.events import MembershipEventHandler


@pytest.fixture
def mem_default_payload():
    """Provide the basic structure for a membership payload."""
    default_payload =\
        {
            "action": "removed",
            "scope": "team",
            "member": {
                "login": "Codertocat",
                "id": "21031067",
                "node_id": "MDQ6VXNlcjIxMDMxMDY3",
                "avatar_url": "",
                "gravatar_id": "",
                "url": "",
                "html_url": "",
                "followers_url": "",
                "following_url": "",
                "gists_url": "",
                "starred_url": "",
                "subscriptions_url": "",
                "organizations_url": "",
                "repos_url": "",
                "events_url": "",
                "received_events_url": "",
                "type": "User",
                "site_admin": False
            },
            "sender": {
                "login": "Codertocat",
                "id": "21031067",
                "node_id": "MDQ6VXNlcjIxMDMxMDY3",
                "avatar_url": "",
                "gravatar_id": "",
                "url": "",
                "html_url": "",
                "followers_url": "",
                "following_url": "",
                "gists_url": "",
                "starred_url": "",
                "subscriptions_url": "",
                "organizations_url": "",
                "repos_url": "",
                "events_url": "",
                "received_events_url": "",
                "type": "User",
                "site_admin": False
            },
            "team": {
                "name": "rocket",
                "id": "2723476",
                "node_id": "MDQ6VGVhbTI3MjM0NzY=",
                "slug": "rocket",
                "description": "hub hub hubber-one",
                "privacy": "closed",
                "url": "",
                "members_url": "",
                "repositories_url": "",
                "permission": "pull"
            },
            "organization": {
                "login": "Octocoders",
                "id": "38302899",
                "node_id": "",
                "url": "",
                "repos_url": "",
                "events_url": "",
                "hooks_url": "",
                "issues_url": "",
                "members_url": "",
                "public_members_url": "",
                "avatar_url": "",
                "description": ""
            }
        }
    return default_payload


@pytest.fixture
def mem_add_payload(mem_default_payload):
    """Provide a membership payload for adding a member."""
    add_payload = mem_default_payload
    add_payload["action"] = "added"
    return add_payload


@pytest.fixture
def mem_rm_payload(mem_default_payload):
    """Provide a membership payload for removing a member."""
    rm_payload = mem_default_payload
    rm_payload["action"] = "removed"
    return rm_payload


@pytest.fixture
def mem_empty_payload(mem_default_payload):
    """Provide a membership payload with no action."""
    empty_payload = mem_default_payload
    empty_payload["action"] = ""
    return empty_payload


def test_org_supported_action_list():
    """Confirm the supported action list of the handler."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = MembershipEventHandler(mock_facade)
    assert webhook_handler.supported_action_list == ["removed",
                                                     "added"]


@mock.patch('app.controller.webhook.github.events.membership.logging')
def test_handle_mem_event_add_member(mock_logging, mem_add_payload):
    """Test that instances when members are added to the mem are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    return_team = Team("2723476", "rocket", "rocket")
    return_team.add_member("SLACKID")
    mock_facade.query.return_value = [return_user]
    mock_facade.retrieve.return_value = return_team
    webhook_handler = MembershipEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(mem_add_payload)
    mock_facade.store.assert_called_once_with(return_team)
    mock_logging.info.assert_called_once_with(("user Codertocat added "
                                               "to rocket"))
    assert rsp == "added slack ID SLACKID"
    assert code == 200


@mock.patch('app.controller.webhook.github.events.membership.logging')
def test_handle_mem_event_add_missing_member(mock_logging, mem_add_payload):
    """Test that instances when members are added to the mem are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query.return_value = []
    webhook_handler = MembershipEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(mem_add_payload)
    mock_logging.error.assert_called_once_with("could not find user 21031067")
    assert rsp == "could not find user Codertocat"
    assert code == 404


@mock.patch('app.controller.webhook.github.events.membership.logging')
def test_handle_mem_event_rm_single_member(mock_logging, mem_rm_payload):
    """Test that members removed from the mem are deleted from rocket's db."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    return_team = Team("2723476", "rocket", "rocket")
    return_team.add_member("21031067")
    mock_facade.query.return_value = [return_user]
    mock_facade.retrieve.return_value = return_team
    webhook_handler = MembershipEventHandler(mock_facade)
    (rsp, code) = webhook_handler.handle(mem_rm_payload)
    mock_facade.query\
        .assert_called_once_with(User, [('github_user_id', "21031067")])
    mock_facade.retrieve \
        .assert_called_once_with(Team, "2723476")
    mock_facade.store.assert_called_once_with(return_team)
    mock_logging.info.assert_called_once_with("deleted slack user SLACKID"
                                              " from rocket")
    assert not return_team.has_member("21031067")
    assert rsp == "deleted slack ID SLACKID from rocket"
    assert code == 200


@mock.patch('app.controller.webhook.github.events.membership.logging')
def test_handle_mem_event_rm_member_missing(mock_logging, mem_rm_payload):
    """Test that members not in rocket db are handled correctly."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    return_team = Team("2723476", "rocket", "rocket")
    mock_facade.query.return_value = [return_user]
    mock_facade.retrieve.return_value = return_team
    webhook_handler = MembershipEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(mem_rm_payload)
    mock_facade.query\
        .assert_called_once_with(User, [('github_user_id', "21031067")])
    mock_logging.error.assert_called_once_with("slack user SLACKID "
                                               "not in rocket")
    assert rsp == "slack user SLACKID not in rocket"
    assert code == 404


@mock.patch('app.controller.webhook.github.events.membership.logging')
def test_handle_mem_event_rm_member_wrong_team(mock_logging, mem_rm_payload):
    """Test what happens when member removed from a team they are not in."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query.return_value = []
    webhook_handler = MembershipEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(mem_rm_payload)
    mock_facade.query\
        .assert_called_once_with(User, [('github_user_id', "21031067")])
    mock_logging.error.assert_called_once_with("could not find user 21031067")
    assert rsp == "could not find user 21031067"
    assert code == 404


@mock.patch('app.controller.webhook.github.events.membership.logging')
def test_handle_mem_event_rm_mult_members(mock_logging, mem_rm_payload):
    """Test that multiple members with the same github name can be deleted."""
    mock_facade = mock.MagicMock(DBFacade)
    user1 = User("SLACKUSER1")
    user2 = User("SLACKUSER2")
    user3 = User("SLACKUSER3")
    mock_facade.query.return_value = [user1, user2, user3]
    webhook_handler = MembershipEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(mem_rm_payload)
    mock_facade.query\
        .assert_called_once_with(User, [('github_user_id', "21031067")])
    mock_logging.error.assert_called_once_with("Error: found github ID "
                                               "connected to multiple"
                                               " slack IDs")
    assert rsp == "Error: found github ID connected to multiple slack IDs"
    assert code == 412


@mock.patch('app.controller.webhook.github.events.membership.logging')
def test_handle_mem_event_empty_action(mock_logging, mem_empty_payload):
    """Test that instances where there is no/invalid action are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = MembershipEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(mem_empty_payload)
    mock_logging.error.assert_called_once_with(("membership webhook "
                                                "triggered, invalid "
                                                "action specified: {}"
                                                .format(mem_empty_payload)))
    assert rsp == "invalid membership webhook triggered"
    assert code == 405
