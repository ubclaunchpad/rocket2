"""Data model to represent an individual user."""
from typing import Dict, Any, TypeVar, Type
from app.model.permissions import Permissions
from app.model.base import RocketModel

T = TypeVar('T', bound='User')


class User(RocketModel):
    """Represent a user with related fields and methods."""

    def __init__(self, slack_id: str):
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
        self.karma = 1

    def get_attachment(self) -> Dict[str, Any]:
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
            ('Permissions Level', str(self.permissions_level)),
            ('Karma', self.karma)
        ]

        fields = [{'title': t, 'value': v if v else 'n/a', 'short': True}
                  for t, v in text_pairs]
        fallback = str('\n'.join(map(str, text_pairs)))

        return {'fallback': fallback, 'fields': fields}

    @classmethod
    def to_dict(cls: Type[T], user: T) -> Dict[str, Any]:
        """
        Convert user object to dict object.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.

        :param user: the user object
        :return: the dictionary representing the user
        """
        def place_if_filled(name: str, field: Any):
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
        place_if_filled('karma', user.karma)

        return udict

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> T:
        """
        Convert dict response object to user model.

        :param d: the dictionary representing a user
        :return: returns converted user model.
        """
        user = cls(d['slack_id'])
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
        user.karma = int(d.get('karma', 1))
        return user

    @classmethod
    def is_valid(cls: Type[T], user: T) -> bool:
        """
        Return true if this user has no missing required fields.

        Required fields for database to accept:
            - ``slack_id``
            - ``permissions_level``

        :param user: user to check
        :return: return true if this user has no missing required fields
        """
        return len(user.slack_id) > 0

    def __eq__(self, other: object) -> bool:
        """Return true if this user has the same attributes as the other."""
        return isinstance(other, User) and\
            str(self.__dict__) == str(other.__dict__)

    def __ne__(self, other: object) -> bool:
        """Return the opposite of what is returned in self.__eq__(other)."""
        return not self == other

    def __str__(self) -> str:
        """Print information on the user class."""
        return str(self.__dict__)
