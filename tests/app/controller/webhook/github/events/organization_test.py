"""Test the handler for GitHub organization events."""
import pytest

from db import DBFacade
from app.model import User
from unittest import mock
from app.controller.webhook.github.events import OrganizationEventHandler


@pytest.fixture
def org_default_payload():
    """Provide the basic structure for an organization payload."""
    default_payload =\
        {
            "action": "member_added",
            "membership": {
                "url": "",
                "state": "pending",
                "role": "member",
                "organization_url": "",
                "user": {
                    "login": "hacktocat",
                    "id": "39652351",
                    "node_id": "MDQ6VXNlcjM5NjUyMzUx",
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
                }
            },
            "organization": {
                "login": "Octocoders",
                "id": "38302899",
                "node_id": "MDEyOk9yZ2FuaXphdGlvbjM4MzAyODk5",
                "url": "",
                "repos_url": "",
                "events_url": "",
                "hooks_url": "",
                "issues_url": "",
                "members_url": "",
                "public_members_url": "",
                "avatar_url": "",
                "description": ""
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
            }
        }
    return default_payload


@pytest.fixture
def org_add_payload(org_default_payload):
    """Provide an organization payload for adding a member."""
    add_payload = org_default_payload
    add_payload["action"] = "member_added"
    return add_payload


@pytest.fixture
def org_rm_payload(org_default_payload):
    """Provide an organization payload for removing a member."""
    rm_payload = org_default_payload
    rm_payload["action"] = "member_removed"
    return rm_payload


@pytest.fixture
def org_empty_payload(org_default_payload):
    """Provide an organization payload with no action."""
    empty_payload = org_default_payload
    empty_payload["action"] = ""
    return empty_payload


def test_org_supported_action_list():
    """Confirm the supported action list of the handler."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = OrganizationEventHandler(mock_facade)
    assert webhook_handler.supported_action_list == ["member_removed",
                                                     "member_added"]


def test_handle_org_event_add_member(org_add_payload):
    """Test that instances when members are added to the org are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = OrganizationEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(org_add_payload)
    assert rsp == "user hacktocat added to Octocoders"
    assert code == 200


def test_handle_org_event_rm_single_member(org_rm_payload):
    """Test that members removed from the org are deleted from rocket's db."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    mock_facade.query.return_value = [return_user]
    webhook_handler = OrganizationEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(org_rm_payload)
    mock_facade.query\
        .assert_called_once_with(User, [('github_user_id', "39652351")])
    mock_facade.delete.assert_called_once_with(User, "SLACKID")
    assert rsp == "deleted slack ID SLACKID"
    assert code == 200


def test_handle_org_event_rm_member_missing(org_rm_payload):
    """Test that members not in rocket db are handled correctly."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query.return_value = []
    webhook_handler = OrganizationEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(org_rm_payload)
    mock_facade.query\
        .assert_called_once_with(User, [('github_user_id', "39652351")])
    assert rsp == "could not find user hacktocat"
    assert code == 404


def test_handle_org_event_rm_mult_members(org_rm_payload):
    """Test that multiple members with the same github name can be deleted."""
    mock_facade = mock.MagicMock(DBFacade)
    user1 = User("SLACKUSER1")
    user2 = User("SLACKUSER2")
    user3 = User("SLACKUSER3")
    mock_facade.query.return_value = [user1, user2, user3]
    webhook_handler = OrganizationEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(org_rm_payload)
    mock_facade.query\
        .assert_called_once_with(User, [('github_user_id', "39652351")])
    assert rsp == "Error: found github ID connected to multiple slack IDs"
    assert code == 412


def test_handle_org_event_empty_action(org_empty_payload):
    """Test that instances where there is no/invalid action are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = OrganizationEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(org_empty_payload)
    assert rsp == "invalid organization webhook triggered"
    assert code == 405
