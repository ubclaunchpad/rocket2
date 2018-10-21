from slackeventsapi import SlackEventAdapter
import os

slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")

commands = {}

@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    message = event_data["event"]["text"]
    s = message.split(' ', 2)
    if s[0] is not "@rocket":
        pass
    else:
        command = s[1] + ' ' + s[2]
        commands[user].handle(command)

slack_events_adapter.start(port=3000)