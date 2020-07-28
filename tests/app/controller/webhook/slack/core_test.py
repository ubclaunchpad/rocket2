from app.controller.webhook.slack import SlackEventsHandler
from app.model import User
from interface.slack import SlackAPIError
from unittest import mock, TestCase
from tests.memorydb import MemoryDB


class TestSlackWebhookCore(TestCase):
    def setUp(self):
        self.u_id = 'U012A3CDE'
        self.db = MemoryDB()
        self.bot = mock.Mock()
        self.handler = SlackEventsHandler(self.db, self.bot)
        self.event = {
            'token': 'XXYYZZ',
            'team_id': 'TXXXXXXXX',
            'api_app_id': 'AXXXXXXXXX',
            'event': {
                'type': 'team_join',
                'user': {
                    'id': self.u_id,
                    'team_id': 'T012AB3C4',
                    'name': 'spengler',
                    'deleted': False,
                    'color': '9f69e7',
                    'real_name': 'Egon Spengler',
                    'tz': 'America/Los_Angeles',
                    'tz_label': 'Pacific Daylight Time',
                    'tz_offset': -25200,
                    'profile': {
                        'avatar_hash': 'ge3b51ca72de',
                        'status_text': 'Print is dead',
                        'status_emoji': ':books:',
                        'status_expiration': 1502138999,
                        'real_name': 'Egon Spengler',
                        'display_name': 'spengler',
                        'real_name_normalized': 'Egon Spengler',
                        'display_name_normalized': 'spengler',
                        'email': 'spengler@ghostbusters.example.com',
                        'image_24': 'https://.../avatar/hello.jpg',
                        'image_32': 'https://.../avatar/hello.jpg',
                        'image_48': 'https://.../avatar/hello.jpg',
                        'image_72': 'https://.../avatar/hello.jpg',
                        'image_192': 'https://.../avatar/hello.jpg',
                        'image_512': 'https://.../avatar/hello.jpg',
                        'team': 'T012AB3C4'
                    },
                    'is_admin': True,
                    'is_owner': False,
                    'is_primary_owner': False,
                    'is_restricted': False,
                    'is_ultra_restricted': False,
                    'is_bot': False,
                    'is_stranger': False,
                    'updated': 1502138686,
                    'is_app_user': False,
                    'has_2fa': False,
                    'locale': 'en-US'
                }
            },
            'type': 'app_mention',
            'authed_users': ['UXXXXXXX1', 'UXXXXXXX2'],
            'event_id': 'Ev08MFMKH6',
            'event_time': 1234567890
        }

    def test_handle_team_join_success(self):
        self.handler.handle_team_join(self.event)
        self.bot.send_dm.assert_called_once_with(SlackEventsHandler.welcome,
                                                 self.u_id)
        u = self.db.retrieve(User, self.u_id)
        self.assertEqual(u.slack_id, self.u_id)

    def test_handle_team_join_slack_error(self):
        self.bot.send_dm.side_effect = SlackAPIError(None)
        self.handler.handle_team_join(self.event)
        self.bot.send_dm.assert_called_once_with(SlackEventsHandler.welcome,
                                                 self.u_id)
        u = self.db.retrieve(User, self.u_id)
        self.assertEqual(u.slack_id, self.u_id)
