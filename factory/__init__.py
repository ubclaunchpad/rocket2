"""All necessary class initializations."""
import toml
import os

from command.core import Core
from command.commands.token import TokenCommandConfig
from datetime import timedelta
from db.facade import DBFacade
from db.dynamodb import DynamoDB
from github import Github
from interface.github import GithubInterface
from interface.slack import Bot
from slackclient import SlackClient
from webhook.webhook import WebhookHandler


def make_core(config, gh=None):
    """
    Initialize and returns a :class:`command.core.Core` object.

    :return: a new ``Core`` object, freshly initialized
    """
    slack_api_token = ""
    github_api_token, github_organization = "", ""
    signing_key = ""
    if not config['testing']:
        slack_api_token = toml.load(
            config['slack']['creds_path'])['api_token']
        github_api_token = toml.load(
            config['github']['creds_path'])['api_token']
        github_organization = config['github']['organization']
        gh = GithubInterface(Github(github_api_token), github_organization)
        if os.path.isfile(config['auth']['signing_key_path']):
            signing_key = open(config['auth']['signing_key_path']).read()
        else:
            signing_key = os.urandom(24).decode('utf-8')
            open(config['auth']['signing_key_path']).write(signing_key)
    facade = DBFacade(DynamoDB(config))
    bot = Bot(SlackClient(slack_api_token))
    # TODO: make token config expiry configurable
    token_config = TokenCommandConfig(timedelta(days=7), signing_key)
    return Core(facade, bot, gh, token_config)


def make_webhook_handler(config):
    """
    Initialize and returns a :class:`webhook.webhook.WebhookHandler` object.

    :return: a new ``WebhookHandler`` object, freshly initialized
    """
    facade = DBFacade(DynamoDB(config))
    return WebhookHandler(facade)
