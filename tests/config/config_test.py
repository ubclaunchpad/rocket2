"""Test the loading of config."""
import pytest
from config import Config, MissingConfigError
import os


@pytest.fixture
def complete_config():
    """Return a config object with complete attributes."""
    os.environ = {
        'TESTING': 'True',
        'CREDS_PATH': 'creds_path',

        'SLACK_BOT_CHANNEL': '#rocket2',
        'SLACK_SIGNING_SECRET': 'something secret',
        'SLACK_API_TOKEN': 'some token idk',

        'GITHUB_APP_ID': '2024',
        'GITHUB_ORG_NAME': 'ubclaunchpad',
        'GITHUB_WEBHOOK_ENDPT': '/webhook',
        'GITHUB_WEBHOOK_SECRET': 'oiarstierstiemoiarno',
        'GITHUB_KEY_FILE': 'github-signing-key.pem',

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
        'CREDS_PATH': 'creds_path',

        'GITHUB_APP_ID': '2024',
        'GITHUB_ORG_NAME': 'ubclaunchpad',
        'GITHUB_WEBHOOK_ENDPT': '/webhook',
        'GITHUB_WEBHOOK_SECRET': 'oiarstierstiemoiarno',
        'GITHUB_KEY_FILE': 'github-signing-key.pem',

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
    assert complete_config.creds_path in complete_config.github_key_file


def test_incomplete_config(incomplete_config):
    """Test a few things from an incompleted config object."""
    try:
        Config()
        assert False
    except MissingConfigError as e:
        missing_fields = ['SLACK_BOT_CHANNEL', 'SLACK_SIGNING_SECRET',
                          'SLACK_API_TOKEN']
        for field in missing_fields:
            assert field in e.error
