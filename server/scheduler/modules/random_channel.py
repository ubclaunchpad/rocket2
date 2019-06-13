"""Feature random public channels."""
from slack import WebClient
from interface.slack import Bot
from random import choice
import logging


NAME = 'Feature random channels'


def do_it(flask_app, config, credentials):
    """Select and post random channels to #general."""
    bot = Bot(WebClient(credentials.slack_api_token),
              config['slack']['bot_channel'])
    channels = bot.get_channels()
    rand_channel = choice(channels)
    channel_id, channel_name = rand_channel['id'], rand_channel['name']
    bot.send_to_channel(f'Featured channel of the week: ' +
                        f'<#{channel_id}|{channel_name}>!',
                        '#general')

    logging.info(f'Featured #{channel_name}')
