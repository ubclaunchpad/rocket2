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
        self.missing_cred_files = []
        self.missing_cred_fields = {}

        slack_toml_path = join(credentials_path, 'slack.toml')
        try:
            slack_toml = toml.load(slack_toml_path)
            self.slack_signing_secret = self.attempt_toml_read(
                slack_toml, 'signing_secret', 'slack')
            self.slack_api_token = self.attempt_toml_read(
                slack_toml, 'api_token', 'slack')
        except IOError:
            self.missing_cred_files.append('slack.toml')

        aws_toml_path = join(credentials_path, 'aws.toml')
        try:
            aws_toml = toml.load(aws_toml_path)
            self.aws_access_key_id = self.attempt_toml_read(
                aws_toml, 'access_key_id', 'aws')
            self.aws_secret_access_key = self.attempt_toml_read(
                aws_toml, 'secret_access_key', 'aws')
        except IOError:
            self.missing_cred_files.append('aws.toml')

        github_toml_path = join(credentials_path, 'github.toml')
        try:
            github_toml = toml.load(github_toml_path)
            self.github_webhook_secret = self.attempt_toml_read(
                github_toml, 'webhook_secret', 'github')
        except IOError:
            self.missing_cred_files.append('github.toml')

        github_signing_key_path = join(
            credentials_path, 'github_signing_key.pem')
        if isfile(github_signing_key_path):
            self.github_signing_key_path = github_signing_key_path
        else:
            self.missing_cred_files.append('github_signing_key.pem')

        if len(self.missing_cred_files) > 0 or \
                len(self.missing_cred_fields) > 0:
            raise MissingCredentialsError(self.missing_cred_files,
                                          self.missing_cred_fields)

    def attempt_toml_read(self, toml_dict, key, service):
        """
        Attempt to get a value from the toml dictionary given a key.

        :param toml_dict: dictionary derived from toml file being attempted
                          to be read from
        :param service: name of the service whose type of credential
                        belongs to, and the key to the list of its missing
                        credentials fields in the `missing_creds_fields` dict
        :param key: key being attempted to read from the toml_dict with
        :return: value associated with key if the key exists in the toml_dict,
                 None if it does not exist
        """
        try:
            value = toml_dict[key]
            return value
        except KeyError:
            try:
                missing_fields = self.missing_cred_fields[service]
                missing_fields.append(key)
                self.missing_cred_fields[service] = missing_fields
            except KeyError:
                self.missing_cred_fields[service] = [key]
            return None


class MissingCredentialsError(Exception):
    """Exception representing an error while loading credentials."""

    def __init__(self, missing_cred_files, missing_cred_fields):
        """
        Initialize a new MissingCredentialsError.

        : param missing_cred_files: List of missing files of credentials.
        """
        self.error = f'Missing files: {str(missing_cred_files)}\n' \
            f'Missing fields: {str(missing_cred_fields)}'
