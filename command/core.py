"""Calls the appropriate handler depending on the event data."""
from command.commands.user import UserCommand
from model.user import User
from interface.slack import SlackAPIError
import logging
import json


class Core:
    """Encapsulate methods for handling events."""

    def __init__(self, db_facade, bot, gh_interface):
        """Initialize the dictionary of command handlers."""
        self.__commands = {}
        self.__facade = db_facade
        self.__bot = bot
        self.__github = gh_interface
        self.__commands["user"] = UserCommand(self.__facade, self.__github)

    def handle_app_command(self, cmd_txt, user):
        """Handle a command call to rocket."""
        def regularize_char(c):
            if c == "‘" or c == "’":
                return "'"
            if c == '“' or c == '”':
                return '"'
            return c

        # Slightly hacky way to deal with Apple platform
        # smart punctuation messing with argparse.
        cmd_txt = ''.join(map(regularize_char, cmd_txt))
        s = cmd_txt.split(' ', 1)
        if s[0] == "help" or s[0] is None:
            logging.info("Help command was called")
            return self.get_help(), 200
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
        welcome = 'Welcome to UBC Launch Pad!'
        try:
            self.__bot.send_dm(welcome, new_id)
            logging.info(new_id + " added to database - user notified")
        except SlackAPIError:
            logging.error(new_id + " added to database - user not notified")

    def get_help(self):
        """Get help messages and return a formatted string for messaging."""
        message = {"text": "Displaying all available commands. To read about"
                           " a specific command, use `/rocket COMMAND help`\n",
                   "mrkdwn": "true"}
        attachments = []
        for cmd in self.__commands:
            cmd_name = self.__commands[cmd].get_name()
            cmd_text = "*[" + cmd_name.upper() + "]*\n\n" + \
                "Commands for editing", cmd_name + "s."
            # use below when cmd_usage is fixed in #202
            # cmd_usage = self.__commands[cmd].get_help()
            # cmd_text = "*[" + cmd_name + "]*\n\n" + \
            #           "```" + cmd_usage + "```"
            # perhaps get_help could have a parameter to only return usage?
            attachment = {"text": cmd_text, "mrkdwn_in": ["text"]}
            attachments.append(attachment)
        message["attachments"] = attachments
        return json.dumps(message)
