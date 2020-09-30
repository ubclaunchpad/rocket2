"""All necessary class initializations."""
import random
import string
import json
import logging

from app.controller.command import CommandParser
from app.controller.command.commands.token import TokenCommandConfig
from datetime import timedelta
from db import DBFacade
from db.dynamodb import DynamoDB
from interface.github import GithubInterface, DefaultGithubFactory
from interface.slack import Bot
from interface.gcp import GCPInterface
from interface.cloudwatch_metrics import CWMetrics
from slack import WebClient
from app.controller.webhook.github import GitHubWebhookHandler
from app.controller.webhook.slack import SlackEventsHandler
from config import Config
from google.oauth2 import service_account as gcp_service_account
from googleapiclient.discovery import build as gcp_build
from typing import Optional


def make_dbfacade(config: Config) -> DBFacade:
    return DynamoDB(config)


def make_github_interface(config: Config) -> GithubInterface:
    return GithubInterface(DefaultGithubFactory(config.github_app_id,
                                                config.github_key),
                           config.github_org_name)


def make_command_parser(config: Config, gh: GithubInterface) \
        -> CommandParser:
    # Initialize database
    facade = make_dbfacade(config)
    # Create Slack bot
    bot = Bot(WebClient(config.slack_api_token),
              config.slack_notification_channel)
    # TODO: make token config expiry configurable
    token_config = TokenCommandConfig(timedelta(days=7), config.github_key)
    # Metrics
    metrics = CWMetrics(config)
    # Create GCP client (optional)
    gcp_client = make_gcp_client(config)
    return CommandParser(config, facade, bot, gh, token_config, metrics,
                         gcp=gcp_client)


def make_github_webhook_handler(gh: GithubInterface,
                                config: Config) -> GitHubWebhookHandler:
    facade = make_dbfacade(config)
    return GitHubWebhookHandler(facade, gh, config)


def make_slack_events_handler(config: Config) -> SlackEventsHandler:
    facade = make_dbfacade(config)
    bot = Bot(WebClient(config.slack_api_token),
              config.slack_notification_channel)
    return SlackEventsHandler(facade, bot)


def make_gcp_client(config: Config) -> Optional[GCPInterface]:
    if len(config.gcp_service_account_credentials) == 0:
        logging.info("Google Cloud client not provided, disabling")
        return None

    scopes = ['https://www.googleapis.com/auth/drive']

    try:
        raw_credentials = json.loads(config.gcp_service_account_credentials)
        credentials = gcp_service_account.Credentials\
            .from_service_account_info(raw_credentials, scopes=scopes)
        if len(config.gcp_service_account_subject) > 0:
            credentials = credentials.with_subject(
                config.gcp_service_account_subject)
    except Exception as e:
        logging.error(f"Unable to load GCP credentials, disabling: {e}")
        return None

    # Build appropriate service clients.
    # See https://github.com/googleapis/google-api-python-client/blob/master/docs/dyn/index.md # noqa
    drive = gcp_build('drive', 'v3', credentials=credentials)
    return GCPInterface(drive, subject=config.gcp_service_account_subject)


def create_signing_token() -> str:
    """Create a new, random signing token."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(24))
