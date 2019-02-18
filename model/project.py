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
        self.__project_id = hfunc.hexdigest()
        self.__github_team_id = github_team_id
        self.__github_urls = github_urls

        self.__display_name = ''
        self.__short_description = ''
        self.__long_description = ''
        self.__tags = []
        self.__website_url = ''
        self.__medium_url = ''
        self.__appstore_url = ''
        self.__playstore_url = ''

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

    @property
    def project_id(self):
        """Return project ID."""
        return self.__project_id

    @property
    def github_team_id(self):
        """Return Github team ID."""
        return self.__github_team_id

    @property
    def github_urls(self):
        """Return links to a list of Github URLs."""
        return self.__github_urls

    @property
    def display_name(self):
        """Return name of project."""
        return self.__display_name

    @property
    def short_description(self):
        """Return a short description of the project."""
        return self.__short_description

    @property
    def long_description(self):
        """Return a long description of the project."""
        return self.__long_description

    @property
    def tags(self):
        """Return a list of tags used by Github."""
        return self.__tags

    @property
    def website_url(self):
        """Return a URL to the project website."""
        return self.__website_url

    @property
    def medium_url(self):
        """Return a URL to the project Medium page."""
        return self.__medium_url

    @property
    def appstore_url(self):
        """Return a URL to the project on the Appstore."""
        return self.__appstore_url

    @property
    def playstore_url(self):
        """Return a URL to the project on the Google Playstore."""
        return self.__playstore_url

    @project_id.setter
    def project_id(self, project_id):
        """Set project ID."""
        self.__project_id = project_id

    @github_team_id.setter
    def github_team_id(self, team_id):
        """Set Github team ID."""
        self.__github_team_id = team_id

    @github_urls.setter
    def github_urls(self, github_urls):
        """Set links to a list of Github URLs."""
        self.__github_urls = github_urls

    @display_name.setter
    def display_name(self, display_name):
        """Set name of project."""
        self.__display_name = display_name

    @short_description.setter
    def short_description(self, short_description):
        """Set a short description of the project."""
        self.__short_description = short_description

    @long_description.setter
    def long_description(self, long_description):
        """Set a long description of the project."""
        self.__long_description = long_description

    @tags.setter
    def tags(self, tags):
        """Set a list of tags used by Github."""
        self.__tags = tags

    @website_url.setter
    def website_url(self, website_url):
        """Set a URL to the project website."""
        self.__website_url = website_url

    @medium_url.setter
    def medium_url(self, medium_url):
        """Set a URL to the project Medium page."""
        self.__medium_url = medium_url

    @appstore_url.setter
    def appstore_url(self, appstore_url):
        """Set a URL to the project on the Appstore."""
        self.__appstore_url = appstore_url

    @playstore_url.setter
    def playstore_url(self, playstore_url):
        """Set a URL to the project on the Google Playstore."""
        self.__playstore_url = playstore_url
