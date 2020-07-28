from app.model import User, Team
from unittest import mock, TestCase
from app.controller.webhook.github.events import OrganizationEventHandler
from tests.memorydb import MemoryDB


def org_default_payload(login: str, uid: str):
    """Provide the basic structure for an organization payload."""
    return {
        'action': 'member_added',
        'membership': {
            'url': '',
            'state': 'pending',
            'role': 'member',
            'organization_url': '',
            'user': {
                'login': login,
                'id': uid,
                'node_id': 'MDQ6VXNlcjM5NjUyMzUx',
                'avatar_url': '',
                'gravatar_id': '',
                'url': '',
                'html_url': '',
                'followers_url': '',
                'following_url': '',
                'gists_url': '',
                'starred_url': '',
                'subscriptions_url': '',
                'organizations_url': '',
                'repos_url': '',
                'events_url': '',
                'received_events_url': '',
                'type': 'User',
                'site_admin': False
            }
        },
        'organization': {
            'login': 'Octocoders',
            'id': '38302899',
            'node_id': 'MDEyOk9yZ2FuaXphdGlvbjM4MzAyODk5',
            'url': '',
            'repos_url': '',
            'events_url': '',
            'hooks_url': '',
            'issues_url': '',
            'members_url': '',
            'public_members_url': '',
            'avatar_url': '',
            'description': ''
        },
        'sender': {
            'login': 'Codertocat',
            'id': '21031067',
            'node_id': 'MDQ6VXNlcjIxMDMxMDY3',
            'avatar_url': '',
            'gravatar_id': '',
            'url': '',
            'html_url': '',
            'followers_url': '',
            'following_url': '',
            'gists_url': '',
            'starred_url': '',
            'subscriptions_url': '',
            'organizations_url': '',
            'repos_url': '',
            'events_url': '',
            'received_events_url': '',
            'type': 'User',
            'site_admin': False
        }
    }


class TestOrganizationHandles(TestCase):
    def setUp(self):
        self.username = 'hacktocat'
        self.gh_uid = '4738549'
        self.default_payload = org_default_payload(self.username, self.gh_uid)
        self.add_payload = org_default_payload(self.username, self.gh_uid)
        self.rm_payload = org_default_payload(self.username, self.gh_uid)
        self.invite_payload = org_default_payload(self.username, self.gh_uid)
        self.empty_payload = org_default_payload(self.username, self.gh_uid)

        self.add_payload['action'] = 'member_added'
        self.rm_payload['action'] = 'member_removed'
        self.invite_payload['action'] = 'member_invited'
        self.empty_payload['action'] = ''

        self.u0 = User('U01234954')
        self.u0.github_id = self.gh_uid
        self.u0.github_username = self.username
        self.team_all = Team('1', 'all', 'Team all')
        self.db = MemoryDB(users=[self.u0], teams=[self.team_all])

        self.gh = mock.Mock()
        self.conf = mock.Mock()
        self.conf.github_team_all = 'all'
        self.webhook_handler = OrganizationEventHandler(self.db, self.gh,
                                                        self.conf)

    def test_org_handle_invite(self):
        resp, code = self.webhook_handler.handle(self.invite_payload)
        self.assertIn(self.username, resp)
        self.assertEqual(code, 200)

    def test_handle_org_event_add_member(self):
        rsp, code = self.webhook_handler.handle(self.add_payload)
        self.assertEqual(rsp, f'user {self.username} added to Octocoders')
        self.assertEqual(code, 200)
        self.assertIn(self.gh_uid, self.team_all.members)

    def test_handle_org_event_add_no_all_team(self):
        self.db.teams = {}
        self.gh.org_create_team.return_value = 305938
        rsp, code = self.webhook_handler.handle(self.add_payload)
        self.assertEqual(rsp, f'user {self.username} added to Octocoders')
        self.assertEqual(code, 200)

        team = self.db.retrieve(Team, '305938')
        self.assertEqual(team.github_team_name, self.conf.github_team_all)
        self.assertIn(self.gh_uid, team.members)

    def test_handle_org_event_rm_single_member(self):
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.assertEqual(rsp, f'deleted slack ID {self.u0.slack_id}')
        self.assertEqual(code, 200)
        with self.assertRaises(LookupError):
            self.db.retrieve(User, self.u0.slack_id)

    def test_handle_org_event_rm_member_missing(self):
        self.db.users = {}
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.assertEqual(rsp, f'could not find user {self.username}')
        self.assertEqual(code, 404)

    def test_handle_org_event_rm_multiple_members_cause_error(self):
        clone0 = User('Ustreisand')
        clone0.github_username = self.username
        clone0.github_id = self.gh_uid
        self.db.users['Ustreisand'] = clone0
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.assertEqual(
            rsp,
            'Error: found github ID connected to multiple slack IDs'
        )
        self.assertEqual(code, 412)

    def test_handle_org_event_empty_action(self):
        rsp, code = self.webhook_handler.handle(self.empty_payload)
        self.assertEqual(rsp, 'invalid organization webhook triggered')
        self.assertEqual(code, 405)
