"""Flask server instance."""
from flask import Flask
from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from command.core import Core
from db.facade import DBFacade
from db.dynamodb import DynamoDB
from bot.bot import Bot
import os
import logging

app = Flask(__name__)
db_facade = DBFacade(DynamoDB())
bot = Bot(SlackClient())
core = Core(db_facade, bot)
logging.basicConfig(format='%(asctime)s - %(levelname)s @' +
                    '%(module)s-%(funcName)s : %(message)s',
                    level=logging.INFO)


@app.route('/')
def check():
    """Display a Rocket status image."""
    logging.info('Served check()')
    return "🚀"


SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET,
                                         "/slack/events", app)


@slack_events_adapter.on("app_mention")
def handle_mention(event):
    """Handle a mention to @rocket."""
    core.handle_app_mention(event)
