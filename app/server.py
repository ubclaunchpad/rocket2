"""Flask server instance."""
from factory import make_command_parser, make_github_webhook_handler, \
    make_slack_events_handler
from flask import Flask, request
from logging.config import dictConfig
from slackeventsapi import SlackEventAdapter
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import structlog
from flask_talisman import Talisman
from config import Config
from app.scheduler import Scheduler
from interface.slack import Bot
from slack import WebClient
from boto3.session import Session
from threading import Thread

config = Config()
boto3_session = Session(aws_access_key_id=config.aws_access_keyid,
                        aws_secret_access_key=config.aws_secret_key,
                        region_name=config.aws_region)

dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'aws': {
            # No time b.c. CloudWatch logs times
            'format': u"[%(levelname)-8s] %(message)s "
                      u"{%(module)s.%(funcName)s():%(lineno)s %(pathname)s}",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        "colored": {
            'format': '{Time: %(asctime)s, '
                      'Level: [%(levelname)s], '
                      'module: %(module)s, '
                      'function: %(funcName)s():%(lineno)s, '
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
        },
        'watchtower': {
            'level': 'DEBUG',
            'class': 'watchtower.CloudWatchLogHandler',
            'boto3_session': boto3_session,
            'log_group': 'watchtower',
            'stream_name': 'rocket2',
            'formatter': 'aws',
        },
    },
    'root': {
        'level': 'INFO',
        'propagate': True,
        'handlers': ['wsgi', 'watchtower']
    }
})

app = Flask(__name__)
# HTTP security header middleware for Flask
talisman = Talisman(app)
talisman.force_https = False
command_parser = make_command_parser(config)
github_webhook_handler = make_github_webhook_handler(config)
slack_events_handler = make_slack_events_handler(config)
slack_events_adapter = SlackEventAdapter(config.slack_signing_secret,
                                         "/slack/events",
                                         app)
sched = Scheduler(BackgroundScheduler(timezone="America/Los_Angeles"),
                  (app, config))
sched.start()

bot = Bot(WebClient(config.slack_api_token),
          config.slack_notification_channel)
bot.send_to_channel('rocket2 has restarted successfully! :clap: :clap:',
                    config.slack_notification_channel)


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
        response_url = request.form['response_url']
        Thread(target=command_parser.handle_app_command,
               args=(txt, uid, response_url)).start()
        return "", 200
    else:
        logging.error("Slack signature could not be verified")
        return "Slack signature could not be verified", 200


@app.route(config.github_webhook_endpt, methods=['POST'])
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
