"""Data model to represent a team."""
class Team:
    __display_name = ""
    __platform = ""
    __members = set()
    __github_team_name = ""

    def __init__(self, display_name):
        self.__display_name = display_name

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

    def set_github_team_name(self, github_team_name):
        self.__github_team_name = github_team_name

    def get_github_team_name(self):
        return self.__github_team_name
