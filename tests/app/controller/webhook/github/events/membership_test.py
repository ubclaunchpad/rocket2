"""Test the handler for GitHub membership events."""
from app.model import User, Team
from unittest import mock, TestCase
from app.controller.webhook.github.events import MembershipEventHandler


def mem_default_payload():
    """Provide the basic structure for a membership payload."""
    return {
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


class TestMembershipHandles(TestCase):
    """Test membership functions on Github interface."""

    def setUp(self):
        """Set up variables for testing."""
        self.default_payload = mem_default_payload()
        self.add_payload = mem_default_payload()
        self.rm_payload = mem_default_payload()
        self.empty_payload = mem_default_payload()

        self.add_payload['action'] = 'added'
        self.rm_payload['action'] = 'removed'
        self.empty_payload['action'] = ''

        self.dbfacade = mock.Mock()
        self.gh = mock.Mock()
        self.conf = mock.Mock()
        self.conf.github_team_all = 'all'
        self.webhook_handler = MembershipEventHandler(self.dbfacade, self.gh,
                                                      self.conf)

    def test_org_supported_action_list(self):
        """Confirm the supported action list of the handler."""
        self.assertCountEqual(self.webhook_handler.supported_action_list,
                              ['removed', 'added'])

    def test_handle_mem_event_add_member(self):
        """Test instances when members are added to the mem are logged."""
        return_user = User("SLACKID")
        return_team = Team("2723476", "rocket", "rocket")
        return_team.add_member("SLACKID")
        self.dbfacade.query.return_value = [return_user]
        self.dbfacade.retrieve.return_value = return_team
        rsp, code = self.webhook_handler.handle(self.add_payload)
        self.dbfacade.store.assert_called_once_with(return_team)
        self.assertEqual(rsp, 'added slack ID SLACKID')
        self.assertEqual(code, 200)

    def test_handle_mem_event_add_missing_member(self):
        """Test instances when members are added to the mem are logged."""
        self.dbfacade.query.return_value = []
        rsp, code = self.webhook_handler.handle(self.add_payload)
        self.assertEqual(rsp, 'could not find user Codertocat')
        self.assertEqual(code, 404)

    def test_handle_mem_event_rm_single_member(self):
        """Test members removed from the mem are deleted from rocket's db."""
        return_user = User("SLACKID")
        return_team = Team("2723476", "rocket", "rocket")
        return_team.add_member("21031067")
        self.dbfacade.query.return_value = [return_user]
        self.dbfacade.retrieve.return_value = return_team
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.dbfacade.query\
            .assert_called_once_with(User, [('github_user_id', "21031067")])
        self.dbfacade.retrieve \
            .assert_called_once_with(Team, "2723476")
        self.dbfacade.store.assert_called_once_with(return_team)
        self.assertFalse(return_team.has_member('21031067'))
        self.assertEqual(rsp, 'deleted slack ID SLACKID from rocket')
        self.assertEqual(code, 200)

    def test_handle_mem_event_rm_member_missing(self):
        """Test members not in rocket db are handled correctly."""
        return_user = User("SLACKID")
        return_team = Team("2723476", "rocket", "rocket")
        self.dbfacade.query.return_value = [return_user]
        self.dbfacade.retrieve.return_value = return_team
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.dbfacade.query\
            .assert_called_once_with(User, [('github_user_id', "21031067")])
        self.assertEqual(rsp, 'slack user SLACKID not in rocket')
        self.assertEqual(code, 404)

    def test_handle_mem_event_rm_member_wrong_team(self):
        """Test member removed from a team they are not in."""
        self.dbfacade.query.return_value = []
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.dbfacade.query\
            .assert_called_once_with(User, [('github_user_id', "21031067")])
        self.assertEqual(rsp, 'could not find user 21031067')
        self.assertEqual(code, 404)

    def test_handle_mem_event_rm_mult_members(self):
        """Test multiple members with the same github name deleted."""
        user1 = User("SLACKUSER1")
        user2 = User("SLACKUSER2")
        user3 = User("SLACKUSER3")
        self.dbfacade.query.return_value = [user1, user2, user3]
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.dbfacade.query\
            .assert_called_once_with(User, [('github_user_id', "21031067")])
        self.assertEqual(
            rsp, 'Error: found github ID connected to multiple slack IDs')
        self.assertEqual(code, 412)

    def test_handle_mem_event_empty_action(self):
        """Test instances where there is no/invalid action are logged."""
        rsp, code = self.webhook_handler.handle(self.empty_payload)
        self.assertEqual(rsp, 'invalid membership webhook triggered')
        self.assertEqual(code, 405)
