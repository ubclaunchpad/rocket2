"""Utility class for interacting with Slack API"""
import os
from slackclient import SlackClient
class Bot:
  """Utility class for interacting with Slack API"""

  def __init__(self):
    """Initialize Bot by creating a SlackClient Object"""
    token_not_found_message = "Token Not Found. Please add SLACK_API_TOKEN to your .env"
    slack_token = os.getenv("SLACK_API_TOKEN", token_not_found_message)
    if slack_token == token_not_found_message:
      raise Exception(token_not_found_message)
    self.sc = SlackClient(slack_token)

  def send_dm(self, message, slack_user_id):
    """Send direct message to user with id of slack_user_id"""
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
    """Send message to channel with name channel_name"""
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