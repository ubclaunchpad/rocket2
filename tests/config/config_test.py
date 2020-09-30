"""Test the loading of config."""
from unittest import TestCase
from config import Config, MissingConfigError
import os


class TestConfig(TestCase):
    """Test error handling of configuration initialization."""

    def setUp(self):
        """Set up environments and variables."""
        self.complete_config = {
            'SLACK_SIGNING_SECRET': 'something secret',
            'SLACK_API_TOKEN': 'some token idk',
            'SLACK_NOTIFICATION_CHANNEL': '#rocket2',
            'SLACK_ANNOUNCEMENT_CHANNEL': '#ot-random',

            'GITHUB_APP_ID': '2024',
            'GITHUB_ORG_NAME': 'ubclaunchpad',
            'GITHUB_WEBHOOK_ENDPT': '/webhook',
            'GITHUB_WEBHOOK_SECRET': 'oiarstierstiemoiarno',
            'GITHUB_DEFAULT_TEAM_NAME': '',
            'GITHUB_KEY': 'BEGIN END',

            'AWS_ACCESS_KEYID': '324098102',
            'AWS_SECRET_KEY': 'more secret',
            'AWS_USERS_TABLE': 'users',
            'AWS_TEAMS_TABLE': 'teams',
            'AWS_PROJECTS_TABLE': 'projects',
            'AWS_REGION': 'us-west-2',
            'AWS_LOCAL': 'True',

            'GCP_SERVICE_ACCOUNT_CREDENTIALS': '{"hello":"world"}',
        }
        self.incomplete_config = {
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

    def test_complete_config(self):
        """Test a few things from the completed config object."""
        os.environ = self.complete_config
        conf = Config()
        self.assertTrue(conf.aws_local)
        self.assertEqual(conf.gcp_service_account_credentials,
                         '{"hello":"world"}')

    def test_incomplete_config(self):
        """Test a few things from an incompleted config object."""
        with self.assertRaises(MissingConfigError) as e:
            os.environ = self.incomplete_config
            Config()

        missing_fields = ['SLACK_NOTIFICATION_CHANNEL', 'SLACK_SIGNING_SECRET',
                          'SLACK_API_TOKEN', 'SLACK_ANNOUNCEMENT_CHANNEL']
        optional_fields = ['AWS_LOCAL']
        e = e.exception
        for field in missing_fields:
            self.assertIn(field, e.error)
        for field in optional_fields:
            self.assertNotIn(field, e.error)
