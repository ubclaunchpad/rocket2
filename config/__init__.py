"""Contain the dictionaries of configurations for all needed services."""
import os


class Config:
    """
    Load important informations from environmental variables.

    We load the information (secret keys, access keys, paths to public/private
    keys, etc.) from the environment. Pipenv already loads from the environment
    and from the .env files.
    """

    # Map name of env variable to python variable
    ENV_NAMES = {
        'TESTING': 'testing',

        'SLACK_BOT_CHANNEL': 'slack_bot_channel',
        'SLACK_SIGNING_SECRET': 'slack_signing_secret',
        'SLACK_API_TOKEN': 'slack_api_token',

        'GITHUB_APP_ID': 'github_app_id',
        'GITHUB_ORG_NAME': 'github_org_name',
        'GITHUB_WEBHOOK_ENDPT': 'github_webhook_endpt',
        'GITHUB_WEBHOOK_SECRET': 'github_webhook_secret',
        'GITHUB_KEY': 'github_key',

        'AWS_ACCESS_KEYID': 'aws_access_keyid',
        'AWS_SECRET_KEY': 'aws_secret_key',
        'AWS_USERS_TABLE': 'aws_users_tablename',
        'AWS_TEAMS_TABLE': 'aws_teams_tablename',
        'AWS_PROJECTS_TABLE': 'aws_projects_tablename',
        'AWS_REGION': 'aws_region',
    }

    def __init__(self):
        """
        Load environmental variables into self.

        :raises: MissingConfigError exception if any of the env variables
                 aren't found
        """
        self._set_attrs()
        missing_config_fields = []

        for var_name, var in self.ENV_NAMES.items():
            try:
                data = os.environ[var_name]
                setattr(self, var, data)
            except KeyError:
                missing_config_fields.append(var_name)

        if missing_config_fields:
            raise MissingConfigError(missing_config_fields)

        self.testing = self.testing == 'True'

    def _set_attrs(self):
        """Add attributes so that mypy doesn't complain."""
        self.testing = ''
        self.creds_path = ''

        self.slack_bot_channel = ''
        self.slack_signing_secret = ''
        self.slack_api_token = ''

        self.github_app_id = ''
        self.github_org_name = ''
        self.github_webhook_endpt = ''
        self.github_webhook_secret = ''
        self.github_key = ''

        self.aws_access_keyid = ''
        self.aws_secret_key = ''
        self.aws_users_tablename = ''
        self.aws_teams_tablename = ''
        self.aws_projects_tablename = ''
        self.aws_region = ''


class MissingConfigError(Exception):
    """Exception representing an error while loading credentials."""

    def __init__(self, missing_config_fields):
        """
        Initialize a new MissingConfigError.

        :param: missing_config_fields List of missing config variables
        """
        self.error = 'Please set the following env variables:\n' + \
            '\n'.join(missing_config_fields)
