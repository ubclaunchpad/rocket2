"""Represent a data model for a team."""
from typing import Set, Dict, Any, TypeVar, Type
from app.model.base import RocketModel

T = TypeVar('T', bound='Team')


class Team(RocketModel):
    """Represent a team with related fields and methods."""

    def __init__(self,
                 github_team_id: str,
                 github_team_name: str,
                 displayname: str):
        """
        Initialize the team.

        Parameters are a valid Github team ID, team name and display name.
        """
        self.github_team_id = github_team_id
        self.github_team_name = github_team_name
        self.displayname = displayname
        self.platform = ""
        self.team_leads: Set[str] = set()
        self.members: Set[str] = set()
        self.folder = ""

    def get_attachment(self):
        """Return slack-formatted attachment (dictionary) for team."""
        text_pairs = [
            ('Github ID', self.github_team_id),
            ('Github Team Name', self.github_team_name),
            ('Display Name', self.displayname),
            ('Platform', self.platform),
            ('Folder', self.folder),
            ('Team Leads', '\n'.join(self.team_leads)),
            ('Members', '\n'.join(self.members))
        ]
        fields = [{'title': t, 'value': v if v else 'n/a', 'short': True}
                  for t, v in text_pairs]
        fallback = str('\n'.join(map(str, text_pairs)))

        return {'fallback': fallback, 'fields': fields}

    def get_basic_attachment(self):
        """Return basic slack-formatted attachment (dictionary) for team."""
        text_pairs = [
            ('Github ID', self.github_team_id),
            ('Github Team Name', self.github_team_name),
            ('Display Name', self.displayname),
            ('Platform', self.platform),
        ]
        fields = [{'title': t, 'value': v if v else 'n/a', 'short': True}
                  for t, v in text_pairs]
        fallback = str('\n'.join(map(str, text_pairs)))

        return {'fallback': fallback, 'fields': fields}

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> T:
        """
        Convert dict response object to team model.

        :param d: the dictionary representing a team
        :return: the converted team model.
        """
        team = cls(d['github_team_id'],
                   d['github_team_name'],
                   d.get('displayname', ''))
        team.platform = d.get('platform', '')
        team.folder = d.get('folder', '')
        team.team_leads = set(d.get('team_leads', []))
        members = set(d.get('members', []))
        for member in members:
            team.add_member(member)
        return team

    @classmethod
    def to_dict(cls: Type[T], team: T) -> Dict[str, Any]:
        """
        Convert team object to dict object.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.

        :param team: the team object
        :return: the dictionary representing the team
        """
        def place_if_filled(name: str, field: Any):
            """Populate ``tdict`` if ``field`` isn't empty."""
            if field:
                tdict[name] = field

        tdict = {
            'github_team_id': team.github_team_id,
            'github_team_name': team.github_team_name
        }
        place_if_filled('displayname', team.displayname)
        place_if_filled('platform', team.platform)
        place_if_filled('members', team.members)
        place_if_filled('team_leads', team.team_leads)
        place_if_filled('folder', team.folder)

        return tdict

    @classmethod
    def is_valid(cls: Type[T], team: T) -> bool:
        """
        Return true if this team has no missing required fields.

        Required fields for database to accept:
            - ``github_team_name``
            - ``github_team_id``

        :param team: team to check
        :return: true if this team has no missing required fields
        """
        return len(team.github_team_name) > 0 and\
            len(team.github_team_id) > 0

    def __eq__(self, other: object) -> bool:
        """Return true if this team has the same attributes as the other."""
        return isinstance(other, Team) and str(self) == str(other)

    def __ne__(self, other: object) -> bool:
        """Return the opposite of what is returned in self.__eq__(other)."""
        return not (self == other)

    def add_member(self, github_user_id: str):
        """Add a new member's Github ID to the team's set of members' IDs."""
        self.members.add(github_user_id)

    def discard_member(self, github_user_id: str):
        """Discard the member of the team with Github ID in the argument."""
        self.members.discard(github_user_id)

    def has_member(self, github_user_id: str) -> bool:
        """Identify if any member has the ID specified in the argument."""
        return github_user_id in self.members

    def add_team_lead(self, github_user_id: str):
        """Add a user's Github ID to the team's set of team lead IDs."""
        self.team_leads.add(github_user_id)

    def is_team_lead(self, github_user_id: str) -> bool:
        """Identify if user with given ID is a team lead."""
        return github_user_id in self.team_leads

    def has_team_lead(self, github_user_id: str) -> bool:
        """Identify if user with given ID is a team lead."""
        return github_user_id in self.team_leads

    def discard_team_lead(self, github_user_id: str):
        """Remove a user's Github ID to the team's set of team lead IDs."""
        self.team_leads.remove(github_user_id)

    def __str__(self) -> str:
        """Print information on the team class."""
        return str(self.__dict__)

    def __hash__(self) -> int:
        """Hash the team class using a dictionary."""
        return self.__str__().__hash__()
