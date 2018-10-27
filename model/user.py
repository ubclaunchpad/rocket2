"""Data model to represent an individual user."""
from model.permissions import Permissions


class User:
    """Represent a user with related fields and methods."""

    def __init__(self, slack_id):
        """Initialize the user with a given Slack ID."""
        self.__slack_id = slack_id
        self.__name = ""
        self.__email = ""
        self.__github_username = ""
        self.__major = ""
        self.__position = ""
        self.__biography = ""
        self.__image_url = ""
        self.__permissions_level = Permissions.member

    def get_slack_id(self):
        """Return this user's Slack ID."""
        return self.__slack_id

    def get_email(self):
        """Return this user's email."""
        return self.__email

    def set_email(self, email):
        """Set this user's email to the given argument."""
        self.__email = email

    def get_github_username(self):
        """Return this user's Github username."""
        return self.__github_username

    def set_github_username(self, github_username):
        """Set this user's Github username to the given argument."""
        self.__github_username = github_username

    def get_major(self):
        """Return this user's major."""
        return self.__major

    def set_major(self, major):
        """Set this user's major to the given argument."""
        self.__major = major

    def get_position(self):
        """Return this user's position."""
        return self.__position

    def set_position(self, position):
        """Set this user's position to the given argument."""
        self.__position = position

    def get_biography(self):
        """Return this user's biography."""
        return self.__biography

    def set_biography(self, biography):
        """Set this user's biography to the given argument."""
        self.__biography = biography

    def get_image_url(self):
        """Return this user's image URL."""
        return self.__image_url

    def set_image_url(self, image_url):
        """Set this user's image URL to the given argument."""
        self.__image_url = image_url

    def get_permissions_level(self):
        """Return this user's permissions level."""
        return self.__permissions_level

    def set_permissions_level(self, permissions_level):
        """Set this user's permissions level to the given argument."""
        self.__permissions_level = permissions_level

    def __str__(self):
        """Prints information on the user class."""
        return "User, slack_id: {}, name: {}, email: {}, github: {}," \
               " major: {}, position: {}, bio: {}, image_url: {}," \
               " permission level: {}".format(
                self.__slack_id, self.__name, self.__email,
                self.__github_username, self.__major,
                self.__position, self.__biography, self.__image_url,
                self.__permissions_level)
