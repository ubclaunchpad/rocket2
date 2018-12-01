"""Calls the appropriate handler depending on the event data."""
from command.commands.user import UserCommand
from model.user import User
from bot.bot import SlackAPIError
import logging


class Core:
    """Encapsulate methods for handling events."""

    def __init__(self, db_facade, bot):
        """Initialize the dictionary of command handlers."""
        self.__commands = {}
        self.__facade = db_facade
        self.__bot = bot
        self.__commands["user"] = UserCommand(self.__facade, self.__bot)

    def handle_app_mention(self, event_data):
        """Handle the events associated with mentions of @rocket."""
        message = event_data["event"]["text"]
        user = event_data["event"]["user"]
        channel = event_data["event"]["channel"]
        s = message.split(' ', 2)
        command_type = s[1]
        logging.info('{}:{}'.format(user, message))
        command = command_type + ' ' + s[2]
        try:
            self.__commands[command_type].handle(command, user, channel)
            return 1
        except KeyError:
            return -1

    def handle_member_join(self, event_data):
        """Handle the event of a new user joining the workspace."""
        new_user_id = event_data["event"]["user"]["id"]
        new_user = User(new_user_id)
        self.__facade.store_user(new_user)
        welcome = 'Welcome to Lauchpad!'
        try:
            self.__bot.send_dm(welcome, new_user_id)
            return True
        except SlackAPIError:
            return False
