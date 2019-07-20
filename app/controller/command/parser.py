"""Handle Rocket 2 commands."""
from app.controller import ResponseTuple
from app.controller.command.commands import UnionCommands, \
    UserCommand, TeamCommand, TokenCommand, KarmaCommand, MentionCommand
from app.controller.command.commands.token import TokenCommandConfig
from db.facade import DBFacade
from flask import jsonify, Response
from interface.slack import Bot
from interface.github import GithubInterface
from typing import Dict, cast
import utils.slack_parse as util
import logging
import re
from utils.slack_msg_fmt import wrap_slack_code


class CommandParser:
    """Manage the different command parsers for Rocket 2 commands."""

    def __init__(self,
                 db_facade: DBFacade,
                 bot: Bot,
                 gh_interface: GithubInterface,
                 token_config: TokenCommandConfig) -> None:
        """Initialize the dictionary of command handlers."""
        self.__commands: Dict[str, UnionCommands] = {}
        self.__facade = db_facade
        self.__bot = bot
        self.__github = gh_interface
        self.__commands["user"] = UserCommand(self.__facade, self.__github)
        self.__commands["team"] = TeamCommand(self.__facade,
                                              self.__github, self.__bot)
        self.__commands["token"] = TokenCommand(self.__facade, token_config)
        self.__commands["karma"] = KarmaCommand(self.__facade)
        self.__commands["mention"] = MentionCommand(self.__facade)

    def handle_app_command(self,
                           cmd_txt: str,
                           user: str) -> ResponseTuple:
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
        elif re.match("^[UW][A-Z0-9]{8}$", s[0]):
            logging.info("mention command activated")
            return self.__commands["mention"].handle(cmd_txt, user)
        else:
            logging.error("app command triggered incorrectly")
            return 'Please enter a valid command', 200

    def get_help(self) -> Response:
        """
        Get help messages and return a formatted string for messaging.

        :return: Preformatted ``flask.Response`` object containing help
                 messages
        """
        message = {"text": "Displaying all available commands. "
                           "To read about a specific command, use "
                           f"\n{wrap_slack_code('/rocket [command] help')}\n"
                           "For arguments containing spaces, "
                           "please enclose them with quotations.\n",
                   "mrkdwn": "true"}
        attachments = []
        for cmd in self.__commands.values():
            cmd_name = cmd.command_name
            cmd_text = f"*{cmd_name}:* {cmd.desc}"
            attachment = {"text": cmd_text, "mrkdwn_in": ["text"]}
            attachments.append(attachment)
        message["attachments"] = attachments  # type: ignore
        return cast(Response, jsonify(message))
