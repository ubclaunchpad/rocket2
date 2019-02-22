"""Represent a team project."""
import hashlib
import time


class Project:
    """Represent a team project with team ID and related fields and methods."""

    def __init__(self, github_team_id, github_urls):
        """
        Initialize the team project.

        Project ID is a SHA1 generated from the first Github project URL and
        epoch time.

        :param github_team_id: the Github team ID associated with the project
        :param github_urls: a set/list of URLs pointing to repositories
        """
        hfunc = hashlib.sha1()
        hfunc.update(bytes(github_urls[0], 'utf-8'))
        hfunc.update(bytes(str(time.time()), 'utf-8'))
        self.project_id = hfunc.hexdigest()
        self.github_team_id = github_team_id
        self.github_urls = github_urls

        self.display_name = ''
        self.short_description = ''
        self.long_description = ''
        self.tags = []
        self.website_url = ''
        self.medium_url = ''
        self.appstore_url = ''
        self.playstore_url = ''

    @staticmethod
    def from_dict(d):
        """
        Return a project from a dict object.

        :param d: the dictionary (usually from DynamoDB)
        :return: a Project object
        """
        p = Project(d['github_team_id'], d['github_urls'])
        p.project_id = d['project_id']
        p.display_name = d.get('display_name', '')
        p.short_description = d.get('short_description', '')
        p.long_description = d.get('long_description', '')
        p.tags = d.get('tags', [])
        p.website_url = d.get('website_url', '')
        p.medium_url = d.get('medium_url', '')
        p.appstore_url = d.get('appstore_url', '')
        p.playstore_url = d.get('playstore_url', '')

        return p

    @staticmethod
    def to_dict(p):
        """
        Return a dict object representing a project.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.

        :param p: the Project object
        :return: a dictionary representing a project
        """
        def place_if_filled(name, field):
            """Populate ``udict`` if ``field`` isn't empty."""
            if field:
                udict[name] = field

        udict = {
            'project_id': p.project_id,
            'github_urls': p.github_urls
        }
        place_if_filled('github_team_id', p.github_team_id)
        place_if_filled('display_name', p.display_name)
        place_if_filled('short_description', p.short_description)
        place_if_filled('long_description', p.long_description)
        place_if_filled('tags', p.tags)
        place_if_filled('website_url', p.website_url)
        place_if_filled('appstore_url', p.appstore_url)
        place_if_filled('playstore_url', p.playstore_url)

        return udict

    @staticmethod
    def is_valid(p):
        """
        Return true if this project has no missing fields.

        Required fields for database to accept:
        - ``__project_id``
        - ``__github_urls``

        :param project: project to check
        :return: true if this project has no missing fields
        """
        return len(p.project_id) > 0 and\
            len(p.github_urls) > 0

    def __eq__(self, other):
        """Return true if this project is equal to the other project."""
        return str(self) == str(other)

    def __ne__(self, other):
        """Return true if this project isn't equal to the other project."""
        return not (self == other)

    def __str__(self):
        """Return all fields of this project, JSON format."""
        return str(self.__dict__)
