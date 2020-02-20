"""Test Scheduler base class."""
from unittest import TestCase
from unittest.mock import MagicMock
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler import Scheduler
from config import Config


class TestScheduler(TestCase):
    """Test Scheduler base class."""

    def setUp(self):
        """Set up testing environment."""
        self.config = MagicMock(Config)
        self.flask = MagicMock(Flask)
        self.args = (self.flask, self.config)
        self.bgsched = MagicMock(BackgroundScheduler)

        self.config.slack_announcement_channel = "#general"
        self.config.slack_notification_channel = "#general"
        self.config.slack_api_token = "sometoken.exe"

    def test_proper_initialization(self):
        """Test proper initialization with proper arguments."""
        s = Scheduler(self.bgsched, self.args)

        self.assertEqual(self.bgsched.add_job.call_count, 1)
        self.assertEqual(len(s.modules), 1)
