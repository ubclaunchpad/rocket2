"""Test the loading of config."""
import pytest
from config import Config, MissingConfigError
import os


@pytest.fixture
def complete_config():
    """Return a config object with complete attributes."""
    os.environ = {
        'TESTING': 'True',

        'SLACK_SIGNING_SECRET': 'something secret',
        'SLACK_API_TOKEN': 'some token idk',
        'SLACK_NOTIFICATION_CHANNEL': '#rocket2',
        'SLACK_ANNOUNCEMENT_CHANNEL': '#ot-random',

        'GITHUB_APP_ID': '2024',
        'GITHUB_ORG_NAME': 'ubclaunchpad',
        'GITHUB_WEBHOOK_ENDPT': '/webhook',
        'GITHUB_WEBHOOK_SECRET': 'oiarstierstiemoiarno',
        'GITHUB_KEY': 'BEGIN END',

        'AWS_ACCESS_KEYID': '324098102',
        'AWS_SECRET_KEY': 'more secret',
        'AWS_USERS_TABLE': 'users',
        'AWS_TEAMS_TABLE': 'teams',
        'AWS_PROJECTS_TABLE': 'projects',
        'AWS_REGION': 'us-west-2',
    }
    return Config()


@pytest.fixture
def incomplete_config():
    """Return a config object with incomplete attributes."""
    os.environ = {
        'TESTING': 'True',

        'GITHUB_APP_ID': '2024',
        'GITHUB_ORG_NAME': 'ubclaunchpad',
        'GITHUB_WEBHOOK_ENDPT': '/webhook',
        'GITHUB_WEBHOOK_SECRET': 'oiarstierstiemoiarno',
        'GITHUB_KEY': 'BEGIN END',

        'AWS_ACCESS_KEYID': '324098102',
        'AWS_SECRET_KEY': 'more secret',
        'AWS_USERS_TABLE': 'users',
        'AWS_TEAMS_TABLE': 'teams',
        'AWS_PROJECTS_TABLE': 'projects',
        'AWS_REGION': 'us-west-2',
    }
    return None


def test_complete_config(complete_config):
    """Test a few things from the completed config object."""
    assert complete_config.testing


def test_incomplete_config(incomplete_config):
    """Test a few things from an incompleted config object."""
    try:
        Config()
        assert False
    except MissingConfigError as e:
        missing_fields = ['SLACK_NOTIFICATION_CHANNEL', 'SLACK_SIGNING_SECRET',
                          'SLACK_API_TOKEN', 'SLACK_ANNOUNCEMENT_CHANNEL']
        for field in missing_fields:
            assert field in e.error
