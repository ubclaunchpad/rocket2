"""All necessary class initializations."""
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
from config import Config


def make_github_interface(config: Config) -> GithubInterface:
    """
    Initialize and return a :class:`GithubInterface` object.

    :return: a new ``GithubInterface`` object, freshly initialized
    """
    return GithubInterface(DefaultGithubFactory(config.github_app_id,
                                                config.github_key),
                           config.github_org_name)


def make_command_parser(config: Config, gh: GithubInterface) \
        -> CommandParser:
    """
    Initialize and returns a :class:`CommandParser` object.

    :return: a new ``CommandParser`` object, freshly initialized
    """
    facade = DBFacade(DynamoDB(config))
    bot = Bot(WebClient(config.slack_api_token),
              config.slack_notification_channel)
    # TODO: make token config expiry configurable
    token_config = TokenCommandConfig(timedelta(days=7), config.github_key)
    return CommandParser(config, facade, bot, gh, token_config)


def make_github_webhook_handler(gh: GithubInterface,
                                config: Config) -> GitHubWebhookHandler:
    """
    Initialize a :class:`GitHubWebhookHandler` object.

    :return: a new ``GitHubWebhookHandler`` object, freshly initialized
    """
    facade = DBFacade(DynamoDB(config))
    return GitHubWebhookHandler(facade, gh, config)


def make_slack_events_handler(config: Config) -> SlackEventsHandler:
    """
    Initialize a :class:`SlackEventsHandler` object.

    :return: a new ``SlackEventsHandler`` object, freshly initialized
    """
    facade = DBFacade(DynamoDB(config))
    bot = Bot(WebClient(config.slack_api_token),
              config.slack_notification_channel)
    return SlackEventsHandler(facade, bot)


def create_signing_token() -> str:
    """Create a new, random signing token."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(24))
