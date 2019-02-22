"""Data model to represent an individual user."""
from model.permissions import Permissions


class User:
    """Represent a user with related fields and methods."""

    def __init__(self, slack_id):
        """Initialize the user with a given Slack ID."""
        self.slack_id = slack_id
        self.name = ""
        self.email = ""
        self.github_username = ""
        self.github_id = ""
        self.major = ""
        self.position = ""
        self.biography = ""
        self.image_url = ""
        self.permissions_level = Permissions.member

    def get_attachment(self):
        """Return slack-formatted attachment (dictionary) for user."""
        # TODO: Refactor into another file to preserve purity
        text_pairs = [
            ('Slack ID', self.slack_id),
            ('Name', self.name),
            ('Email', self.email),
            ('Github Username', self.github_username),
            ('Github ID', self.github_id),
            ('Major', self.major),
            ('Position', self.position),
            ('Biography', self.biography),
            ('Image URL', self.image_url),
            ('Permissions Level', str(self.permissions_level))
        ]

        fields = [{'title': t, 'value': v if v else 'n/a', 'short': True}
                  for t, v in text_pairs]
        fallback = str('\n'.join(map(str, text_pairs)))

        return {'fallback': fallback, 'fields': fields}

    @staticmethod
    def to_dict(user):
        """
        Convert user object to dict object.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.

        :param user: the user object
        :return: the dictionary representing the user
        """
        def place_if_filled(name, field):
            """Populate ``udict`` if ``field`` isn't empty."""
            if field:
                udict[name] = field

        udict = {
            'slack_id': user.slack_id,
            'permission_level': user.permissions_level.name
        }
        place_if_filled('email', user.email)
        place_if_filled('name', user.name)
        place_if_filled('github', user.github_username)
        place_if_filled('github_user_id', user.github_id)
        place_if_filled('major', user.major)
        place_if_filled('position', user.position)
        place_if_filled('bio', user.biography)
        place_if_filled('image_url', user.image_url)

        return udict

    @staticmethod
    def from_dict(d):
        """
        Convert dict response object to user model.

        :param d: the dictionary representing a user
        :return: returns converted user model.
        """
        user = User(d['slack_id'])
        user.email = d.get('email', '')
        user.name = d.get('name', '')
        user.github_username = d.get('github', '')
        user.github_id = d.get('github_user_id', '')
        user.major = d.get('major', '')
        user.position = d.get('position', '')
        user.biography = d.get('bio', '')
        user.image_url = d.get('image_url', '')
        user.permissions_level = Permissions[d.get('permission_level',
                                                   'member')]
        return user

    @staticmethod
    def is_valid(user):
        """
        Return true if this user has no missing required fields.

        Required fields for database to accept:
        - ``slack_id``
        - ``permissions_level``

        :param user: user to check
        :return: return true if this user has no missing required fields
        """
        return len(user.slack_id) > 0

    def __eq__(self, other):
        """Return true if this user has the same attributes as the other."""
        return str(self.__dict__) == str(other.__dict__)

    def __ne__(self, other):
        """Return the opposite of what is returned in self.__eq__(other)."""
        return not self == other

    def __str__(self):
        """Print information on the user class."""
        return str(self.__dict__)
