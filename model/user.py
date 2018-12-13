"""Data model to represent an individual user."""
from model.permissions import Permissions


class User:
    """Represent a user with related fields and methods."""

    def __init__(self, slack_id):
        """Initialize the user with a given Slack ID."""
        self.__slack_id = slack_id
        self.__name = ""
        self.__email = ""
        self.__github_username = ""
        self.__major = ""
        self.__position = ""
        self.__biography = ""
        self.__image_url = ""
        self.__permissions_level = Permissions.member

    def get_attachment(self):
        """Return slack-formatted attachment (dictionary) for user."""
        text_pairs = [
            ('Slack ID', self.__slack_id),
            ('Name', self.__name),
            ('Email', self.__email),
            ('Github Username', self.__github_username),
            ('Major', self.__major),
            ('Position', self.__position),
            ('Biography', self.__biography),
            ('Image URL', self.__image_url),
            ('Permissions Level', str(self.__permissions_level))
        ]

        fields = [{'title': t, 'value': v if v else 'n/a', 'short': True}
                  for t, v in text_pairs]
        fallback = str('\n'.join(map(str, text_pairs)))

        return {'fallback': fallback, 'fields': fields}

    @staticmethod
    def is_valid(user):
        """
        Return true if this user has no missing required fields.

        Required fields for database to accept:
        - ``__slack_id``
        - ``__permissions_level``

        :param user: user to check
        :return: return true if this user has no missing required fields
        """
        return len(user.get_slack_id()) > 0

    def __eq__(self, other):
        """Return true if this user has the same attributes as the other."""
        return str(self.__dict__) == str(other.__dict__)

    def __ne__(self, other):
        """Return the opposite of what is returned in self.__eq__(other)."""
        return not self == other

    def get_slack_id(self):
        """Return this user's Slack ID."""
        return self.__slack_id

    def get_name(self):
        """Return this user's display name."""
        return self.__name

    def set_name(self, name):
        """Set this user's display name to the given name."""
        self.__name = name

    def get_email(self):
        """Return this user's email."""
        return self.__email

    def set_email(self, email):
        """Set this user's email to the given argument."""
        self.__email = email

    def get_github_username(self):
        """Return this user's Github username."""
        return self.__github_username

    def set_github_username(self, github_username):
        """Set this user's Github username to the given argument."""
        self.__github_username = github_username

    def get_major(self):
        """Return this user's major."""
        return self.__major

    def set_major(self, major):
        """Set this user's major to the given argument."""
        self.__major = major

    def get_position(self):
        """Return this user's position."""
        return self.__position

    def set_position(self, position):
        """Set this user's position to the given argument."""
        self.__position = position

    def get_biography(self):
        """Return this user's biography."""
        return self.__biography

    def set_biography(self, biography):
        """Set this user's biography to the given argument."""
        self.__biography = biography

    def get_image_url(self):
        """Return this user's image URL."""
        return self.__image_url

    def set_image_url(self, image_url):
        """Set this user's image URL to the given argument."""
        self.__image_url = image_url

    def get_permissions_level(self):
        """Return this user's permissions level."""
        return self.__permissions_level

    def set_permissions_level(self, permissions_level):
        """Set this user's permissions level to the given argument."""
        self.__permissions_level = permissions_level

    def __str__(self):
        """Print information on the user class."""
        return str(self.__dict__)
