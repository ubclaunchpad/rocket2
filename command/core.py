"""Calls the appropriate handler depending on the event data."""
from command.commands.user import UserCommand
from model.user import User
from interface.slack import SlackAPIError
import logging


class Core:
    """Encapsulate methods for handling events."""

    def __init__(self, db_facade, bot):
        """Initialize the dictionary of command handlers."""
        self.__commands = {}
        self.__facade = db_facade
        self.__bot = bot
        self.__commands["user"] = UserCommand(self.__facade)

    def handle_app_command(self, cmd_txt, user):
        """Handle a command call to rocket."""
        s = cmd_txt.split(' ', 1)
        if s[0] in self.__commands:
            return self.__commands[s[0]].handle(cmd_txt, user)
        else:
            logging.error("app command triggered incorrectly")
            return 'Please enter a valid command', 200

    def handle_team_join(self, event_data):
        """Handle the event of a new user joining the workspace."""
        new_id = event_data["event"]["user"]["id"]
        new_user = User(new_id)
        self.__facade.store_user(new_user)
        welcome = 'Welcome to Launchpad!'
        try:
            self.__bot.send_dm(welcome, new_id)
            logging.info(new_id + " added to database - user notified")
        except SlackAPIError:
            logging.error(new_id + " added to database - user not notified")
