"""test the handler for GitHub team events."""
import pytest

from db import DBFacade
from app.model import Team
from unittest import mock
from app.controller.webhook.github.events import TeamEventHandler


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


def test_org_supported_action_list():
    """Confirm the supported action list of the handler."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = TeamEventHandler(mock_facade)
    assert webhook_handler.supported_action_list == ["created",
                                                     "deleted",
                                                     "edited",
                                                     "added_to_repository",
                                                     "removed_from_repository"
                                                     ]


def test_handle_team_event_created_team(team_created_payload):
    """Test that teams can be created if they are not in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.retrieve.side_effect = LookupError
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(team_created_payload)
    mock_facade.store.assert_called_once()
    assert rsp == "created team with github id 2723476"
    assert code == 200


def test_handle_team_event_create_update(team_created_payload):
    """Test that teams can be updated if they are in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(team_created_payload)
    mock_facade.store.assert_called_once()
    assert rsp == "created team with github id 2723476"
    assert code == 200


def test_handle_team_event_delete_team(team_deleted_payload):
    """Test that teams can be deleted if they are in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(team_deleted_payload)
    mock_facade.delete.assert_called_once_with(Team, "2723476")
    assert rsp == "deleted team with github id 2723476"
    assert code == 200


def test_handle_team_event_deleted_miss(team_deleted_payload):
    """Test that attempts to delete a missing team are handled."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.retrieve.side_effect = LookupError
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(team_deleted_payload)
    assert rsp == "team with github id 2723476 not found"
    assert code == 404


def test_handle_team_event_edit_team(team_edited_payload):
    """Test that teams can be edited if they are in the db."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(team_edited_payload)
    assert rsp == "updated team with id 2723476"
    assert code == 200


def test_handle_team_event_edit_miss(team_edited_payload):
    """Test that attempts to edit a missing team are handled."""
    mock_facade = mock.MagicMock(DBFacade)
    mock_facade.retrieve.side_effect = LookupError
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(team_edited_payload)


def test_handle_team_event_add_to_repo(team_added_to_repository_payload):
    """Test that rocket knows when team is added to a repo."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = \
        webhook_handler.handle(team_added_to_repository_payload)
    assert rsp == "team with id 2723476 added to repository Hello-World"
    assert code == 200


def test_handle_team_event_rm_from_repo(team_rm_from_repository_payload):
    """Test that rocket knows when team is removed from a repo."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = \
        webhook_handler.handle(team_rm_from_repository_payload)
    assert rsp == "team with id 2723476 removed repository Hello-World"
    assert code == 200


def test_handle_team_event_empty_payload(team_empty_payload):
    """Test that empty/invalid payloads can be handled."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = TeamEventHandler(mock_facade)
    rsp, code = webhook_handler.handle(team_empty_payload)
    assert rsp == "invalid payload"
