"""Represent a data model for a team."""


class Team:
    """Represent a team with related fields and methods."""

    def __init__(self, gh_team_id, gh_team_name, display_name):
        """
        Initialize the team.

        Parameters are a valid Github team ID, team name and display name.
        """
        self.__gh_team_id = gh_team_id
        self.__gh_team_name = gh_team_name
        self.__display_name = display_name
        self.__platform = ""
        self.__members = set()

    @staticmethod
    def is_valid(team):
        """
        Return true if this team has no missing required fields.

        Required fields for database to accept:
        - ``__gh_team_name``
        - ``__gh_team_id``

        :param team: team to check
        :return: returns true if this team has no missing required fields
        """
        return len(team.get_gh_team_name()) > 0 and\
            len(team.get_gh_team_id()) > 0

    def __eq__(self, other):
        """Return true if this team has the same attributes as the other."""
        return str(self.__dict__) == str(other.__dict__)

    def __ne__(self, other):
        """Return the opposite of what is returned in self.__eq__(other)."""
        return not (self == other)

    def get_gh_team_id(self):
        """Return this team's unique Github team ID."""
        return self.__gh_team_id

    def set_gh_team_id(self, gh_team_id):
        """Set this team's unique Github team ID."""
        self.__gh_team_id = gh_team_id

    def get_gh_team_name(self):
        """Return this team's unique Github team name."""
        return self.__gh_team_name

    def set_display_name(self, display_name):
        """Set this team's display name to the given argument."""
        self.__display_name = display_name

    def get_display_name(self):
        """Return this team's display name."""
        return self.__display_name

    def set_platform(self, platform):
        """Set this team's working platform to the given argument."""
        self.__platform = platform

    def get_platform(self):
        """Return this team's working platform."""
        return self.__platform

    def add_member(self, gh_user_id):
        """Add a new member's Github ID to the team's set of members' IDs."""
        self.__members.add(gh_user_id)

    def discard_member(self, gh_user_id):
        """Discard the member of the team with Github ID in the argument."""
        self.__members.discard(gh_user_id)

    def get_members(self):
        """Return the set of all members' Github IDs."""
        return self.__members

    def is_member(self, gh_user_id):
        """Identify if any member has the ID specified in the argument."""
        return gh_user_id in self.__members

    def __str__(self):
        """Print information on the team class."""
        return str(self.__dict__)
