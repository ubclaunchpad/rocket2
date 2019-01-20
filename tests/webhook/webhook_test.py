"""Test the webhook handler."""
import json
import pytest
from unittest import mock
from model.user import User
from webhook.webhook import WebhookHandler
from db.facade import DBFacade


@pytest.fixture
def org_default_payload_string():
    """Provide the basic structure for an organization payload."""
    default_payload =\
        """
            {
                "action": "member_added",
                "membership": {
                    "url": "",
                    "state": "pending",
                    "role": "member",
                    "organization_url": "",
                    "user": {
                        "login": "hacktocat",
                        "id": 39652351,
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
                        "site_admin": false
                    }
                },
                "organization": {
                    "login": "Octocoders",
                    "id": 38302899,
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
                    "id": 21031067,
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
                    "site_admin": false
                }
            }
        """
    return default_payload


@pytest.fixture
def org_add_payload(org_default_payload_string):
    """Provide an organization payload for adding a member."""
    add_payload = json.loads(org_default_payload_string)
    add_payload["action"] = "member_added"
    return json.dumps(add_payload)


@pytest.fixture
def org_rm_payload(org_default_payload_string):
    """Provide an organization payload for removing a member."""
    rm_payload = json.loads(org_default_payload_string)
    rm_payload["action"] = "member_removed"
    return json.dumps(rm_payload)


@pytest.fixture
def org_inv_payload(org_default_payload_string):
    """Provide an organization payload for inviting a member."""
    inv_payload = json.loads(org_default_payload_string)
    inv_payload["action"] = "member_invited"
    return json.dumps(inv_payload)


@pytest.fixture
def org_empty_payload(org_default_payload_string):
    """Provide an organization payload with no action."""
    empty_payload = json.loads(org_default_payload_string)
    empty_payload["action"] = ""
    return json.dumps(empty_payload)


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_add_member(mock_logging, org_add_payload):
    """Test that instances when members are added to the org are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(org_add_payload)
    mock_logging.info.assert_called_once_with(("user hacktocat added "
                                               "to organization"))


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_rm_single_member(mock_logging, org_rm_payload):
    """Test that members removed from the org are deleted from rocket's db."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    mock_facade.query_user.return_value = [return_user]
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(org_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_id', 39652351])
    mock_facade.delete_user.assert_called_once_with("SLACKID")
    mock_logging.info.assert_called_once_with("deleted slack user SLACKID")


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_rm_member_missing(mock_logging, org_rm_payload):
    """Test that members not in rocket db are handled correctly."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query_user.return_value = []
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(org_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_id', 39652351])
    mock_logging.error.assert_called_once_with("could not find user 39652351")


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_rm_mult_members(mock_logging, org_rm_payload):
    """Test that multiple members with the same github name can be deleted."""
    mock_facade = mock.MagicMock(DBFacade)
    user1 = User("SLACKUSER1")
    user2 = User("SLACKUSER2")
    user3 = User("SLACKUSER3")
    mock_facade.query_user.return_value = [user1, user2, user3]
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(org_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_id', 39652351])
    assert mock_facade.delete_user.call_count is 3
    assert mock_logging.info.call_count is 3


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_inv_member(mock_logging, org_inv_payload):
    """Test that instances when members are added to the org are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(org_inv_payload)
    mock_logging.info.assert_called_once_with(("user hacktocat invited "
                                               "to organization"))


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_empty_action(mock_logging, org_empty_payload):
    """Test that instances where there is no/invalid action are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(org_empty_payload)
    mock_logging.error.assert_called_once_with(("organization webhook "
                                                "triggered, invalid "
                                                "action specified"))
