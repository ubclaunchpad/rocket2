"""All necessary class initializations."""
from db.facade import DBFacade
from db.dynamodb import DynamoDB
from command.core import Core
from slackclient import SlackClient
from interface.slack import Bot
from webhook.webhook import WebhookHandler
from github import Github, GithubException
import toml
from interface.github import GithubInterface
import logging


def make_core(config, gh=None):
    """
    Initialize and returns a :class:`command.core.Core` object.

    :return: a new ``Core`` object, freshly initialized
    """
    slack_api_token, github_api_token, github_organization = "", "", ""
    if not config['testing']:
        slack_api_token = toml.load(
            config['slack']['creds_path'])['api_token']
        github_api_token = toml.load(
            config['github']['creds_path'])['api_token']
        github_organization = config['github']['organization']
        gh = GithubInterface(Github(github_api_token), github_organization)
    facade = DBFacade(DynamoDB(config))
    bot = Bot(SlackClient(slack_api_token))
    return Core(facade, bot, gh)


def make_webhook_handler(config):
    """
    Initialize and returns a :class:`webhook.webhook.WebhookHandler` object.

    :return: a new ``WebhookHandler`` object, freshly initialized
    """
    facade = DBFacade(DynamoDB(config))
    return WebhookHandler(facade)
