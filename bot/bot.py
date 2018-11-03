"""Utility class for interacting with Slack API."""
import os
from slackclient import SlackClient


class Bot:
    """Utility class for interacting with Slack API."""

    def __init__(self, sc):
        """Initialize Bot by creating a SlackClient Object."""
        self.sc = sc

    def send_dm(self, message, slack_user_id):
        """Send direct message to user with id of slack_user_id."""
        response = self.sc.api_call(
                            "chat.postMessage",
                            channel=slack_user_id,
                            text=message
                            )
        if not response['ok']:
            print('API Call error: {}'.format(response["error"]))
            return False
        return True

    def send_to_channel(self, message, channel_name):
        """Send message to channel with name channel_name."""
        response = self.sc.api_call(
            "chat.postMessage",
            channel=channel_name,
            text=message
        )
        if not response['ok']:
            print('API Call error: {}'.format(response["error"]))
            return False
        return True


# Example of how we are going to use SlackBot interface
# Bot().send_dm("Hello <@UD8UCTN05>", "UD8UCTN05")
