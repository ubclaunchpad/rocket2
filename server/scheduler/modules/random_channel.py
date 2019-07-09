"""Feature random public channels."""
from slack import WebClient
from interface.slack import Bot
from random import choice
from .base import ModuleBase
from typing import Dict, Any
from flask import Flask
from config import Credentials
import logging


class RandomChannelPromoter(ModuleBase):
    """Module that promotes a random channel every Saturday."""

    NAME = 'Feature random channels'

    def __init__(self,
                 flask_app: Flask,
                 config: Dict[str, Any],
                 credentials: Credentials):
        """Initialize the object."""
        self.bot = Bot(WebClient(credentials.slack_api_token),
                       config['slack']['bot_channel'])

    def get_job_args(self) -> Dict[str, Any]:
        """Get job configuration arguments for apscheduler."""
        return {'trigger':      'cron',
                'day_of_week':  'sat',
                'hour':         12,
                'name':         self.NAME}

    def do_it(self):
        """Select and post random channels to #general."""
        channels = self.bot.get_channels()
        rand_channel = choice(channels)
        channel_id, channel_name = rand_channel['id'], rand_channel['name']
        self.bot.send_to_channel(f'Featured channel of the week: ' +
                                 f'<#{channel_id}|{channel_name}>!',
                                 '#general')

        logging.info(f'Featured #{channel_name}')
