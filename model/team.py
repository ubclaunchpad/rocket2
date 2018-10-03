"""Data model to represent a team."""
import uuid


class Team:
    """Represent a team with related fields and methods."""

    __team_id = 0
    __display_name = ""
    __platform = ""
    __members = set()
    __github_team_name = ""

    def __init__(self, display_name):
        self.__team_id = uuid.uuid4()
        self.__display_name = display_name

    def get_team_id(self):
        return self.__team_id

    def set_display_name(self, display_name):
        self.__display_name = display_name

    def get_display_name(self):
        return self.__display_name

    def set_platform(self, platform):
        self.__platform = platform

    def get_platform(self):
        return self.__platform

    def add_member(self, uuid):
        self.__members.add(uuid)

    def discard_member(self, uuid):
        self.__members.discard(uuid)

    def get_members(self):
        return self.__members

    def is_member(self, uuid):
        return uuid in self.__members

    def set_github_team_name(self, github_team_name):
        self.__github_team_name = github_team_name

    def get_github_team_name(self):
        return self.__github_team_name
