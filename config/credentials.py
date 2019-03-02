"""Contain the dictionaries of credentials for all needed services."""
from os import listdir
from os.path import isfile, join
import toml


class Credentials:
    """Abstract away the loading of toml files."""

    def __init__(self, credentials_path):
        """
        Collect the toml dictionaries for credentials of needed services.

        :param credentials_path: path to folder that contains toml files
                                 of credentials for all needed services
        """
        missing_creds_list = []

        slack_toml_path = join(credentials_path, 'slack.toml')
        try:
            self.slack = toml.load(slack_toml_path)
        except IOError:
            missing_creds_list.append(slack_toml_path)

        github_toml_path = join(credentials_path, 'github.toml')
        try:
            self.github = toml.load(github_toml_path)
        except IOError:
            missing_creds_list.append(github_toml_path)

        aws_toml_path = join(credentials_path, 'aws.toml')
        try:
            self.aws = toml.load(aws_toml_path)
        except IOError:
            missing_creds_list.append(aws_toml_path)

        if len(missing_creds_list) > 0:
            raise MissingCredentialsError(missing_creds_list)


class MissingCredentialsError(Exception):
    """Exception representing an error while loading credentials."""

    def __init__(self, missing_creds_list):
        """
        Initialize a new MissingCredentialsError.

        :param missing_creds_list: List of missing toml files of credentials.
        """
        self.error = 'Missing credentials files: ' + str(missing_creds_list)
