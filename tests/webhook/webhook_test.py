"""Test the webhook handler."""
import pytest
from unittest import mock
from model.user import User
from model.team import Team
from webhook.webhook import WebhookHandler
from db.facade import DBFacade


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
                    "site_admin": "False"
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
                "site_admin": "False"
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
def org_inv_payload(org_default_payload):
    """Provide an organization payload for inviting a member."""
    inv_payload = org_default_payload
    inv_payload["action"] = "member_invited"
    return inv_payload


@pytest.fixture
def org_empty_payload(org_default_payload):
    """Provide an organization payload with no action."""
    empty_payload = org_default_payload
    empty_payload["action"] = ""
    return empty_payload


@pytest.fixture
def team_default_payload():
    """Provide the basic structure for a team payload."""
    default_payload =\
        {
            "action": "added_to_repository",
            "team": {
                "name": "github",
                "id": 2723476,
                "node_id": "MDQ6VGVhbTI3MjM0NzY=",
                "slug": "github",
                "description": "hub hub hubber-one",
                "privacy": "closed",
                "url": "",
                "members_url": "",
                "repositories_url": "",
                "permission": "pull"
            },
            "repository": {
                "id": 135493281,
                "node_id": "MDEwOlJlcG9zaXRvcnkxMzU0OTMyODE=",
                "name": "Hello-World",
                "full_name": "Octocoders/Hello-World",
                "owner": {
                    "login": "Octocoders",
                    "id": 38302899,
                    "node_id": "MDEyOk9yZ2FuaXphdGlvbjM4MzAyODk5",
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
                    "type": "Organization",
                    "site_admin": False
                },
                "private": False,
                "html_url": "",
                "description": None,
                "fork": True,
                "url": "",
                "forks_url": "",
                "keys_url": "",
                "collaborators_url": "",
                "teams_url": "",
                "hooks_url": "",
                "issue_events_url": "",
                "events_url": "",
                "assignees_url": "",
                "branches_url": "",
                "tags_url": "",
                "blobs_url": "",
                "git_tags_url": "",
                "git_refs_url": "",
                "trees_url": "",
                "statuses_url": "",
                "languages_url": "",
                "stargazers_url": "",
                "contributors_url": "",
                "subscribers_url": "",
                "subscription_url": "",
                "commits_url": "",
                "git_commits_url": "",
                "comments_url": "",
                "issue_comment_url": "",
                "contents_url": "",
                "compare_url": "",
                "merges_url": "",
                "archive_url": "",
                "downloads_url": "",
                "issues_url": "",
                "pulls_url": "",
                "milestones_url": "",
                "notifications_url": "",
                "labels_url": "",
                "releases_url": "",
                "deployments_url": "",
                "created_at": "2018-05-30T20:18:35Z",
                "updated_at": "2018-05-30T20:18:37Z",
                "pushed_at": "2018-05-30T20:18:30Z",
                "git_url": "",
                "ssh_url": "",
                "clone_url": "",
                "svn_url": "",
                "homepage": None,
                "size": 0,
                "stargazers_count": 0,
                "watchers_count": 0,
                "language": None,
                "has_issues": False,
                "has_projects": True,
                "has_downloads": True,
                "has_wiki": True,
                "has_pages": False,
                "forks_count": 0,
                "mirror_url": None,
                "archived": False,
                "open_issues_count": 0,
                "license": None,
                "forks": 0,
                "open_issues": 0,
                "watchers": 0,
                "default_branch": "master",
                "permissions": {
                    "pull": True,
                    "push": False,
                    "admin": False
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
                "site_admin": False
            }
        }
    return default_payload


@pytest.fixture
def team_created_payload(team_default_payload):
    """Provide a team payload for creating a team."""
    created_payload = team_default_payload
    created_payload["action"] = "created"
    return created_payload


@pytest.fixture
def team_deleted_payload(team_default_payload):
    """Provide a team payload for deleting a team."""
    deleted_payload = team_default_payload
    deleted_payload["action"] = "deleted"
    return deleted_payload


@pytest.fixture
def team_edited_payload(team_default_payload):
    """Provide a team payload for editing a team."""
    edited_payload = team_default_payload
    edited_payload["action"] = "edited"
    return edited_payload


@pytest.fixture
def team_added_to_repository_payload(team_default_payload):
    """Provide a team payload for adding a team to a repository."""
    added_to_repository_payload = team_default_payload
    added_to_repository_payload["action"] = "added_to_repository"
    return added_to_repository_payload


@pytest.fixture
def team_rm_from_repository_payload(team_default_payload):
    """Provide a team payload for removing a team from a repository."""
    removed_from_repository_payload = team_default_payload
    removed_from_repository_payload["action"] = "removed_from_repository"
    return removed_from_repository_payload


@pytest.fixture
def team_empty_payload(team_default_payload):
    """Provide an empty team payload."""
    empty_payload = team_default_payload
    empty_payload["action"] = ""
    return empty_payload


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_add_member(mock_logging, org_add_payload):
    """Test that instances when members are added to the org are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_organization_event(org_add_payload)
    mock_logging.info.assert_called_once_with(("user hacktocat added "
                                               "to Octocoders"))
    assert rsp == "user hacktocat added to Octocoders"
    assert code == 200


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_rm_single_member(mock_logging, org_rm_payload):
    """Test that members removed from the org are deleted from rocket's db."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    mock_facade.query_user.return_value = [return_user]
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_organization_event(org_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with([('github_id', "39652351")])
    mock_facade.delete_user.assert_called_once_with("SLACKID")
    mock_logging.info.assert_called_once_with("deleted slack user SLACKID")
    assert rsp == "deleted slack ID SLACKID"
    assert code == 200


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_rm_member_missing(mock_logging, org_rm_payload):
    """Test that members not in rocket db are handled correctly."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query_user.return_value = []
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_organization_event(org_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with([('github_id', "39652351")])
    mock_logging.error.assert_called_once_with("could not find user 39652351")
    assert rsp == "could not find user 39652351"
    assert code == 404


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_rm_mult_members(mock_logging, org_rm_payload):
    """Test that multiple members with the same github name can be deleted."""
    mock_facade = mock.MagicMock(DBFacade)
    user1 = User("SLACKUSER1")
    user2 = User("SLACKUSER2")
    user3 = User("SLACKUSER3")
    mock_facade.query_user.return_value = [user1, user2, user3]
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_organization_event(org_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with([('github_id', "39652351")])
    mock_logging.error.assert_called_once_with("Error: found github ID "
                                               "connected to multiple"
                                               " slack IDs")
    assert rsp == "Error: found github ID connected to multiple slack IDs"
    assert code == 412


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_inv_member(mock_logging, org_inv_payload):
    """Test that instances when members are added to the org are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_organization_event(org_inv_payload)
    mock_logging.info.assert_called_once_with(("user hacktocat invited "
                                               "to Octocoders"))
    assert rsp == "user hacktocat invited to Octocoders"
    assert code == 200


@mock.patch('webhook.webhook.logging')
def test_handle_org_event_empty_action(mock_logging, org_empty_payload):
    """Test that instances where there is no/invalid action are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_organization_event(org_empty_payload)
    mock_logging.error.assert_called_once_with(("organization webhook "
                                                "triggered, invalid "
                                                "action specified: {}"
                                                .format(org_empty_payload)))
    assert rsp == "invalid organization webhook triggered"
    assert code == 405


@mock.patch('webhook.webhook.logging')
def test_handle_team_event_created_team(mock_logging, team_created_payload):
    """Test that teams can be created if they are not in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.retrieve_team.side_effect = LookupError
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_team_event(team_created_payload)
    mock_logging.debug.assert_called_with(("team github with id 2723476 "
                                           "added to organization."))
    mock_facade.store_team.assert_called_once()
    assert rsp == "created team with github id 2723476"
    assert code == 200


@mock.patch('webhook.webhook.logging')
def test_handle_team_event_create_update(mock_logging, team_created_payload):
    """Test that teams can be updated if they are in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_team_event(team_created_payload)
    mock_logging.warning.assert_called_with(("team github with id 2723476 "
                                             "already exists."))
    mock_facade.store_team.assert_called_once()
    assert rsp == "created team with github id 2723476"
    assert code == 200


def test_handle_team_event_delete_team(team_deleted_payload):
    """Test that teams can be deleted if they are in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_team_event(team_deleted_payload)
    mock_facade.delete_team.assert_called_once_with(2723476)
    assert rsp == "deleted team with github id 2723476"
    assert code == 200


def test_handle_team_event_deleted_miss(team_deleted_payload):
    """Test that attempts to delete a missing team are handled."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.retrieve_team.side_effect = LookupError
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_team_event(team_deleted_payload)
    assert rsp == "team with github id 2723476 not found"
    assert code == 404


def test_handle_team_event_edit_team(team_edited_payload):
    """Test that teams can be edited if they are in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_team_event(team_edited_payload)
    assert rsp == "updated team with id 2723476"
    assert code == 200


def test_handle_team_event_edit_miss(team_edited_payload):
    """Test that attempts to edit a missing team are handled."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.retrieve_team.side_effect = LookupError
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_team_event(team_edited_payload)


def test_handle_team_event_add_to_repo(team_added_to_repository_payload):
    """Test that rocket knows when team is added to a repo."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = \
        webhook_handler.handle_team_event(team_added_to_repository_payload)
    assert rsp == "team with id 2723476 added to repository Hello-World"
    assert code == 200


def test_handle_team_event_rm_from_repo(team_rm_from_repository_payload):
    """Test that rocket knows when team is removed from a repo."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = \
        webhook_handler.handle_team_event(team_rm_from_repository_payload)
    assert rsp == "team with id 2723476 removed repository Hello-World"
    assert code == 200


def test_handle_team_event_empty_payload(team_empty_payload):
    """Test that empty/invalid payloads can be handled."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_team_event(team_empty_payload)
    assert rsp == "invalid payload"


@pytest.fixture
def mem_default_payload():
    """Provide the basic structure for an membership payload."""
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
                "site_admin": "False"
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
                "site_admin": "False"
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
    """Provide an membership payload for adding a member."""
    add_payload = mem_default_payload
    add_payload["action"] = "member_added"
    return add_payload


@pytest.fixture
def mem_rm_payload(mem_default_payload):
    """Provide an membership payload for removing a member."""
    rm_payload = mem_default_payload
    rm_payload["action"] = "member_removed"
    return rm_payload


@pytest.fixture
def mem_inv_payload(mem_default_payload):
    """Provide an membership payload for inviting a member."""
    inv_payload = mem_default_payload
    inv_payload["action"] = "member_invited"
    return inv_payload


@pytest.fixture
def mem_empty_payload(mem_default_payload):
    """Provide an membership payload with no action."""
    empty_payload = mem_default_payload
    empty_payload["action"] = ""
    return empty_payload


@mock.patch('webhook.webhook.logging')
def test_handle_mem_event_add_member(mock_logging, mem_add_payload):
    """Test that instances when members are added to the mem are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    mock_facade.query_user.return_value = [return_user]
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_membership_event(mem_add_payload)
    mock_logging.info.assert_called_once_with(("user Codertocat added "
                                               "to rocket"))
    assert rsp == "added slack ID SLACKID"
    assert code == 200


@mock.patch('webhook.webhook.logging')
def test_handle_mem_event_rm_single_member(mock_logging, mem_rm_payload):
    """Test that members removed from the mem are deleted from rocket's db."""
    mock_facade = mock.MagicMock(DBFacade)
    return_user = User("SLACKID")
    return_team = Team("2723476", "rocket", "rocket")
    return_team.add_member("21031067")
    mock_facade.query_user.return_value = [return_user]
    mock_facade.retrieve_team.return_value = return_team
    webhook_handler = WebhookHandler(mock_facade)
    (rsp, code) = webhook_handler.handle_membership_event(mem_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with([('github_id', "21031067")])
    mock_facade.retrieve_team \
        .assert_called_once_with("2723476")
    mock_logging.info.assert_called_once_with("deleted slack user SLACKID"
                                              " from rocket")
    assert not return_team.is_member("21031067")
    assert rsp == "deleted slack ID SLACKID from rocket"
    assert code == 200


@mock.patch('webhook.webhook.logging')
def test_handle_mem_event_rm_member_missing(mock_logging, mem_rm_payload):
    """Test that members not in rocket db are handled correctly."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.query_user.return_value = []
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_membership_event(mem_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with([('github_id', "21031067")])
    mock_logging.error.assert_called_once_with("could not find user 21031067")
    assert rsp == "could not find user 21031067"
    assert code == 404


@mock.patch('webhook.webhook.logging')
def test_handle_mem_event_rm_mult_members(mock_logging, mem_rm_payload):
    """Test that multiple members with the same github name can be deleted."""
    mock_facade = mock.MagicMock(DBFacade)
    user1 = User("SLACKUSER1")
    user2 = User("SLACKUSER2")
    user3 = User("SLACKUSER3")
    mock_facade.query_user.return_value = [user1, user2, user3]
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_membership_event(mem_rm_payload)
    mock_facade.query_user\
        .assert_called_once_with([('github_id', "21031067")])
    mock_logging.error.assert_called_once_with("Error: found github ID "
                                               "connected to multiple"
                                               " slack IDs")
    assert rsp == "Error: found github ID connected to multiple slack IDs"
    assert code == 412


@mock.patch('webhook.webhook.logging')
def test_handle_mem_event_inv_member(mock_logging, mem_inv_payload):
    """Test that instances when members are added to the mem are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_membership_event(mem_inv_payload)
    mock_logging.info.assert_called_once_with(("user Codertocat invited "
                                               "to rocket"))
    assert rsp == "user Codertocat invited to rocket"
    assert code == 200


@mock.patch('webhook.webhook.logging')
def test_handle_mem_event_empty_action(mock_logging, mem_empty_payload):
    """Test that instances where there is no/invalid action are logged."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = WebhookHandler(mock_facade)
    rsp, code = webhook_handler.handle_membership_event(mem_empty_payload)
    mock_logging.error.assert_called_once_with(("membership webhook "
                                                "triggered, invalid "
                                                "action specified: {}"
                                                .format(mem_empty_payload)))
    assert rsp == "invalid membership webhook triggered"
    assert code == 405
