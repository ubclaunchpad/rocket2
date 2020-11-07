"""Test Scheduler base class."""
from unittest import TestCase
from unittest.mock import MagicMock, patch
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler import Scheduler
from interface.slack import Bot
from config import Config
from tests.memorydb import MemoryDB


class TestScheduler(TestCase):
    """Test Scheduler base class."""

    def setUp(self):
        """Set up testing environment."""
        self.config = MagicMock(Config)
        self.flask = MagicMock(Flask)
        self.args = (self.flask, self.config)
        self.bgsched = MagicMock(BackgroundScheduler)
        self.db = MemoryDB()
        self.config.slack_announcement_channel = "#general"
        self.config.slack_notification_channel = "#general"
        self.config.slack_api_token = "sometoken.exe"
        self.config.slack_pairing_channel = "#general"
        self.config.slack_pairing_frequency = "* * * * *"

    @patch.object(Bot, 'get_channel_id')
    def test_proper_initialization(self, other):
        """Test proper initialization with proper arguments."""
        s = Scheduler(self.bgsched, self.args, self.db)

        self.assertEqual(self.bgsched.add_job.call_count, 2)
        self.assertEqual(len(s.modules), 2)
