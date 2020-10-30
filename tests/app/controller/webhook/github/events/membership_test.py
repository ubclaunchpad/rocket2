"""Test the handler for GitHub membership events."""
from app.model import User, Team
from unittest import mock, TestCase
from app.controller.webhook.github.events import MembershipEventHandler
from tests.memorydb import MemoryDB


def mem_default_payload(teamname: str, teamid: int,
                        member: str, memberid: int):
    """Provide the basic structure for a membership payload."""
    return {
        'action': 'removed',
        'scope': 'team',
        'member': {
            'login': member,
            'id': memberid,
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
        },
        'team': {
            'name': teamname,
            'id': teamid,
            'node_id': 'MDQ6VGVhbTI3MjM0NzY=',
            'slug': 'rocket',
            'description': 'hub hub hubber-one',
            'privacy': 'closed',
            'url': '',
            'members_url': '',
            'repositories_url': '',
            'permission': 'pull'
        },
        'organization': {
            'login': 'Octocoders',
            'id': '38302899',
            'node_id': '',
            'url': '',
            'repos_url': '',
            'events_url': '',
            'hooks_url': '',
            'issues_url': '',
            'members_url': '',
            'public_members_url': '',
            'avatar_url': '',
            'description': ''
        }
    }


class TestMembershipHandles(TestCase):
    def setUp(self):
        self.team = 'rocket'
        self.teamid = 395830
        self.member = 'theflatearth'
        self.memberid = 3058493
        self.add_payload = mem_default_payload(
            self.team, self.teamid,
            self.member, self.memberid
        )
        self.rm_payload = mem_default_payload(
            self.team, self.teamid,
            self.member, self.memberid
        )
        self.empty_payload = mem_default_payload(
            self.team, self.teamid,
            self.member, self.memberid
        )

        self.add_payload['action'] = 'added'
        self.rm_payload['action'] = 'removed'
        self.empty_payload['action'] = ''

        self.u = User('U4058409')
        self.u.github_id = str(self.memberid)
        self.u.github_username = self.member
        self.t = Team(str(self.teamid), self.team, self.team.capitalize())
        self.db = MemoryDB(users=[self.u], teams=[self.t])

        self.gh = mock.Mock()
        self.conf = mock.Mock()
        self.conf.github_team_all = 'all'
        self.webhook_handler = MembershipEventHandler(self.db, self.gh,
                                                      self.conf)

    def test_handle_mem_event_add_member(self):
        rsp, code = self.webhook_handler.handle(self.add_payload)
        self.assertEqual(rsp, f'added slack ID {self.u.slack_id}')
        self.assertEqual(code, 200)

    def test_handle_mem_event_add_member_not_found_in_db(self):
        self.db.users = {}
        rsp, code = self.webhook_handler.handle(self.add_payload)
        self.assertEqual(rsp, f'could not find user {self.member}')
        self.assertEqual(code, 200)

    def test_handle_mem_event_rm_member(self):
        self.t.add_member(self.u.github_id)
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.assertFalse(self.t.has_member(self.u.github_id))
        self.assertIn(self.u.slack_id, rsp)
        self.assertEqual(code, 200)

    def test_handle_mem_event_rm_member_missing_from_team(self):
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.assertEqual(
            rsp,
            f'slack user {self.u.slack_id} not in {self.team}')
        self.assertEqual(code, 200)

    def test_handle_mem_event_rm_member_missing_from_db(self):
        self.db.users = {}
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.assertEqual(rsp, f'could not find user {self.memberid}')
        self.assertEqual(code, 200)

    def test_handle_mem_event_rm_multiple_members(self):
        clone = User('Uclones')
        clone.github_id = str(self.memberid)
        clone.github_username = self.member
        self.db.users['Uclones'] = clone
        rsp, code = self.webhook_handler.handle(self.rm_payload)
        self.assertEqual(
            rsp, 'Error: found github ID connected to multiple slack IDs')
        self.assertEqual(code, 200)

    def test_handle_mem_event_invalid_action(self):
        rsp, code = self.webhook_handler.handle(self.empty_payload)
        self.assertEqual(rsp, 'Unsupported action triggered, ignoring.')
        self.assertEqual(code, 202)
