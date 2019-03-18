"""Utility classes for interacting with Slack API."""
from slackclient import SlackClient
from typing import Dict, Any, List, cast
import logging


class Bot:
    """Utility class for calling Slack APIs."""

    def __init__(self, sc: SlackClient, slack_channel: str = '') -> None:
        """Initialize Bot by creating a SlackClient Object."""
        logging.info("Initializing Slack client interface")
        self.sc = sc
        self.slack_channel = slack_channel

    def send_dm(self, message: str, slack_user_id: str) -> None:
        """Send direct message to user with id of slack_user_id."""
        logging.debug(f"Sending direct message to {slack_user_id}")
        response = self.sc.api_call(
            "chat.postMessage",
            channel=slack_user_id,
            text=message
        )
        if 'ok' not in response or not response['ok']:
            logging.error(f"Direct message to {slack_user_id} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])

    def send_to_channel(self,
                        message: str,
                        channel_name: str,
                        attachments: List[Any] = []) -> None:
        """Send message to channel with name channel_name."""
        logging.debug(f"Sending message to channel {channel_name}")
        response = self.sc.api_call(
            "chat.postMessage",
            channel=channel_name,
            attachments=attachments,
            text=message
        )
        if 'ok' not in response or not response['ok']:
            logging.error(f"Message to channel {channel_name} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])

    def get_channel_users(self, channel_id: str) -> Dict[str, Any]:
        """Retrieve list of user IDs from channel with channel_id."""
        logging.debug(f"Retrieving user IDs from channel {channel_id}")
        response = self.sc.api_call(
            "conversation.members",
            channel=channel_id
        )
        if 'ok' not in response or not response['ok']:
            logging.error("User retrieval "
                          f"from channel {channel_id} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])
        else:
            return cast(Dict[str, Any], response["members"])

    def create_channel(self, channel_name):
        """
        Create a channel with the given name.

        :return name of newly created channel
        """
        logging.debug("Attempting to create channel with name {}".
                      format(channel_name))
        response = self.sc.api_call(
            "channels.create",
            name=channel_name,
            validate=True
        )
        if 'ok' not in response or not response['ok']:
            if response['error'] == "name_taken":
                logging.warning("Channel with name {} "
                                "already exists!".
                                format(channel_name))
                return channel_name
            else:
                logging.error("Channel creation "
                              "with name {} failed with error: {}".
                              format(channel_name, response['error']))
                raise SlackAPIError(response['error'])
        else:
            return response["name"]

    def send_event_notif(self, message):
        """
        Send a message to the slack bot channel, usually for webhook notifs.

        :param message to send to configured bot channel
        """
        try:
            self.send_to_channel(message, self.slack_channel, [])
            logging.info("Webhook notif successfully sent to {} channel".
                         format(self.slack_channel))
        except SlackAPIError as se:
            logging.error("Webhook notif failed to send due to {} error.".
                          format(se.error))


class SlackAPIError(Exception):
    """Exception representing an error while calling Slack API."""

    def __init__(self, error):
        """
        Initialize a new SlackAPIError.

        :param error: Error string returned from Slack API.
        """
        self.error = error
