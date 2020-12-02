"""Handle Rocket 2 commands."""
from app.controller import ResponseTuple
from app.controller.command.commands import UserCommand, TeamCommand,\
    ExportCommand, TokenCommand, KarmaCommand,\
    MentionCommand, IQuitCommand
from app.controller.command.commands.base import Command
from app.controller.command.commands.token import TokenCommandConfig
from db.facade import DBFacade
from interface.slack import Bot
from interface.github import GithubInterface
from interface.gcp import GCPInterface
from interface.cloudwatch_metrics import CWMetrics
from typing import Dict, Optional
import utils.slack_parse as util
import logging
import time
from utils.slack_msg_fmt import wrap_slack_code
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
        self.commands["export"] = ExportCommand(self.__facade)
        self.commands["token"] = TokenCommand(self.__facade, token_config)
        self.commands["karma"] = KarmaCommand(self.__facade)
        self.commands["mention"] = MentionCommand(self.__facade)
        self.commands["i-quit"] = IQuitCommand(self.__facade)

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
            resp, _ = self.get_help()
        elif s[0] in self.commands:
            resp, _ = self.commands[s[0]].handle(cmd_txt, user)

            # Hack to only grab first 2 command/subcommand pair
            s = cmd_txt.split(' ')
            if len(s) == 2 and s[1].startswith('-'):
                cmd_name = s[0]
            else:
                cmd_name = ' '.join(s[0:2])
        elif util.is_slack_id(s[0]):
            logging.info('mention command activated')
            resp, _ = self.commands['mention'].handle(cmd_txt, user)
            cmd_name = 'mention'
        else:
            logging.error("app command triggered incorrectly")
            resp, _ = self.get_help()

        if isinstance(resp, str):
            # Wrap response if response is just some text
            resp = {'text': resp}

        # Submit metrics
        duration_taken_ms = time.time() * 1000 - start_time_ms
        self.__metrics.submit_cmd_mstime(cmd_name, duration_taken_ms)

        if response_url != "":
            requests.post(url=response_url, json=resp)
        else:
            return resp, 200

    def get_help(self) -> ResponseTuple:
        """
        Get help messages and return a formatted string for messaging.

        :return: Preformatted ``flask.Response`` object containing help
                 messages
        """
        wrapped = wrap_slack_code('/rocket [command] -h')
        message = f'''Displaying all available commands.
To read about a specific command, use {wrapped}.
For arguments containing spaces, please enclose them with quotations.'''
        for cmd in self.commands.values():
            cmd_name = cmd.command_name
            message += f"\n> *{cmd_name}:* {cmd.desc}"
        return message, 200
