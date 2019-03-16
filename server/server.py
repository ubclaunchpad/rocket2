"""Flask server instance."""
from factory import make_core, make_webhook_handler
from flask import Flask, request
from logging.config import dictConfig
from slackeventsapi import SlackEventAdapter
import logging
import sys
import toml
import structlog
from flask_talisman import Talisman
from flask_seasurf import SeaSurf
from interface.slack import SlackAPIError
from config import Credentials

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{Time: %(asctime)s, Level: [%(levelname)s], ' +
                      'module: %(module)s, function: %(funcName)s()' +
                      ':%(lineno)s, message: %(message)s}',
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        "colored": {
            'format': '{Time: %(asctime)s, '
                      'Level: [%(levelname)s], ' +
                      'module: %(module)s, '
                      'function: %(funcName)s():%(lineno)s, ' +
                      'message: %(message)s}',
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(colors=True),
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }},
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'colored'
        }
    },
    'root': {
        'level': 'INFO',
        'propogate': True,
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
# HTTP security header middleware for Flask
talisman = Talisman(app)
talisman.force_https = False
config = toml.load('config.toml')
credentials = Credentials(config['creds_path'])
core = make_core(config, credentials)
webhook_handler = make_webhook_handler(config, credentials)
if not config['testing']:
    slack_signing_secret = credentials.slack_signing_secret
else:
    slack_signing_secret = ""
slack_events_adapter = SlackEventAdapter(slack_signing_secret,
                                         "/slack/events", app)


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


@app.route('/webhook/organization', methods=['POST'])
def handle_organization_webhook():
    """Handle GitHub organization webhooks."""
    logging.info("organization webhook triggered")
    logging.debug(f"organization payload: {str(request.get_json())}")
    return webhook_handler.handle_organization_event(request.get_json())


@app.route('/webhook/team', methods=['POST'])
def handle_team_webhook():
    """Handle GitHub team webhooks."""
    logging.info("team webhook triggered")
    logging.debug(f"team payload: {str(request.get_json())}")
    msg = webhook_handler.handle_team_event(request.get_json())
    core.send_event_notif(msg[0].capitalize())
    return msg


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
