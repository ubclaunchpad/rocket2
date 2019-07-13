"""Test how random channels would work."""
from unittest import mock
from app.scheduler.modules.random_channel import RandomChannelPromoter


@mock.patch('flask.Flask')
@mock.patch('config.Credentials', autospec=True)
@mock.patch('interface.slack.Bot', autospec=True)
def test_doing_it(bot, creds, app):
    """Test selecting and posting a random channel."""
    creds.slack_api_token = ''
    bot.get_channels.return_value = [{'id': '123', 'name': 'general'},
                                     {'id': '321', 'name': 'random'}]

    config = {'slack': {'bot_channel': ''}}
    promoter = RandomChannelPromoter(app, config, creds)
    promoter.bot = bot

    promoter.do_it()

    bot.send_to_channel.assert_called()
    assert 'general' in bot.send_to_channel.call_args[0][0] or\
        'random' in bot.send_to_channel.call_args[0][0]
