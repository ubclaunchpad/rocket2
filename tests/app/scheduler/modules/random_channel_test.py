"""Test how random channels would work."""
from unittest import mock, TestCase
from app.scheduler.modules.random_channel import RandomChannelPromoter


class TestRandomChannelExec(TestCase):
    """Test cases for execution of random channel selector."""

    def setUp(self):
        """Set up necessary spec'd components for testing later."""
        self.config = mock.Mock()
        self.config.slack_api_token = ''
        self.config.slack_notification_channel = ''
        self.config.slack_announcement_channel = ''
        self.app = mock.Mock()
        self.slackbot = mock.Mock()

        self.promoter = RandomChannelPromoter(self.app, self.config)
        self.promoter.bot = self.slackbot

    def test_choose_from_one(self):
        """Test choosing from 1 channel."""
        self.slackbot.get_channels.return_value = [
            {'id': '123', 'name': 'general', 'is_archived': False}
        ]

        self.promoter.do_it()

        self.slackbot.send_to_channel.assert_called()
        self.assertIn('general', self.slackbot.send_to_channel.call_args[0][0])

    def test_choose_from_archived(self):
        """Test choosing from all archived channels."""
        self.slackbot.get_channels.return_value = [
            {'id': '123', 'name': 'general', 'is_archived': True},
            {'id': '123', 'name': 'random', 'is_archived': True},
            {'id': '123', 'name': 'choochoo', 'is_archived': True},
        ]

        with self.assertRaises(IndexError):
            self.promoter.do_it()

        self.slackbot.send_to_channel.assert_not_called()

    def test_choose_non_archived(self):
        """Test choosing from all but one archived channels."""
        self.slackbot.get_channels.return_value = [
            {'id': '123', 'name': 'general', 'is_archived': True},
            {'id': '123', 'name': 'random', 'is_archived': False},
            {'id': '123', 'name': 'choochoo', 'is_archived': True},
        ]

        self.promoter.do_it()

        self.slackbot.send_to_channel.assert_called()
        self.assertIn('random', self.slackbot.send_to_channel.call_args[0][0])
