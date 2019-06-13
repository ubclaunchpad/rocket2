"""Feature random public channels."""
from slackclient import SlackClient
from interface.slack import Bot
from random import choice
import logging


NAME = 'Feature random channels'


def do_it(flask_app, config, credentials):
    """Select and post random channels to #general."""
    bot = Bot(SlackClient(credentials.slack_api_token),
              config['slack']['bot_channel'])
    channels = bot.get_channels()
    rand_channel = choice(channels)
    bot.send_to_channel(f'Featured channel of the week: #{rand_channel}!',
                        '#general')

    logging.info(f'Featured #{rand_channel}')
