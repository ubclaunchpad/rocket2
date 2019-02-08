"""Represent a team project."""
import hashlib
import time


class Project:
    """Represent a team project with team ID and related fields and methods."""

    def __init__(self, github_team_id, github_urls):
        """
        Initialize the team project.

        Project ID is just the current epoch time and the first github project
        URL mashed together using SHA1.

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
        p.set_project_id(d['project_id'])
        p.set_display_name(d.get('display_name', ''))
        p.set_short_description(d.get('short_description', ''))
        p.set_long_description(d.get('long_description', ''))
        p.set_tags(d.get('tags', []))
        p.set_website_url(d.get('website_url', ''))
        p.set_medium_url(d.get('medium_url', ''))
        p.set_appstore_url(d.get('appstore_url', ''))
        p.set_playstore_url(d.get('playstore_url', ''))

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
            'project_id': p.get_slack_id(),
            'github_urls': p.get_github_urls()
        }
        place_if_filled('github_team_id', p.get_github_team_id())
        place_if_filled('display_name', p.get_display_name())
        place_if_filled('short_description', p.get_short_description())
        place_if_filled('long_description', p.get_long_description())
        place_if_filled('tags', p.get_tags())
        place_if_filled('website_url', p.get_website_url())
        place_if_filled('appstore_url', p.get_appstore_url())
        place_if_filled('playstore_url', p.get_playstore_url())

        return udict

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
        return len(project.__project_id) > 0 and\
            len(project.__github_urls) > 0

    def __eq__(self, other):
        """Return true if this project is equal to the other project."""
        return str(self) == str(other)

    def __ne__(self, other):
        """Return true if this project isn't equal to the other project."""
        return not (self == other)

    def __str__(self):
        """Return all fields of this project, JSON format."""
        return str(self.__dict__)

    def get_project_id(self):
        """Return project ID."""
        return self.__project_id

    def get_github_team_id(self):
        """Return Github team ID."""
        return self.__github_team_id

    def get_github_urls(self):
        """Return links to a list of Github URLs."""
        return self.__github_urls

    def get_display_name(self):
        """Return name of project."""
        return self.__display_name

    def get_short_description(self):
        """Return a short description of the project."""
        return self.__short_description

    def get_long_description(self):
        """Return a long description of the project."""
        return self.__long_description

    def get_tags(self):
        """Return a list of tags used by Github."""
        return self.__tags

    def get_website_url(self):
        """Return a URL to the project website."""
        return self.__website_url

    def get_medium_url(self):
        """Return a URL to the project Medium page."""
        return self.__medium_url

    def get_appstore_url(self):
        """Return a URL to the project on the Appstore."""
        return self.__appstore_url

    def get_playstore_url(self):
        """Return a URL to the project on the Google Playstore."""
        return self.__playstore_url

    def set_project_id(self, project_id):
        """Set project ID."""
        self.__project_id = project_id

    def set_github_team_id(self, team_id):
        """Set Github team ID."""
        self.__github_team_id = team_id

    def set_github_urls(self, github_urls):
        """Set links to a list of Github URLs."""
        self.__github_urls = github_urls

    def set_display_name(self, display_name):
        """Set name of project."""
        self.__display_name = display_name

    def set_short_description(self, short_description):
        """Set a short description of the project."""
        self.__short_description = short_description

    def set_long_description(self, long_description):
        """Set a long description of the project."""
        self.__long_description = long_description

    def set_tags(self, tags):
        """Set a list of tags used by Github."""
        self.__tags = tags

    def set_website_url(self, website_url):
        """Set a URL to the project website."""
        self.__website_url = website_url

    def set_medium_url(self, medium_url):
        """Set a URL to the project Medium page."""
        self.__medium_url = medium_url

    def set_appstore_url(self, appstore_url):
        """Set a URL to the project on the Appstore."""
        self.__appstore_url = appstore_url

    def set_playstore_url(self, playstore_url):
        """Set a URL to the project on the Google Playstore."""
        self.__playstore_url = playstore_url
