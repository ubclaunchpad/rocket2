"""Interface to Github App API."""
from datetime import datetime, timedelta
import jwt
import requests


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
        url = "https://api.github.com/app"
        headers = self._gen_headers()
        return requests.get(url=url, headers=headers).json()

    def create_api_token(self):
        """
        Create installation token to make Github API requests.

        See
        https://developer.github.com/v3/apps/#create-a-new-installation-token
        for details.

        :return: Authenticated API token
        """
        url = "https://api.github.com/app/installations"
        headers = self._gen_headers()
        installation_id = requests.get(url=url,
                                       headers=headers).json()[0]['id']

        url = f"https://api.github.com/app/installations/" \
              f"{installation_id}/access_tokens"
        return requests.post(url=url, headers=headers).json()['token']

    def _gen_headers(self):
        if self.auth.is_expired():
            self.auth = self.app_auth_factory.create()
        return {
            'Authorization': f'Bearer {self.auth.token}',
            'Accept': 'application/vnd.github.machine-man-preview+json'
        }

    class GithubAppAuth:
        """Class to encapsulate JWT encoding for Github App API."""

        def __init__(self, app_id, private_key):
            """Initialize Github App authentication."""
            expiry = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
            payload = {
                'iat': datetime.utcnow(),
                'exp': expiry,
                'iss': app_id
            }
            self.expiry = expiry
            self.token = jwt.encode(payload,
                                    private_key,
                                    algorithm='RS256') \
                .decode('utf-8')

        def is_expired(self):
            """Check if Github App token is expired."""
            return datetime.utcnow() >= datetime.fromtimestamp(self.expiry)


class GithubAppAuthFactory:
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
