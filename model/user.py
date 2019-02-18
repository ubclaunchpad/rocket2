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
        self.__github_id = ""
        self.__major = ""
        self.__position = ""
        self.__biography = ""
        self.__image_url = ""
        self.__permissions_level = Permissions.member
        self.__karma = 1

    def get_attachment(self):
        """Return slack-formatted attachment (dictionary) for user."""
        # TODO: Refactor into another file to preserve purity
        text_pairs = [
            ('Slack ID', self.__slack_id),
            ('Name', self.__name),
            ('Email', self.__email),
            ('Github Username', self.__github_username),
            ('Github ID', self.__github_id),
            ('Major', self.__major),
            ('Position', self.__position),
            ('Biography', self.__biography),
            ('Image URL', self.__image_url),
            ('Permissions Level', str(self.__permissions_level)),
            ('Karma', self.__karma)
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
            'slack_id': user.get_slack_id(),
            'permission_level': user.get_permissions_level().name
        }
        place_if_filled('email', user.get_email())
        place_if_filled('name', user.get_name())
        place_if_filled('github', user.get_github_username())
        place_if_filled('github_user_id', user.get_github_id())
        place_if_filled('major', user.get_major())
        place_if_filled('position', user.get_position())
        place_if_filled('bio', user.get_biography())
        place_if_filled('image_url', user.get_image_url())

        return udict

    @staticmethod
    def from_dict(d):
        """
        Convert dict response object to user model.

        :param d: the dictionary representing a user
        :return: returns converted user model.
        """
        user = User(d['slack_id'])
        user.set_email(d.get('email', ''))
        user.set_name(d.get('name', ''))
        user.set_github_username(d.get('github', ''))
        user.set_github_id(d.get('github_user_id', ''))
        user.set_major(d.get('major', ''))
        user.set_position(d.get('position', ''))
        user.set_biography(d.get('bio', ''))
        user.set_image_url(d.get('image_url', ''))
        user.set_permissions_level(Permissions[d.get('permission_level',
                                                     'member')])
        return user

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
        """
        Set this user's Github username to the given argument.

        Also sends request to get matching Github ID and sets it for user.
        """
        self.__github_username = github_username
        # stub, fetch github_id, and set it

    def get_github_id(self):
        """Return this user's Github ID."""
        return self.__github_id

    def set_github_id(self, github_user_id):
        """Set this user's Github ID."""
        self.__github_id = github_user_id

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

    def reset_karma(self):
        """Resets amount of karma for a user, default is one"""
        self.__karma = 1

    def add_karma_by_amount(self, amount):
        """Adds karma by amount"""
        self.__karma += amount

    def remove_karma_by_amount(self, amount):
        """Removes karma by amount"""
        self.__karma -= amount
        if self.__karma <= 0:
           self.reset_karma

    def get_karma(self):
        """Returns amount of karma for a User"""
        return self.__karma
