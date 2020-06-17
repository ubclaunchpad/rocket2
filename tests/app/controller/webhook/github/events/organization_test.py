"""Test the handler for GitHub organization events."""
from app.model import User, Team
from unittest import mock, TestCase
from app.controller.webhook.github.events import OrganizationEventHandler


def org_default_payload():
    """Provide the basic structure for an organization payload."""
    return {
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


class TestOrganizationHandles(TestCase):
    """Test functions pertaining to Github Organizations."""

    def setUp(self):
        """Set up mocks and payloads and whatnot for use in testing."""
        self.default_payload = org_default_payload()
        self.add_payload = org_default_payload()
        self.rm_payload = org_default_payload()
        self.empty_payload = org_default_payload()

        self.add_payload['action'] = 'member_added'
        self.rm_payload['action'] = 'member_removed'
        self.empty_payload['action'] = ''

        self.dbfacade = mock.Mock()
        self.gh = mock.Mock()
        self.conf = mock.Mock()
        self.conf.github_team_all = 'all'
        self.webhook_handler = OrganizationEventHandler(self.dbfacade, self.gh,
                                                        self.conf)

    def test_org_supported_action_list(self):
        """Confirm the supported action list of the handler."""
        self.assertCountEqual(self.webhook_handler.supported_action_list,
                              ['member_removed', 'member_added'])

    def test_handle_org_event_add_member(self):
        """Test instances when members are added to the org are logged."""
        return_team = Team('1', 't', 'T')
        self.dbfacade.query.return_value = [return_team]
        rsp, code = self.webhook_handler.handle(self.add_payload)
        self.assertEqual(rsp, 'user hacktocat added to Octocoders')
        self.assertEqual(code, 200)

    def test_handle_org_event_rm_single_member(self):
        """Test members removed from the org are deleted from rocket's db."""
        return_user = User("SLACKID")
        self.dbfacade.query.return_value = [return_user]
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.dbfacade.query\
            .assert_called_once_with(User, [('github_user_id', "39652351")])
        self.dbfacade.delete.assert_called_once_with(User, "SLACKID")
        self.assertEqual(rsp, 'deleted slack ID SLACKID')
        self.assertEqual(code, 200)

    def test_handle_org_event_rm_member_missing(self):
        """Test members not in rocket db are handled correctly."""
        self.dbfacade.query.return_value = []
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.dbfacade.query\
            .assert_called_once_with(User, [('github_user_id', "39652351")])
        self.assertEqual(rsp, 'could not find user hacktocat')
        self.assertEqual(code, 404)

    def test_handle_org_event_rm_mult_members(self):
        """Test multiple members with the same github name can be deleted."""
        user1 = User("SLACKUSER1")
        user2 = User("SLACKUSER2")
        user3 = User("SLACKUSER3")
        self.dbfacade.query.return_value = [user1, user2, user3]
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.dbfacade.query\
            .assert_called_once_with(User, [('github_user_id', "39652351")])
        self.assertEqual(
            rsp,
            'Error: found github ID connected to multiple slack IDs'
        )
        self.assertEqual(code, 412)

    def test_handle_org_event_empty_action(self):
        """Test that instances where there is no/invalid action are logged."""
        rsp, code = self.webhook_handler.handle(self.empty_payload)
        self.assertEqual(rsp, 'invalid organization webhook triggered')
        self.assertEqual(code, 405)
