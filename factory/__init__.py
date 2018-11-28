"""All necessary class initializations."""
from db.facade import DBFacade
from db.dynamodb import DynamoDB
from command.core import Core
from slackclient import SlackClient
import os


def make_core():
    """
    Initialize and returns a :class:`command.core.Core` object.

    Requires that environmental variable ``SLACK_API_TOKEN`` to be set. Please
    set it to be the slack API token.

    :return: a new ``Core`` object, freshly initialized
    """
    slack_token = os.environ['SLACK_API_TOKEN']
    facade = DBFacade(DynamoDB())
    slack_client = SlackClient(slack_token)
    return Core(facade, slack_client)
