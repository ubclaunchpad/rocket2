"""Flask server instance."""
from factory import make_core
from flask import Flask, request
from logging.config import dictConfig
from slackeventsapi import SlackEventAdapter
import logging
import sys
import toml

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s @ ' +
                      '%(module)s-%(funcName)s : %(message)s'
        }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

try:
    app = Flask(__name__)
    config = toml.load('config.toml')
    core = make_core(config)
    slack_signing_secret = toml.load(
        config['slack']['creds_path'])['signing_secret']
    slack_events_adapter = SlackEventAdapter(slack_signing_secret,
                                             "/slack/events", app)
except Exception as e:
    # A bit of a hack to catch exceptions
    # that Gunicorn/uWSGI would swallow otherwise
    logging.error(e)
    sys.exit(1)


@app.route('/')
def check():
    """Display a Rocket status image."""
    logging.info('Served check()')
    return "🚀"


@app.route('/slack/commands', methods=['POST'])
def handle_commands():
    """Handle rocket slash commands."""
    txt = request.form['text']
    uid = request.form['user_id']
    return core.handle_app_command(txt, uid)


@slack_events_adapter.on("app_mention")
def handle_app_mention(event):
    """Handle a mention to @rocket."""
    logging.info("Handled 'app_mention' event")
    core.handle_app_mention(event)


@slack_events_adapter.on("team_join")
def handle_team_join(event):
    """Handle instances when user joins the Launchpad slack workspace."""
    logging.info("Handled 'team_join' event")
    core.handle_team_join(event)
