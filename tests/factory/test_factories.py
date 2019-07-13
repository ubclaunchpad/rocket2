"""Tests for factories."""
import pytest

from factory import make_command_parser, CommandParser
from unittest import mock
from config import Credentials
from app.controller.webhook.github import GitHubWebhookHandler
from app.controller.webhook.slack import SlackEventsHandler


@pytest.mark.db
def test_make_command_parser():
    """Test the make_command_parser function."""
    test_config = {
        'testing': True,
        'aws': {
            'users_table': 'users_test',
            'teams_table': 'teams_test',
            'projects_table': 'projects_test'
        }
    }
    parser = make_command_parser(test_config, mock.MagicMock(Credentials))
    assert isinstance(parser, CommandParser)


@pytest.mark.db
def test_make_github_webhook_handler():
    """Test the make_command_github_webhook_handler function."""
    test_config = {
        'testing': True,
        'aws': {
            'users_table': 'users_test',
            'teams_table': 'teams_test',
            'projects_table': 'projects_test'
        }
    }
    handler = make_command_github_webhook_handler(test_config,
                                                  mock.MagicMock(Credentials))
    assert isinstance(handler, GitHubWebhookHandler)


@pytest.mark.db
def test_make_github_webhook_handler():
    """Test the make_command_github_webhook_handler function."""
    test_config = {
        'testing': True,
        'aws': {
            'users_table': 'users_test',
            'teams_table': 'teams_test',
            'projects_table': 'projects_test'
        }
    }
    handler = make_command_github_slack_handler(test_config,
                                                mock.MagicMock(Credentials))
    assert isinstance(handler, SlackEventsHandler)
