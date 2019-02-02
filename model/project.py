"""Represent a team project."""
import hashlib
import time


class Project:
    """
    Represent a team project with team ID and other related fields and methods.
    """

    def __init__(self, github_team_id, github_urls):
        """
        Initialize the team project.

        Project ID is just the current epoch time and the first github project
        URL mashed together using SHA1.
        """
        hfunc = hashlib.sha1()
        hfunc.update(bytes(github_urls[0], 'utf-8'))
        hfunc.update(bytes(str(time.time()), 'utf-8'))
        self.__project_id = hfunc.hexdigest()
        self.__github_team_id = github_team_id
        self.__github_urls = github_urls

        self.__display_name = ''
        self.__short_description = ''
        self.__long_desscription = ''
        self.__tags = []
        self.__website_url = ''
        self.__medium_url = ''
        self.__appstore_url = ''
        self.__playstore_url = ''

    @staticmethod
    def is_valid(project):
        """
        Return true if this project has no missing fields.

        Required fields for database to accept:
        - ``__project_id``
        - ``__github_urls``

        :param project: project to check
        :return: true if this project has no missing fields
        """
        # TODO
        return True
