"""Test the webhook handler."""
from unittest import mock
from model.user import User
from interface.github.webhook import WebhookHandler
from db.facade import DBFacade


@mock.patch('interface.github.webhook.logging')
def test_handle_org_event_add_member_success(mock_logging):
    """Test that members' github ids are being added to the db correctly."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("slack id")
    return_user.set_github_username("hacktocat")
    mock_facade.query_user.return_value = [return_user]
    payload = \
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
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_name', 'hacktocat'])
    mock_logging.info.\
        assert_called_once_with(("GitHub user hacktocat's GitHub Id set "
                                 "to 39652351"))


@mock.patch('interface.github.webhook.logging')
def test_handle_org_event_add_member_missing(mock_logging):
    """Test that github usernames not being in our db are handled correctly."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query_user.return_value = []
    payload = \
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
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_name', 'hacktocat'])
    mock_logging.error.\
        assert_called_once_with("GitHub user hacktocat could not be found")


@mock.patch('interface.github.webhook.logging')
def test_handle_org_event_add_member_multiple(mock_logging):
    """Test case where multiple users set the same GitHub name is handled."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user_1 = User("slack id 1")
    return_user_2 = User("slack id 2")
    return_user_1.set_github_username("hacktocat")
    return_user_2.set_github_username("hacktocat")
    mock_facade.query_user.return_value = [return_user_1, return_user_2]
    payload = \
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
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_name', 'hacktocat'])
    mock_logging.error.\
        assert_called_once_with(("More than one user with GitHub name "
                                 "hacktocat found"))


@mock.patch('interface.github.webhook.logging')
def test_handle_org_event_rm_member_success(mock_logging):
    """Test that members removed from the org are deleted from rocket's db."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User(39652351)
    mock_facade.query_user.return_value = [return_user]
    payload = \
        """
            {
                "action": "member_removed",
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
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_id', 39652351])
    mock_facade.delete_user.assert_called_once_with(39652351)
    mock_logging.info.assert_called_once_with("deleted user 39652351")


@mock.patch('interface.github.webhook.logging')
def test_handle_org_event_rm_member_missing(mock_logging):
    """Test that members removed from the org are deleted from rocket's db."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query_user.return_value = []
    payload = \
        """
            {
                "action": "member_removed",
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
    webhook_handler = WebhookHandler(mock_facade)
    webhook_handler.handle_organization_event(payload)
    mock_facade.query_user\
        .assert_called_once_with(['github_id', 39652351])
    mock_logging.error.assert_called_once_with("could not find user 39652351")