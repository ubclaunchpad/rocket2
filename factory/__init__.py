"""All necessary class initializations."""
import os
import pem
import random
import string
import toml

from command.core import Core
from command.commands.token import TokenCommandConfig
from datetime import timedelta
from db.facade import DBFacade
from db.dynamodb import DynamoDB
from interface.github import GithubInterface, DefaultGithubFactory
from interface.slack import Bot
from slackclient import SlackClient
from webhook.webhook import WebhookHandler


def make_core(config, credentials, gh=None):
    """
    Initialize and returns a :class:`command.core.Core` object.

    :return: a new ``Core`` object, freshly initialized
    """
    slack_api_token, slack_bot_channel = "", ""
    signing_key = ""
    if not config['testing']:
        slack_api_token = credentials.slack_api_token
        github_auth_key = pem.parse_file(
            credentials.github_signing_key_path)[0].as_text()
        github_app_id = config['github']['app_id']
        github_organization = config['github']['organization']
        slack_bot_channel = config['slack']['bot_channel']
        gh = GithubInterface(DefaultGithubFactory(github_app_id,
                                                  github_auth_key),
                             github_organization)
        if os.path.isfile(config['auth']['signing_key_path']):
            signing_key = open(config['auth']['signing_key_path']).read()
        else:
            signing_key = create_signing_token()
            open(config['auth']['signing_key_path'], 'w+').write(signing_key)
    facade = DBFacade(DynamoDB(config))
    bot = Bot(SlackClient(slack_api_token), slack_bot_channel)
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


def create_signing_token():
    """Create a new, random signing token."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(24))
