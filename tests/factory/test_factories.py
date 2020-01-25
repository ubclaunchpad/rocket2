"""Tests for factories."""
import pytest

from factory import make_command_parser, CommandParser, \
    make_github_webhook_handler, GitHubWebhookHandler, \
    make_slack_events_handler, SlackEventsHandler
from unittest.mock import MagicMock, patch
from config import Config


@pytest.fixture
def test_config():
    """Create config for testing."""
    test_config = MagicMock(Config)
    test_config.aws_users_tablename = 'users_test'
    test_config.aws_teams_tablename = 'teams_test'
    test_config.aws_projects_tablename = 'projects_test'
    test_config.github_webhook_secret = 'secret'
    test_config.slack_api_token = 'token'
    test_config.slack_notification_channel = 'channel'
    test_config.slack_announcement_channel = 'announcements'
    test_config.testing = True
    return test_config


@pytest.mark.db
@patch('interface.github.GithubInterface')
def test_make_command_parser(gi, test_config):
    """Test the make_command_parser function."""
    parser = make_command_parser(test_config, gi)
    assert isinstance(parser, CommandParser)


@pytest.mark.db
def test_make_github_webhook_handler(test_config):
    """Test the make_command_github_webhook_handler function."""
    handler = make_github_webhook_handler(test_config)
    assert isinstance(handler, GitHubWebhookHandler)


@pytest.mark.db
def test_make_slack_events_handler(test_config):
    """Test the make_command_slack_events_handler function."""
    handler = make_slack_events_handler(test_config)
    assert isinstance(handler, SlackEventsHandler)
