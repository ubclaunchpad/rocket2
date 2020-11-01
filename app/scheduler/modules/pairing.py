"""Match two Launch Pad member for a private conversation"""
from slack import WebClient
from interface.slack import Bot
from random import shuffle
from .base import ModuleBase
from typing import Dict, List, Any, Set
from flask import Flask
from config import Config
from db.facade import DBFacade
from app.model import Pairing
import logging


class PairingSchedule(ModuleBase):
    """Module that pairs members each ``SLACK_PAIRING_FREQUENCY``"""

    NAME = 'Pair members randomly for meetups'

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
            self.bot.send_to_channel("Hello! \
                You have been matched by Rocket \
                please use this channel to get to know each other!",
                                     group_name)

    def __pair_users(self, users: List[str]) -> List[List[str]]:
        """
        Creates pairs of users that haven't been matched before

        :param users: A list of slack ids of all users to match

        If a pairing cannot be done, then the history of pairings is
        purged, and the algorithm is run again.
        """
        # TODO: Clean this up into a more concrete algorithm
        logging.info("Running pairing algorithm")
        shuffle(users)
        already_added = set()
        pairs = []
        for i, user in enumerate(users):
            if user in already_added:
                continue
            previously_paired = self.__get_previous_pairs(user)
            for j in range(i + 1, len(users)):
                other_user = users[j]
                if other_user not in previously_paired and \
                   other_user not in already_added:
                    self.__persist_pairing(user, other_user)
                    pairs.append([user, other_user])
                    already_added.add(user)
                    already_added.add(other_user)
                    break
        not_paired = list(
            filter(lambda user: user not in already_added, users))
        # If we have an odd number of people that is not 1
        # We put the odd person out in one of the groups
        # So we might have a group of 3
        if len(not_paired) == 1 and len(pairs) > 0:
            pairs[len(pairs) - 1].append(not_paired[0])
        # In the case the algorithm failed, purge pairings and repeat
        elif len(not_paired) > 1:
            logging.info("Failed to pair users, purging and trying again..")
            self.__purge_pairings()
            return self.__pair_users(users)
        logging.info("Done pairing algorithm")
        return pairs

    def __get_previous_pairs(self, user: str) -> Set[str]:
        logging.info(f"Getting previous pairs for {user}")
        pairings = self.facade.query_or(Pairing,
                                        [('user1_slack_id', user),
                                         ('user2_slack_id', user)])
        res = set()
        for pairing in pairings:
            other = pairing.user1_slack_id if pairing.user2_slack_id == user \
                                           else pairing.user2_slack_id
            res.add(other)
        logging.info(f"Previous pairings are {res}")
        return res

    def __persist_pairing(self, user1_slack_id: str, user2_slack_id: str):
        pairing = Pairing(user1_slack_id, user2_slack_id)
        reverse_pairing = Pairing(user2_slack_id, user1_slack_id)
        self.facade.store(pairing)
        self.facade.store(reverse_pairing)

    def __purge_pairings(self):
        logging.info("Deleting all pairings")
        self.facade.delete_all(Pairing)
