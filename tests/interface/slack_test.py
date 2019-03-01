"""Test Bot Class."""
from interface.slack import Bot, SlackAPIError
from slackclient import SlackClient
from unittest import mock, TestCase


class TestBot(TestCase):
    """Test Case for Bot class."""

    def setUp(self):
        """Set up the test case environment."""
        self.mock_sc = mock.MagicMock(SlackClient)
        self.bot = Bot(self.mock_sc)

    def test_send_dm(self):
        """Test the Bot class method send_dm()."""
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": True})

        self.bot.send_dm("Hahahaha", "UD8UCTN05")
        self.mock_sc.api_call.assert_called_with(
            'chat.postMessage',
            text="Hahahaha",
            channel="UD8UCTN05"
        )

    def test_send_dm_failure(self):
        """Test send_dm() when the Slack API call fails."""
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": False,
                                                             "error": "Error"})

        try:
            self.bot.send_dm("Hahahaha", "UD8UCTN05")
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
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": True})

        self.bot.send_to_channel("Hahahaha", "#random")
        self.mock_sc.api_call.assert_called_with(
            'chat.postMessage',
            text="Hahahaha",
            attachments=[],
            channel="#random"
        )

    def test_send_to_channel_failure(self):
        """Test send_to_channel() when the Slack API call fails."""
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": False,
                                                             "error": "Error"})

        try:
            self.bot.send_to_channel("Hahahaha", "#random")
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
        ids = ["U12314", "U42839", "U31055"]
        self.mock_sc.api_call.return_value = {'ok': True, 'members': [
            "U12314",
            "U42839",
            "U31055"
        ]}
        assert self.bot.get_channel_users("C1234441") == ids
        self.mock_sc.api_call.assert_called_with(
            'conversation.members',
            channel="C1234441"
        )

    def test_get_channel_users_failure(self):
        """Test get_channel_users() when Slack API call fails."""
        self.mock_sc.api_call = mock.MagicMock(return_value={"ok": False,
                                                             "error": "Error"})

        try:
            self.bot.get_channel_users("C1234441")
        except SlackAPIError as e:
            assert e.error == "Error"
        finally:
            self.mock_sc.api_call.assert_called_with(
                'conversation.members',
                channel="C1234441"
            )

    def test_create_same_channel_twice(self):
        """Test create_channel() twice, with the second call throwing up."""
        name: str = "#rocket2"
        self.mock_sc.api_call.return_value = {"ok": True,
                                              "name": name}
        assert self.bot.create_channel(name) == name
        self.mock_sc.api_call.return_value = {"ok": False,
                                              "error": "name_taken"}
        try:
            self.bot.create_channel(name)
        except SlackAPIError as e:
            assert 1 == 0
