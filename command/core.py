"""Calls the appropriate handler depending on the event data."""
from command.commands.user import UserCommand
from command.commands.token import TokenCommand
import command.util as util
from model.user import User
from interface.slack import SlackAPIError
import logging
from flask import jsonify


class Core:
    """Encapsulate methods for handling events."""

    def __init__(self, db_facade, bot, gh_interface, token_config):
        """Initialize the dictionary of command handlers."""
        self.__commands = {}
        self.__facade = db_facade
        self.__bot = bot
        self.__github = gh_interface
        self.__commands["user"] = UserCommand(self.__facade, self.__github)
        self.__commands["token"] = TokenCommand(self.__facade, token_config)

    def handle_app_command(self, cmd_txt, user):
        """
        Handle a command call to rocket.

        :param cmd_txt: the command itself
        :param user: slack ID of user who executed the command
        :return: tuple where first element is the response text (or a
                 ``flask.Response`` object), and the second element
                 is the response status code
        """
        # Slightly hacky way to deal with Apple platform
        # smart punctuation messing with argparse.
        cmd_txt = ''.join(map(util.regularize_char, cmd_txt))
        cmd_txt = util.escaped_id_to_id(cmd_txt)
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
        """
        Handle the event of a new user joining the workspace.

        :param event_data: JSON event data
        """
        new_id = event_data["event"]["user"]["id"]
        new_user = User(new_id)
        self.__facade.store(new_user)
        welcome = 'Welcome to UBC Launch Pad!'
        try:
            self.__bot.send_dm(welcome, new_id)
            logging.info(new_id + " added to database - user notified")
        except SlackAPIError:
            logging.error(new_id + " added to database - user not notified")

    def send_event_notif(self, msg):
        """
        For use in getting bot to report events in designated slack channel.

        :param msg: message to send to slack bot channel
        """
        self.__bot.send_event_notif(msg)
        logging.info("Core passing notification to bot")

    def get_help(self):
        """
        Get help messages and return a formatted string for messaging.

        :return: Preformatted ``flask.Response`` object containing help
                 messages
        """
        message = {"text": "Displaying all available commands. "
                           "To read about a specific command, use "
                           "\n`/rocket [command] help`\n"
                           "For arguments containing spaces, "
                           "please enclose them with quotations.\n",
                   "mrkdwn": "true"}
        attachments = []
        for cmd in self.__commands.values():
            cmd_name = cmd.command_name
            cmd_text = "*" + cmd_name + ":* " + cmd.desc
            attachment = {"text": cmd_text, "mrkdwn_in": ["text"]}
            attachments.append(attachment)
        message["attachments"] = attachments
        return jsonify(message)
