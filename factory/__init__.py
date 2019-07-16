"""All necessary class initializations."""
import os
import pem
import random
import string

from app.controller.command import CommandParser
from app.controller.command.commands.token import TokenCommandConfig
from datetime import timedelta
from db import DBFacade
from db.dynamodb import DynamoDB
from interface.github import GithubInterface, DefaultGithubFactory
from interface.slack import Bot
from slack import WebClient
from app.controller.webhook.github import GitHubWebhookHandler
from app.controller.webhook.slack import SlackEventsHandler
from config import Credentials

from typing import Dict, Any, Optional, cast


def make_command_parser(config: Dict[str, Any],
                        credentials: Credentials,
                        gh: Optional[GithubInterface] = None) \
        -> CommandParser:
    """
    Initialize and returns a :class:`CommandParser` object.

    :return: a new ``CommandParser`` object, freshly initialized
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
    facade = DBFacade(DynamoDB(config, credentials))
    bot = Bot(WebClient(slack_api_token), slack_bot_channel)
    # TODO: make token config expiry configurable
    token_config = TokenCommandConfig(timedelta(days=7), signing_key)
    return CommandParser(facade, bot, cast(GithubInterface, gh), token_config)


def make_github_webhook_handler(config: Dict[str, Any],
                                credentials:
                                Credentials) -> GitHubWebhookHandler:
    """
    Initialize a :class:`GitHubWebhookHandler` object.

    :return: a new ``GitHubWebhookHandler`` object, freshly initialized
    """
    facade = DBFacade(DynamoDB(config, credentials))
    return GitHubWebhookHandler(facade, credentials)


def make_slack_events_handler(config: Dict[str, Any],
                              credentials:
                              Credentials) -> SlackEventsHandler:
    """
    Initialize a :class:`SlackEventsHandler` object.

    :return: a new ``SlackEventsHandler`` object, freshly initialized
    """
    slack_api_token, slack_bot_channel = "", ""
    if not config['testing']:
        slack_api_token = credentials.slack_api_token
        slack_bot_channel = config['slack']['bot_channel']
    facade = DBFacade(DynamoDB(config, credentials))
    bot = Bot(WebClient(slack_api_token), slack_bot_channel)
    return SlackEventsHandler(facade, bot)


def create_signing_token() -> str:
    """Create a new, random signing token."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(24))
