"""All necessary class initializations."""
from db.facade import DBFacade
from db.dynamodb import DynamoDB
from command.core import Core
from slackclient import SlackClient
from interface.slack import Bot
import toml

import logging


def make_core(config):
    """
    Initialize and returns a :class:`command.core.Core` object.

    :return: a new ``Core`` object, freshly initialized
    """
    if not config['testing']:
        slack_api_token = toml.load(config['slack']['creds_path'])['api_token']
    else:
        slack_api_token = ""
    facade = DBFacade(DynamoDB(config))
    bot = Bot(SlackClient(slack_api_token))
    return Core(facade, bot)
