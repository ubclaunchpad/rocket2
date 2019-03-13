"""Utility classes for interacting with Slack API."""
import logging
import json


class Bot:
    """Utility class for calling Slack APIs."""

    def __init__(self, sc):
        """Initialize Bot by creating a SlackClient Object."""
        logging.info("Initializing Slack client interface")
        self.sc = sc

    def send_dm(self, message, slack_user_id):
        """Send direct message to user with id of slack_user_id."""
        logging.debug(f"Sending direct message to {slack_user_id}")
        response = self.sc.api_call(
            "chat.postMessage",
            channel=slack_user_id,
            text=message
        )
        if 'ok' not in response:
            logging.error(f"Direct message to {slack_user_id} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])

    def send_to_channel(self, message, channel_name, attachments=[]):
        """Send message to channel with name channel_name."""
        logging.debug(f"Sending message to channel {channel_name}")
        response = self.sc.api_call(
            "chat.postMessage",
            channel=channel_name,
            attachments=attachments,
            text=message
        )
        if 'ok' not in response:
            logging.error(f"Message to channel {channel_name} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])

    def get_channel_users(self, channel_id):
        """Retrieve list of user IDs from channel with channel_id."""
        logging.debug(f"Retrieving user IDs from channel {channel_id}")
        response = self.sc.api_call(
            "conversation.members",
            channel=channel_id
        )
        if 'ok' not in response:
            logging.error("User retrieval "
                          f"from channel {channel_id} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])
        else:
            json_response = json.loads(response)
            return json_response["members"]


class SlackAPIError(Exception):
    """Exception representing an error while calling Slack API."""

    def __init__(self, error):
        """
        Initialize a new SlackAPIError.

        :param error: Error string returned from Slack API.
        """
        self.error = error
