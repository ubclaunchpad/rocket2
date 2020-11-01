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
        'SLACK_SIGNING_SECRET': 'slack_signing_secret',
        'SLACK_API_TOKEN': 'slack_api_token',
        'SLACK_NOTIFICATION_CHANNEL': 'slack_notification_channel',
        'SLACK_ANNOUNCEMENT_CHANNEL': 'slack_announcement_channel',
        'SLACK_PAIRING_CHANNEL': 'slack_pairing_channel',
        'GITHUB_APP_ID': 'github_app_id',
        'GITHUB_ORG_NAME': 'github_org_name',
        'GITHUB_DEFAULT_TEAM_NAME': 'github_team_all',
        'GITHUB_ADMIN_TEAM_NAME': 'github_team_admin',
        'GITHUB_LEADS_TEAM_NAME': 'github_team_leads',
        'GITHUB_WEBHOOK_ENDPT': 'github_webhook_endpt',
        'GITHUB_WEBHOOK_SECRET': 'github_webhook_secret',
        'GITHUB_KEY': 'github_key',

        'AWS_ACCESS_KEYID': 'aws_access_keyid',
        'AWS_SECRET_KEY': 'aws_secret_key',
        'AWS_USERS_TABLE': 'aws_users_tablename',
        'AWS_TEAMS_TABLE': 'aws_teams_tablename',
        'AWS_PAIRINGS_TABLE': 'aws_pairings_tablename',
        'AWS_PROJECTS_TABLE': 'aws_projects_tablename',
        'AWS_REGION': 'aws_region',
        'AWS_LOCAL': 'aws_local',

        'GCP_SERVICE_ACCOUNT_CREDENTIALS': 'gcp_service_account_credentials',
        'GCP_SERVICE_ACCOUNT_SUBJECT': 'gcp_service_account_subject'
    }
    OPTIONALS = {
        'AWS_LOCAL': 'False',
        'GITHUB_DEFAULT_TEAM_NAME': 'all',
        'GITHUB_ADMIN_TEAM_NAME': '',
        'GITHUB_LEADS_TEAM_NAME': '',
        'GCP_SERVICE_ACCOUNT_CREDENTIALS': '',
        'GCP_SERVICE_ACCOUNT_SUBJECT': '',
        'SLACK_PAIRING_CHANNEL': '',
        'AWS_PAIRINGS_TABLE': '',
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
                if len(data) == 0:
                    if var_name in self.OPTIONALS:
                        data = self.OPTIONALS[var_name]
                    else:
                        missing_config_fields.append(var_name)
                setattr(self, var, data)
            except KeyError:
                if var_name in self.OPTIONALS:
                    data = self.OPTIONALS[var_name]
                    setattr(self, var, data)
                else:
                    missing_config_fields.append(var_name)

        if missing_config_fields:
            raise MissingConfigError(missing_config_fields)

        self.aws_local = self.aws_local == 'True'
        self.github_key = self.github_key\
            .replace('\\n', '\n')\
            .replace('\\-', '-')

    def _set_attrs(self):
        """Add attributes so that mypy doesn't complain."""
        self.creds_path = ''

        self.slack_signing_secret = ''
        self.slack_api_token = ''
        self.slack_notification_channel = ''
        self.slack_announcement_channel = ''
        self.slack_pairing_channel = ''
        self.github_app_id = ''
        self.github_org_name = ''
        self.github_team_all = ''
        self.github_team_admin = ''
        self.github_team_leads = ''
        self.github_webhook_endpt = ''
        self.github_webhook_secret = ''
        self.github_key = ''

        self.aws_access_keyid = ''
        self.aws_secret_key = ''
        self.aws_users_tablename = ''
        self.aws_teams_tablename = ''
        self.aws_pairings_tablename = ''
        self.aws_projects_tablename = ''
        self.aws_region = ''
        self.aws_local: bool = False

        self.gcp_service_account_credentials = ''
        self.gcp_service_account_subject = ''


class MissingConfigError(Exception):
    """Exception representing an error while loading credentials."""

    def __init__(self, missing_config_fields):
        """
        Initialize a new MissingConfigError.

        :param missing_config_fields: the missing config variables
        """
        self.error = 'Please set the following env variables:\n' + \
            '\n'.join(missing_config_fields)
