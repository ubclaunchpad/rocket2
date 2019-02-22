"""Represent a data model for a team."""


class Team:
    """Represent a team with related fields and methods."""

    def __init__(self, github_team_id, github_team_name, display_name):
        """
        Initialize the team.

        Parameters are a valid Github team ID, team name and display name.
        """
        self.github_team_id = github_team_id
        self.github_team_name = github_team_name
        self.display_name = display_name
        self.platform = ""
        self.members = set()

    @staticmethod
    def from_dict(d):
        """
        Convert dict response object to team model.

        :param d: the dictionary representing a team
        :return: returns converted team model.
        """
        team = Team(d['github_team_id'],
                    d['github_team_name'],
                    d.get('display_name', ''))
        team.platform = d.get('platform', '')
        members = set(d.get('members', []))
        for member in members:
            team.add_member(member)
        return team

    @staticmethod
    def to_dict(team):
        """
        Convert team object to dict object.

        The difference with the in-built ``self.__dict__`` is that this is more
        compatible with storing into NoSQL databases like DynamoDB.

        :param team: the team object
        :return: the dictionary representing the team
        """
        def place_if_filled(name, field):
            """Populate ``tdict`` if ``field`` isn't empty."""
            if field:
                tdict[name] = field

        tdict = {
            'github_team_id': team.github_team_id,
            'github_team_name': team.github_team_name
        }
        place_if_filled('display_name', team.display_name)
        place_if_filled('platform', team.platform)
        place_if_filled('members', team.members)

        return tdict

    @staticmethod
    def is_valid(team):
        """
        Return true if this team has no missing required fields.

        Required fields for database to accept:
        - ``github_team_name``
        - ``github_team_id``

        :param team: team to check
        :return: returns true if this team has no missing required fields
        """
        return len(team.github_team_name) > 0 and\
            len(team.github_team_id) > 0

    def __eq__(self, other):
        """Return true if this team has the same attributes as the other."""
        return str(self) == str(other)

    def __ne__(self, other):
        """Return the opposite of what is returned in self.__eq__(other)."""
        return not (self == other)

    def add_member(self, github_user_id):
        """Add a new member's Github ID to the team's set of members' IDs."""
        self.members.add(github_user_id)

    def discard_member(self, github_user_id):
        """Discard the member of the team with Github ID in the argument."""
        self.members.discard(github_user_id)

    def is_member(self, github_user_id):
        """Identify if any member has the ID specified in the argument."""
        return github_user_id in self.members

    def __str__(self):
        """Print information on the team class."""
        return str(self.__dict__)
