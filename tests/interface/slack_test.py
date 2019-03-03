"""Test Bot Class."""
from interface.slack import Bot, SlackAPIError
from slackclient import SlackClient
from unittest import mock, TestCase


class TestBot(TestCase):
    """Test Case for Bot class."""

    def setUp(self):
        """Set up the test case environment."""
        self.mock_sc = mock.MagicMock(SlackClient)

    def test_send_dm(self):
        """Test the Bot class method send_dm()."""
        bot = Bot(self.mock_sc)
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": True})

        bot.send_dm("Hahahaha", "UD8UCTN05")
        self.mock_sc.api_call.assert_called_with(
            'chat.postMessage',
            text="Hahahaha",
            channel="UD8UCTN05"
        )

    def test_send_dm_failure(self):
        """Test send_dm() when the Slack API call fails."""
        bot = Bot(self.mock_sc)
        self.mock_sc.api_call = mock.MagicMock(return_value={"error": "Error"})

        try:
            bot.send_dm("Hahahaha", "UD8UCTN05")
        except SlackAPIError as e:
            assert e.error == "Error"
        finally:
            self.mock_sc.api_call.assert_called_with(
                'chat.postMessage',
                text="Hahahaha",
                channel="UD8UCTN05"
            )

    def test_send_to_channel(self):
        """Test the Bot class method send_to_channel()."""
        bot = Bot(self.mock_sc)
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": True})

        bot.send_to_channel("Hahahaha", "#random")
        self.mock_sc.api_call.assert_called_with(
            'chat.postMessage',
            text="Hahahaha",
            attachments=[],
            channel="#random"
        )

    def test_send_to_channel_failure(self):
        """Test send_to_channel() when the Slack API call fails."""
        bot = Bot(self.mock_sc)
        self.mock_sc.api_call = mock.MagicMock(return_value={"error": "Error"})

        try:
            bot.send_to_channel("Hahahaha", "#random")
        except SlackAPIError as e:
            assert e.error == "Error"
        finally:
            self.mock_sc.api_call.assert_called_with(
                'chat.postMessage',
                text="Hahahaha",
                attachments=[],
                channel="#random"
            )

    def test_get_channel_users(self):
        """Test the bot method get_channel_users()."""
        bot = Bot(self.mock_sc)
        ids = ["U12314", "U42839", "U31055"]
        self.mock_sc.api_call.return_value = """
            {
                "ok": true,
                "members": [
                    "U12314",
                    "U42839",
                    "U31055"
                ]
            }"""

        assert bot.get_channel_users("C1234441") == ids
        self.mock_sc.api_call.assert_called_with(
            'conversation.members',
            channel="C1234441"
        )

    def test_get_channel_users_failure(self):
        """Test get_channel_users() when Slack API call fails."""
        bot = Bot(self.mock_sc)
        self.mock_sc.api_call = mock.MagicMock(return_value={"error": "Error"})

        try:
            bot.get_channel_users("C1234441")
        except SlackAPIError as e:
            assert e.error == "Error"
        finally:
            self.mock_sc.api_call.assert_called_with(
                'conversation.members',
                channel="C1234441"
            )
