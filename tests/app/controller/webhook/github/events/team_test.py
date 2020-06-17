"""test the handler for GitHub team events."""
from app.model import Team
from unittest import mock, TestCase
from app.controller.webhook.github.events import TeamEventHandler


def team_default_payload():
    """Provide the basic structure for a team payload."""
    return {
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


class TestTeamHandles(TestCase):
    """Test Github team hook functions."""

    def setUp(self):
        """Set up variables."""
        self.created_payload = team_default_payload()
        self.deleted_payload = team_default_payload()
        self.edited_payload = team_default_payload()
        self.added_to_repo_payload = team_default_payload()
        self.rm_from_repo_payload = team_default_payload()
        self.empty_payload = team_default_payload()
        self.created_payload['action'] = 'created'
        self.deleted_payload['action'] = 'deleted'
        self.edited_payload['action'] = 'edited'
        self.added_to_repo_payload['action'] = 'added_to_repository'
        self.rm_from_repo_payload['action'] = 'removed_from_repository'
        self.empty_payload['action'] = ''

        self.dbf = mock.Mock()
        self.gh = mock.Mock()
        self.conf = mock.Mock()
        self.webhook_handler = TeamEventHandler(self.dbf, self.gh, self.conf)

    def test_org_supported_action_list(self):
        """Confirm the supported action list of the handler."""
        self.assertCountEqual(self.webhook_handler.supported_action_list,
                              ['created', 'deleted', 'edited',
                               'added_to_repository',
                               'removed_from_repository'])

    def test_handle_team_event_created_team(self):
        """Test teams can be created if they are not in the db."""
        self.dbf.retrieve.side_effect = LookupError
        rsp, code = self.webhook_handler.handle(self.created_payload)
        self.dbf.store.assert_called_once()
        self.assertEqual(rsp, 'created team with github id 2723476')
        self.assertEqual(code, 200)

    def test_handle_team_event_create_update(self):
        """Test teams can be updated if they are in the db."""
        rsp, code = self.webhook_handler.handle(self.created_payload)
        self.dbf.store.assert_called_once()
        self.assertEqual(rsp, 'created team with github id 2723476')
        self.assertEqual(code, 200)

    def test_handle_team_event_delete_team(self):
        """Test teams can be deleted if they are in the db."""
        rsp, code = self.webhook_handler.handle(self.deleted_payload)
        self.dbf.delete.assert_called_once_with(Team, "2723476")
        self.assertEqual(rsp, 'deleted team with github id 2723476')
        self.assertEqual(code, 200)

    def test_handle_team_event_deleted_miss(self):
        """Test attempts to delete a missing team are handled."""
        self.dbf.retrieve.side_effect = LookupError
        rsp, code = self.webhook_handler.handle(self.deleted_payload)
        self.assertEqual(rsp, 'team with github id 2723476 not found')
        self.assertEqual(code, 404)

    def test_handle_team_event_edit_team(self):
        """Test teams can be edited if they are in the db."""
        rsp, code = self.webhook_handler.handle(self.edited_payload)
        self.assertEqual(rsp, 'updated team with id 2723476')
        self.assertEqual(code, 200)

    def test_handle_team_event_edit_miss(self):
        """Test attempts to edit a missing team are handled."""
        self.dbf.retrieve.side_effect = LookupError
        rsp, code = self.webhook_handler.handle(self.edited_payload)
        self.assertEqual(rsp, 'team with github id 2723476 not found')
        self.assertEqual(code, 404)

    def test_handle_team_event_add_to_repo(self):
        """Test rocket knows when team is added to a repo."""
        rsp, code = self.webhook_handler.handle(self.added_to_repo_payload)
        self.assertEqual(
            rsp, 'team with id 2723476 added to repository Hello-World')
        self.assertEqual(code, 200)

    def test_handle_team_event_rm_from_repo(self):
        """Test rocket knows when team is removed from a repo."""
        rsp, code = self.webhook_handler.handle(self.rm_from_repo_payload)
        self.assertEqual(
            rsp, 'team with id 2723476 removed repository Hello-World')
        self.assertEqual(code, 200)

    def test_handle_team_event_empty_payload(self):
        """Test empty/invalid payloads can be handled."""
        rsp, code = self.webhook_handler.handle(self.empty_payload)
        self.assertEqual(rsp, 'invalid payload')
