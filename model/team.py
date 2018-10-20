"""Represent a data model for a team."""


class Team:
    """Represent a team with related fields and methods."""

    def __init__(self, display_name):
        """Initialize the team with a Github team name and given name."""
        self.__github_team_name = self.generate_github_team_name(display_name)
        self.__display_name = display_name
        self.__platform = ""
        self.__members = set()

    @staticmethod
    def generate_github_team_name(display_name):
        """Generate a unique Github team name based on given display name."""
        # stub
        return ""

    def get_github_team_name(self):
        """Return this team's unique Github team name."""
        return self.__github_team_name

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

    def add_member(self, uuid):
        """Add a new member's unique ID to the team's set of members' IDs."""
        self.__members.add(uuid)

    def discard_member(self, uuid):
        """Discard the member of the team with the ID in the argument."""
        self.__members.discard(uuid)

    def get_members(self):
        """Return the set of all members' unique IDs."""
        return self.__members

    def is_member(self, uuid):
        """Identify if any member has the ID specified in the argument."""
        return uuid in self.__members
