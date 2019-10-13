"""Interface to Github App API."""
import jwt
import requests

from datetime import datetime, timedelta
from interface.exceptions.github import GithubAPIException
import logging


class GithubAppInterface:
    """Interface class for interacting with Github App API."""

    def __init__(self, app_auth_factory):
        """
        Initialize GithubAppInterface.

        :param app_auth_factory: Factory for creating auth objects
        """
        self.app_auth_factory = app_auth_factory
        self.auth = app_auth_factory.create()

    def get_app_details(self):
        """
        Retrieve app details from Github Apps API.

        See
        https://developer.github.com/v3/apps/#get-the-authenticated-github-app
        for details.

        :return: Decoded JSON object containing app details
        """
        logging.info("Attempting to retrieve Github App details")
        url = "https://api.github.com/app"
        headers = self._gen_headers()
        r = requests.get(url=url, headers=headers)
        if r.status_code != 200:
            logging.error("Failed to get Github App details with message "
                          f"{r.text} and error code {r.status_code}")
            raise GithubAPIException(r.text)
        logging.info("Successfully retrieved Github App details: "
                     f"{r.json()}")
        return r.json()

    def create_api_token(self):
        """
        Create installation token to make Github API requests.

        See
        https://developer.github.com/v3/apps/#find-installations and
        https://developer.github.com/v3/apps/#create-a-new-installation-token
        for details.

        :return: Authenticated API token
        """
        logging.info("Attempting to get list of installations")
        url = "https://api.github.com/app/installations"
        headers = self._gen_headers()
        r = requests.get(url=url,
                         headers=headers)
        if r.status_code != 200:
            logging.error("Failed to get list of Github App installations "
                          f"with error message {r.text} "
                          f"and code {r.status_code}")
            raise GithubAPIException(r.text)
        installation_id = r.json()[0]['id']

        logging.info("Attempting to create new installation token")
        url = f"https://api.github.com/app/installations/" \
              f"{installation_id}/access_tokens"
        r = requests.post(url=url, headers=headers)
        if r.status_code != 201:
            logging.error("Failed to create new installation token "
                          f"with error message {r.text} "
                          f"and code {r.status_code}")
            raise GithubAPIException(r.text)
        return r.json()['token']

    def _gen_headers(self):
        if self.auth.is_expired():
            logging.info("GithubAppAuth expired, creating new instance")
            self.auth = self.app_auth_factory.create()
        return {
            'Authorization': f'Bearer {self.auth.token}',
            'Accept': 'application/vnd.github.machine-man-preview+json'
        }

    class GithubAppAuth:
        """Class to encapsulate JWT encoding for Github App API."""

        def __init__(self, app_id, private_key):
            """Initialize Github App authentication."""
            self.expiry = (datetime.utcnow() + timedelta(minutes=1))
            payload = {
                'iat': datetime.utcnow(),
                'exp': self.expiry,
                'iss': app_id
            }
            self.token = jwt.encode(payload,
                                    private_key,
                                    algorithm='RS256') \
                .decode('utf-8')

        def is_expired(self):
            """Check if Github App token is expired."""
            return datetime.utcnow() >= self.expiry


class DefaultGithubAppAuthFactory:
    """Factory for creating GithubAppAuth objects."""

    def __init__(self, app_id, private_key):
        """
        Initialize a Github App API auth factory.

        :param app_id: Github Apps ID
        :param private_key: Private key from application
        """
        self.app_id = app_id
        self.private_key = private_key
        self.auth = GithubAppInterface.GithubAppAuth

    def create(self):
        """Create an instance of GithubAppAuth."""
        return self.auth(self.app_id, self.private_key)
