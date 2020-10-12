"""Match two Launchpad member for a private conversation"""
from slack import WebClient
from interface.slack import Bot
from random import shuffle
from .base import ModuleBase
from typing import Dict, List, Tuple, Any
from flask import Flask
from config import Config
from db.facade import DBFacade
import logging


class Pairing(ModuleBase):
    """Module that matches 2 launchpad members each week"""

    NAME = 'Match launch pad members randomly'

    def __init__(self,
                 flask_app: Flask,
                 config: Config,
                 facade: DBFacade):
        """Initialize the object."""
        self.bot = Bot(WebClient(config.slack_api_token),
                       config.slack_notification_channel)
        self.channel_id = self.bot.get_channel_id(config.slack_pairing_channel)
        self.facade = facade


    def get_job_args(self) -> Dict[str, Any]:
        """Get job configuration arguments for apscheduler."""
        return {'trigger':      'cron',
                'minute': '*',
                'name':         self.NAME}

    def do_it(self):
        """Pair users together, and create a private chat for them"""
        users = self.bot.get_channel_users(self.channel_id)
        logging.debug(f"users of the pairing channel are {users}")
        matched_user_pairs = self.__pair_users(users)
        for pair in matched_user_pairs:
            group_name = self.bot.create_private_chat(pair)
            logging.info(f"The name of the created group name is {group_name}")
            self.bot.send_to_channel("Hello! You have been matched by Rocket. " +
            "please use this channel to get to know each other!", group_name)

    def __pair_users(self, users: List[str]) -> List[List[str]]:
        """
        Creates pairs of users that haven't been matched before
        """
        shuffle(users)
        pairs = []
        pair = []
        for i, user in enumerate(users):
            pair.append(user)
            if i % 2 != 0:
                pairs.append(pair)
                pair = []
        # If we have an odd number of people that is not 1
        # We put the odd person out in one of the groups
        # So we might have a group of 3
        if len(pair) == 1 and len(pairs) > 0:
            pairs[len(pairs) - 1].append(pair[0])
        return pairs
