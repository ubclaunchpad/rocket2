"""Flask server instance."""
from flask import Flask
from slackeventsapi import SlackEventAdapter
from command.core import Core
import logging

app = Flask(__name__)
core = Core()
logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s',
                    level=logging.INFO)


@app.route('/')
def check():
    """Display a Rocket status image."""
    logging.info('ROCKET2 IS RUNNING')
    return "🚀"


slack_events_adapter = SlackEventAdapter(None,
                                         "/slack/events", app)


@slack_events_adapter.on("app_mention")
def handle_mention(event):
    """Handle a mention to @rocket."""
    core.handle_app_mention(event)
