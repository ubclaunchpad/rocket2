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

    def msg_split(self, msg):
        """
        Split a message into 3 components.

        The 3 components, in order, are:

        - Mentioned bot slack ID
        - Module of command
        - Submodule and the rest of command

        So the string ``<@ABC123> user view`` will be parsed into

        .. code-block:: python

            ['<@ABC123>', 'user', 'view']

        And the string ``<@ABC123> user view @me`` will be parsed into

        .. code-block:: python

            ['<@ABC123>', 'user', 'view @me']

        :return: A list of 3 strings
        """
        return msg.split(' ', 2)

    def handle_app_mention(self, event_data):
        """Handle the events associated with mentions of @rocket."""
        message = event_data["event"]["text"]
        user = event_data["event"]["user"]
        channel = event_data["event"]["channel"]

        s = self.msg_split(message)
        if s[0] != "@rocket":
            logging.error("app mention event triggered incorrectly")
        else:
            command_type = s[1]
            command = command_type + ' ' + s[2]
            try:
                self.__commands[command_type].handle(command, user, channel)
                logging.info(("@rocket mention - "
                              "successfully handled request: ") + message)
            except KeyError:
                error_dm = "Please enter a valid command."
                self.__bot.send_dm(error_dm, user)
                logging.info("@rocket mention - invalid request: " + message)

    def handle_team_join(self, event_data):
        """Handle the event of a new user joining the workspace."""
        new_id = event_data["event"]["user"]["id"]
        new_user = User(new_id)
        self.__facade.store_user(new_user)
        welcome = 'Welcome to Lauchpad!'
        try:
            self.__bot.send_dm(welcome, new_id)
            logging.info(new_id + " added to database - user notified")
        except SlackAPIError:
            logging.error(new_id + " added to database - user not notified")
