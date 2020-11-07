"""Represent a Pairing between two users."""
from typing import Dict, Any, TypeVar, Type
import uuid
from app.model.base import RocketModel

T = TypeVar('T', bound='Pairing')


class Pairing(RocketModel):
    """Represent a pairing and related fields and methods."""

    def __init__(self,
                 user1_slack_id: str,
                 user2_slack_id: str):
        """
        Initialize the pairing.

        The generated ``pairing_id`` property is meant to uniquely
        represent a pairing.

        :param user1_slack_id: The slack ID of the first user
        :param user2_slack_id: The slack ID of the second user
        """
        self.pairing_id = str(uuid.uuid4())
        self.user1_slack_id = user1_slack_id
        self.user2_slack_id = user2_slack_id
        self.ttl = "TODO"  # TODO

    def get_attachment(self) -> Dict[str, Any]:
        """Return slack-formatted attachment (dictionary) for pairing."""
        text_pairs = [
            ('Pairing ID', self.pairing_id),
            ('User 1 Slack ID', self.user1_slack_id),
            ('User 2 Slack ID', self.user2_slack_id),
            ('TTL', self.ttl)
        ]

        fields = [{'title': t, 'value': v if v else 'n/a', 'short': True}
                  for t, v in text_pairs]
        fallback = str('\n'.join(map(str, text_pairs)))

        return {'fallback': fallback, 'fields': fields}

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> T:
        """
        Return a pairing from a dict object.

        :param d: the dictionary (usually from DynamoDB)
        :return: a Pairing object
        """
        p = cls(d['user1_slack_id'], d['user2_slack_id'])
        p.pairing_id = d['pairing_id']
        p.ttl = d['ttl']
        return p

    @classmethod
    def to_dict(cls: Type[T], p: T) -> Dict[str, Any]:
        """
        Return a dict object representing a pairing.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.

        :param p: the Pairing object
        :return: a dictionary representing a pairing
        """
        def place_if_filled(name: str, field: Any):
            """Populate ``udict`` if ``field`` isn't empty."""
            if field:
                udict[name] = field

        udict = {
            'pairing_id': p.pairing_id,
            'user1_slack_id': p.user1_slack_id,
            'user2_slack_id': p.user2_slack_id
        }
        place_if_filled('ttl', p.ttl)

        return udict

    @classmethod
    def is_valid(cls: Type[T], p: T) -> bool:
        """
        Return true if this pairing has no missing fields.

        Required fields for database to accept:
            - ``__pairing_id``
            - ``__user1_slack_id``
            - ``__user2_slack_id``

        :param pairing: pairing to check
        :return: true if this pairing has no missing fields
        """
        return len(p.pairing_id) > 0 and\
            len(p.user1_slack_id) > 0 and len(p.user2_slack_id) > 0

    def __eq__(self, other: object) -> bool:
        """Return true if this pairing is equal to the other pairing."""
        return isinstance(other, Pairing) and str(self) == str(other)

    def __ne__(self, other: object) -> bool:
        """Return true if this pairing isn't equal to the other pairing."""
        return not (self == other)

    def __str__(self) -> str:
        """Return all fields of this pairing, JSON format."""
        return str(self.__dict__)

    def __hash__(self) -> int:
        """Hash the pairing class using a dictionary."""
        return self.__str__().__hash__()
