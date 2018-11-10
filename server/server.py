"""Flask server instance."""
from flask import Flask
from slackeventsapi import SlackEventAdapter
from command.core import Core

app = Flask(__name__)
core = Core()


@app.route('/')
def check():
    """Display a Rocket status image."""
    return "🚀"


slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET,
                                         "/slack/events", app)


@slack_events_adapter.on("app_mention")
def handle_mention(event):
    """Handle a mention to @rocket."""
    core.handle_app_mention(event)
