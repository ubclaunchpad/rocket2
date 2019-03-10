"""Exceptions from interacting with Github API."""


class GithubAPIException(Exception):
    """Exception representing an error while calling Github API."""

    def __init__(self, data):
        """
        Initialize a new GithubAPIException.

        :param data:
        """
        self.data = data
