"""Flask server instance."""
from factory import make_command_parser, make_github_webhook_handler, \
    make_slack_events_handler
from flask import Flask, request
from logging.config import dictConfig
from slackeventsapi import SlackEventAdapter
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import toml
import structlog
from flask_talisman import Talisman
from config import Credentials
from typing import cast, Dict, Any
from app.scheduler import Scheduler
from datetime import tzinfo


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
config = cast(Dict[str, Any], toml.load('config.toml'))
credentials = Credentials(config['creds_path'])
command_parser = make_command_parser(config, credentials)
github_webhook_handler = make_github_webhook_handler(config, credentials)
slack_events_handler = make_slack_events_handler(config, credentials)
if not config['testing']:
    slack_signing_secret = credentials.slack_signing_secret
else:
    slack_signing_secret = ""
slack_events_adapter = SlackEventAdapter(slack_signing_secret,
                                         "/slack/events", app)
sched = Scheduler(BackgroundScheduler(timezone="America/Los_Angeles"),
                  (app, config, credentials))
sched.start()


@app.route('/')
def check():
    """Display a Rocket status image."""
    logging.info('Served check()')
    return "🚀"


@app.route('/slack/commands', methods=['POST'])
def handle_commands():
    """Handle rocket slash commands."""
    logging.info("Slash command received")
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request.headers.get("X-Slack-Signature")
    verified = slack_events_adapter.server.verify_signature(
        timestamp, slack_signature)
    if verified:
        logging.info("Slack signature verified")
        txt = request.form['text']
        uid = request.form['user_id']
        return command_parser.handle_app_command(txt, uid)
    else:
        logging.error("Slack signature could not be verified")
        return "Slack signature could not be verified", 200


@app.route(config['github']['webhook_url'], methods=['POST'])
def handle_github_webhook():
    """Handle GitHub webhooks."""
    xhub_signature = request.headers.get('X-Hub-Signature')
    request_data = request.get_data()
    request_json = request.get_json()
    msg = github_webhook_handler.handle(
        request_data, xhub_signature, request_json)
    return msg


@slack_events_adapter.on("team_join")
def handle_team_join(event):
    """Handle instances when user joins the Launchpad slack workspace."""
    logging.info("Handled 'team_join' event")
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    slack_signature = request.headers.get("X-Slack-Signature")
    verified = slack_events_adapter.server.verify_signature(
        timestamp, slack_signature)
    if verified:
        logging.info("Slack signature verified")
        slack_events_handler.handle_team_join(event)
    else:
        logging.error("Slack signature could not be verified")
