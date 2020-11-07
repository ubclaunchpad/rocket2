"""Test how pairing users should work"""
from unittest import mock, TestCase
from app.scheduler.modules.pairing import PairingSchedule
from tests.memorydb import MemoryDB
from app.model import Pairing
from interface.slack import Bot


class TestPairingSchedule(TestCase):
    """Test cases for execution of random channel selector."""

    @mock.patch.object(Bot, 'get_channel_id')
    def setUp(self, channel_id_mock):
        """Set up necessary spec'd components for testing later."""
        self.config = mock.Mock()
        self.config.slack_api_token = ''
        self.config.slack_notification_channel = ''
        self.config.slack_announcement_channel = ''
        self.config.slack_pairing_channel = ''
        self.config.slack_pairing_frequency = '* * * * *'
        self.app = mock.Mock()
        self.slackbot = mock.Mock()
        self.db = MemoryDB()
        channel_id_mock.return_value = "id"

        self.pairing = PairingSchedule(self.app, self.config, self.db)
        self.pairing.bot = self.slackbot

    def test_pairing_simple(self):
        """Test pairing two people together"""
        self.db.delete_all(Pairing)
        self.slackbot.get_channel_users.return_value = [
            'user1', 'user2'
        ]

        self.pairing.do_it()
        args = self.slackbot.create_private_chat.call_args.args[0]
        assert 'user1' in args
        assert 'user2' in args
        assert len(args) == 2

    def test_pairing_many(self):
        """Test pairing many people together"""
        users = []
        self.db.delete_all(Pairing)
        for i in range(100):
            users.append("user" + str(i))
        self.slackbot.get_channel_users.return_value = users
        self.pairing.do_it()
        assert self.slackbot.create_private_chat.call_count == 50
        seen = set()
        for arg in self.slackbot.create_private_chat.call_args_list:
            user_args = arg.args[0]
            for user in user_args:
                if user in seen:
                    self.fail("User was matched twice!")
                    return
                seen.add(user)

    def test_pairing_purged(self):
        """Test purging the DB once it is impossible to pair users"""
        self.db.delete_all(Pairing)
        users = ['user1', 'user2']
        self.slackbot.get_channel_users.return_value = users
        self.pairing.do_it()
        args = self.slackbot.create_private_chat.call_args.args[0]
        assert 'user1' in args
        assert 'user2' in args
        assert len(args) == 2
        # Now the db has the pairing of user1 and user2
        self.pairing.do_it()
        # Since they are the only ones, they get matched again
        args = self.slackbot.create_private_chat.call_args.args[0]
        assert 'user1' in args
        assert 'user2' in args
        assert len(args) == 2

    def test_pairing_odd(self):
        """Test pairing users, when one group has an odd number of users"""
        self.db.delete_all(Pairing)
        users = ['user1', 'user2', 'user3']
        self.slackbot.get_channel_users.return_value = users
        self.pairing.do_it()
        args = self.slackbot.create_private_chat.call_args.args[0]
        assert 'user1' in args
        assert 'user2' in args
        assert 'user3' in args
        assert len(args) == 3
