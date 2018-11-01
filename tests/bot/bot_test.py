"""Test Bot Class."""
from bot.bot import Bot
from slackclient import SlackClient

from unittest import mock, TestCase 

class TestBot(TestCase):
    
    def setUp(self):
        self.mock_sc = mock.MagicMock(SlackClient)
        

    def test_send_dm(self):
        """Test the Bot class method send_dm()."""
        bot = Bot(self.mock_sc)
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": True})
        
        bot.send_dm("Hahahaha", "UD8UCTN05")
        self.mock_sc.api_call.assert_called_with('chat.postMessage', text="Hahahaha", channel="UD8UCTN05")

    def test_send_to_channel(self):
        """Test the Bot class method send_to_channel()."""
        bot = Bot(self.mock_sc)
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": True})
        
        bot.send_to_channel("Hahahaha", "#random")
        self.mock_sc.api_call.assert_called_with('chat.postMessage', text="Hahahaha", channel="#random")
