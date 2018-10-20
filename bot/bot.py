"""Utility class for interacting with Slack API"""
import os
from slackclient import SlackClient

# slack_token = os.environ["SLACK_API_TOKEN"]
slack_token = "xoxp-450677644563-450964940005-450690754371-72246adde9effadb4b6d89791edb6316"

class Bot:
  """Utility class for interacting with Slack API"""
  def __init__(self):
    """Initialize Bot by creating a SlackClient Object"""
    self.sc = SlackClient(slack_token)

  def send_dm(self, message, slack_user_id):
    """Send direct message to user with id of slack_user_id"""
    response = self.sc.api_call(
      "chat.postMessage",
      channel=slack_user_id,
      text=message
    )

    if not response['ok']:
      raise Exception('API Call error: {}'.format(response["error"]))

    return

  def send_to_channel(self, message, channel_name):
    response = self.sc.api_call(
      "chat.postMessage",
      channel=channel_name,
      text=message
    )


# Example of how we are going to use SlackBot interface
# Bot().send_dm("Hello <@UD8UCTN05>", "UD8UCTN05")