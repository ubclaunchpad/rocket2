# data model for a slack team
class Team:
    __display_name = ""
    __platform = ""
    __member_list = []
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
        self.__member_list.append(uuid)

    def remove_member(self, uuid):
        if self.__member_list.__contains__(uuid):
            self.__member_list.remove(uuid)

    def get_members(self):
        return self.__member_list

    def set_github_team_name(self, github_team_name):
        self.__github_team_name = github_team_name

    def get_github_team_name(self):
        return self.__github_team_name
