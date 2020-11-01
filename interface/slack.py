"""Utility classes for interacting with Slack API."""
from slack import WebClient
from slack.web.base_client import SlackResponse
from typing import Dict, Any, List, cast
import logging


class Bot:
    """Utility class for calling Slack APIs."""

    def __init__(self, sc: WebClient, slack_channel: str = ''):
        """Initialize Bot by creating a WebClient Object."""
        logging.info("Initializing Slack client interface")
        self.sc = sc
        self.slack_channel = slack_channel

    def send_dm(self, message: str, slack_user_id: str):
        """Send direct message to user with id of slack_user_id."""
        logging.debug(f"Sending direct message to {slack_user_id}")
        response = cast(SlackResponse, self.sc.chat_postMessage(
            channel=slack_user_id,
            text=message,
            as_user=True
        ))
        if not response['ok']:
            logging.error(f"Direct message to {slack_user_id} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])

    def send_to_channel(self,
                        message: str,
                        channel_name: str,
                        attachments: List[Any] = []):
        """Send message to channel with name channel_name."""
        logging.debug(f"Sending message to channel {channel_name}")
        response = cast(SlackResponse, self.sc.chat_postMessage(
            channel=channel_name,
            attachments=attachments,
            text=message
        ))
        if not response['ok']:
            logging.error(f"Message to channel {channel_name} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])

    def get_channel_users(self, channel_id: str) -> Dict[str, Any]:
        """Retrieve list of user IDs from channel with channel_id."""
        logging.debug(f"Retrieving user IDs from channel {channel_id}")
        response = cast(SlackResponse, self.sc.conversations_members(
            channel=channel_id
        ))
        if not response['ok']:
            logging.error("User retrieval "
                          f"from channel {channel_id} failed with "
                          f"error: {response['error']}")
            raise SlackAPIError(response['error'])
        else:
            return cast(Dict[str, Any], response["members"])

    def get_channel_names(self) -> List[str]:
        """Retrieve list of channel names."""
        return list(map(lambda c: str(c['name']), self.get_channels()))

    def get_channels(self) -> List[Any]:
        """Retrieve list of channel objects."""
        resp = cast(SlackResponse, self.sc.conversations_list())
        if not resp['ok']:
            logging.error(f"Channel retrieval failed with "
                          f"error: {resp['error']}")
            raise SlackAPIError(resp['error'])
        else:
            return cast(List[Any], resp['channels'])

    def create_channel(self, channel_name):
        """
        Create a channel with the given name.

        :return name of newly created channel
        """
        logging.debug("Attempting to create channel with name {}".
                      format(channel_name))
        response = cast(SlackResponse, self.sc.channels_create(
            name=channel_name,
            validate=True
        ))
        if not response['ok']:
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

    def create_private_chat(self, users: List[str]):
        """
        Create a private chat with the given users

        :param users: the list of users to add to the private chat

        :raise SlackAPIError if the slack API returned error openning the chat

        :return The name of of the private chat created
        """
        logging.debug(
            f"Attempting to open a private conversation with users {users}")
        response = self.sc.conversations_open(users=users)
        if response['ok']:
            logging.debug(
                f"Successfly opened a converation with the name \
                    {response['channel']['name']}")
            return response['channel']['name']
        raise SlackAPIError(response['error'])

    def get_channel_id(self, channel_name: str):
        """
        Retrieves a channel's id given it's name

        :param channel_name: The name of the channel

        :raise SlackAPIError if no channels were found with the name
        `channel_name`

        :return the slack id of the channel
        """
        # We strip away the "#" in case it was provided with the channel name
        channel_name = channel_name.replace("#", "")
        logging.debug(f"Attempting to get the id of channel {channel_name}")
        channels = list(
            filter(lambda c: c['name'] == channel_name,
                   self.get_channels()))
        if len(channels) == 0:
            raise SlackAPIError(
                f"No channels found with the name {channel_name}")
        if len(channels) != 1:
            logging.warning(
                f"Somehow there is more than one channel\
                     with the name {channel_name}"
                )
        return channels[0]['id']


class SlackAPIError(Exception):
    """Exception representing an error while calling Slack API."""

    def __init__(self, error):
        """
        Initialize a new SlackAPIError.

        :param error: Error string returned from Slack API.
        """
        self.error = error
