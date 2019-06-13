"""Test Bot Class."""
from interface.slack import Bot, SlackAPIError
from slack import WebClient
from unittest import mock, TestCase


OK_RESP = {'ok': True}
BAD_RESP = {'ok': False, 'error': 'Error'}


class TestBot(TestCase):
    """Test Case for Bot class."""

    def setUp(self):
        """Set up the test case environment."""
        self.mock_sc = mock.MagicMock(WebClient)
        self.bot = Bot(self.mock_sc)

    def test_send_dm(self):
        """Test the Bot class method send_dm()."""
        self.mock_sc.chat_postMessage = mock.MagicMock(return_value=OK_RESP)

        self.bot.send_dm("Hahahaha", "UD8UCTN05")
        self.mock_sc.chat_postMessage.assert_called_with(
            text="Hahahaha",
            channel="UD8UCTN05"
        )

    def test_send_dm_failure(self):
        """Test send_dm() when the Slack API call fails."""
        self.mock_sc.chat_postMessage = mock.MagicMock(return_value=BAD_RESP)

        try:
            self.bot.send_dm("Hahahaha", "UD8UCTN05")
        except SlackAPIError as e:
            assert e.error == "Error"
        finally:
            self.mock_sc.chat_postMessage.assert_called_with(
                text="Hahahaha",
                channel="UD8UCTN05"
            )

    def test_send_to_channel(self):
        """Test the Bot class method send_to_channel()."""
        self.mock_sc.chat_postMessage = mock.MagicMock(return_value=OK_RESP)

        self.bot.send_to_channel("Hahahaha", "#random")
        self.mock_sc.chat_postMessage.assert_called_with(
            text="Hahahaha",
            attachments=[],
            channel="#random"
        )

    def test_send_to_channel_failure(self):
        """Test send_to_channel() when the Slack API call fails."""
        self.mock_sc.chat_postMessage = mock.MagicMock(return_value=BAD_RESP)

        try:
            self.bot.send_to_channel("Hahahaha", "#random")
        except SlackAPIError as e:
            assert e.error == "Error"
        finally:
            self.mock_sc.chat_postMessage.assert_called_with(
                text="Hahahaha",
                attachments=[],
                channel="#random"
            )

    def test_get_channels(self):
        """Test get_channel_names() method."""
        resp = {'ok': True, 'channels': []}
        self.mock_sc.conversations_list = mock.MagicMock(return_values=resp)
        names = self.bot.get_channel_names()

        assert len(names) == 0

    def test_get_channel_users(self):
        """Test the bot method get_channel_users()."""
        ids = ["U12314", "U42839", "U31055"]
        self.mock_sc.conversations_members.return_value = {'ok': True,
                                                           'members': [
                                                               "U12314",
                                                               "U42839",
                                                               "U31055"
                                                           ]}
        assert self.bot.get_channel_users("C1234441") == ids
        self.mock_sc.conversations_members.assert_called_with(
            channel="C1234441"
        )

    def test_get_channel_users_failure(self):
        """Test get_channel_users() when Slack API call fails."""
        self.mock_sc.conversations_members =\
            mock.MagicMock(return_value={"ok": False, "error": "Error"})

        try:
            self.bot.get_channel_users("C1234441")
        except SlackAPIError as e:
            assert e.error == "Error"
        finally:
            self.mock_sc.conversations_members.assert_called_with(
                channel="C1234441"
            )

    def test_create_same_channel_thrice(self):
        """Test create_channel() thrice, with the third call throwing up."""
        name: str = "#rocket2"
        self.mock_sc.channels_create.return_value = {"ok": True,
                                                     "name": name}
        assert self.bot.create_channel(name) == name
        try:
            self.mock_sc.channels_create.return_value =\
                {"ok": False, "error": "name_taken"}
            assert self.bot.create_channel(name) == name
            self.mock_sc.channels_create.return_value =\
                {"ok": False, "error": "invalid_name"}
            self.bot.create_channel(name)
        except SlackAPIError as e:
            assert e.error == "invalid_name"
