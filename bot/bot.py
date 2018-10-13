import os
from slackclient import SlackClient

slack_token = os.environ["SLACK_BOT_TOKEN"]

class Bot:

  def __init__(self):
    self.sc = SlackClient(slack_token)

  def sendMsg(self, message, channel):
    self.sc.api_call(
      "chat.postMessage",
      channel=channel,
      text=message
    )


# Example of how we are going to use SlackBot interface
# Bot().sendMsg("Hello", "#random")