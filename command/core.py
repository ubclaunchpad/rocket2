"""Calls the appropriate handler depending on the event data."""
from command.commands.user import UserCommand


class Core:
    """Encapsulate methods for handling events."""

    def __init__(self):
        """Initialize the dictionary of command handlers."""
        self.__commands = {}
        self.__commands["user"] = UserCommand()

    def handle_app_mention(self, event_data):
        """Handle the events associated with mentions of @rocket."""
        message = event_data["event"]["text"]
        user = event_data["event"]["user"]
        s = message.split(' ', 2)
        if s[0] != "@rocket":
            return 0
        else:
            command_type = s[1]
            command = command_type + ' ' + s[2]
            try:
                self.__commands[command_type].handle(command, user)
                return 1
            except KeyError:
                return -1
