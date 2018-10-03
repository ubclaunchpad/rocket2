"""Data model to represent an individual user."""
from permissions import Permissions


class User:
    __slack_id = ""
    __name = ""
    __email = ""
    __github_username = ""
    __major = ""
    __position = ""
    __biography = ""
    __image_url = ""
    __permissions_level = Permissions.member

    def __init__(self, slack_id):
        self.__slack_id = slack_id

    def get_slack_id(self):
        return self.__slack_id

    def set_email(self, email):
        self.__email = email

    def get_email(self):
        return self.__email

    def set_github_username(self, github_username):
        self.__github_username = github_username

    def get_github_username(self):
        return self.__github_username

    def set_major(self, major):
        self.__major = major

    def get_major(self):
        return self.__major

    def set_position(self, position):
        self.__position = position

    def get_position(self):
        return self.__position

    def set_biography(self, biography):
        self.__biography = biography

    def get_biography(self):
        return self.__biography

    def set_image_url(self, image_url):
        self.__image_url = image_url

    def get_image_url(self):
        return self.__image_url

    def set_permissions_level(self, permissions_level):
        self.__permissions_level = permissions_level

    def get_permissions_level(self):
        return self.__permissions_level
