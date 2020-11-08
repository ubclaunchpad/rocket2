"""Handle Rocket 2 commands."""
from app.controller import ResponseTuple
from app.controller.command.commands import UserCommand, TeamCommand,\
    ExportCommand, TokenCommand, ProjectCommand, KarmaCommand,\
    MentionCommand, IQuitCommand
from app.controller.command.commands.base import Command
from app.controller.command.commands.token import TokenCommandConfig
from db.facade import DBFacade
from interface.slack import Bot
from interface.github import GithubInterface
from interface.gcp import GCPInterface
from interface.cloudwatch_metrics import CWMetrics
from typing import Dict, Any, Optional
import utils.slack_parse as util
import logging
import time
from utils.slack_msg_fmt import wrap_slack_code
from utils.slack_parse import is_slack_id
from config import Config
import requests


class CommandParser:
    """Manage the different command parsers for Rocket 2 commands."""

    def __init__(self,
                 config: Config,
                 db_facade: DBFacade,
                 bot: Bot,
                 gh_interface: GithubInterface,
                 token_config: TokenCommandConfig,
                 metrics: CWMetrics,
                 gcp: Optional[GCPInterface] = None):
        """Initialize the dictionary of command handlers."""
        self.commands: Dict[str, Command] = {}
        self.__facade = db_facade
        self.__bot = bot
        self.__github = gh_interface
        self.__gcp = gcp
        self.__metrics = metrics
        self.commands["user"] = UserCommand(self.__facade,
                                            self.__github,
                                            self.__gcp)
        self.commands["team"] = TeamCommand(config, self.__facade,
                                            self.__github,
                                            self.__bot,
                                            gcp=self.__gcp)
        self.commands["export"] = ExportCommand(self.__facade,
                                                self.__bot)
        self.commands["token"] = TokenCommand(self.__facade, token_config)
        self.commands["project"] = ProjectCommand(self.__facade)
        self.commands["karma"] = KarmaCommand(self.__facade)
        self.commands["mention"] = MentionCommand(self.__facade)
        self.commands["i-quit"] = IQuitCommand(self.__facade)

        # Disable project commands (delete when we enable it again)
        del self.commands['project']

    def handle_app_command(self,
                           cmd_txt: str,
                           user: str,
                           response_url: str):
        """
        Handle a command call to rocket.

        :param cmd_txt: the command itself
        :param user: slack ID of user who executed the command
        :return: tuple where first element is the response text (or a
                 ``flask.Response`` object), and the second element
                 is the response status code
        """
        start_time_ms = time.time() * 1000

        # Slightly hacky way to deal with Apple platform
        # smart punctuation messing with argparse.
        cmd_txt = ''.join(map(util.regularize_char, cmd_txt))
        cmd_txt = util.escaped_id_to_id(cmd_txt)
        cmd_txt = util.ios_dash(cmd_txt)
        s = cmd_txt.split(' ', 1)
        cmd_name = 'help'
        if s[0] == 'help' or s[0] is None:
            logging.info('Help command was called')
            v = self.get_help()
        elif s[0] in self.commands:
            v = self.commands[s[0]].handle(cmd_txt, user)

            # Hack to only grab first 2 command/subcommand pair
            s = cmd_txt.split(' ')
            if len(s) == 2 and s[1].startswith('-'):
                cmd_name = s[0]
            else:
                cmd_name = ' '.join(s[0:2])
        elif is_slack_id(s[0]):
            logging.info('mention command activated')
            v = self.commands['mention'].handle(cmd_txt, user)
            cmd_name = 'mention'
        else:
            logging.error("app command triggered incorrectly")
            v = self.get_help()
        if isinstance(v[0], str):
            response_data: Any = {'text': v[0]}
        else:
            response_data = v[0]

        # Submit metrics
        duration_taken_ms = time.time() * 1000 - start_time_ms
        self.__metrics.submit_cmd_mstime(cmd_name, duration_taken_ms)

        if response_url != "":
            requests.post(url=response_url, json=response_data)
        else:
            return v

    def get_help(self) -> ResponseTuple:
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
        for cmd in self.commands.values():
            cmd_name = cmd.command_name
            cmd_text = f"*{cmd_name}:* {cmd.desc}"
            attachment = {"text": cmd_text, "mrkdwn_in": ["text"]}
            attachments.append(attachment)
        message["attachments"] = attachments  # type: ignore
        return message, 200
