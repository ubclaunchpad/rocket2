"""Command parsing for team events."""
import argparse
import shlex


class TeamCommand:
    """Represent Team Command Parser."""

    __command_name = "team"
    __help = ""

    """Top level Team parser."""
    parser = argparse.ArgumentParser(prog="team")
    parser.add_argument("team")
    subparsers = parser.add_subparsers()

    def get_name(self):
        """Return the command type."""
        return self.__command_name

    def get_help(self):
        """Return command options for team events."""
        return self.__help

    def handle(self, command):
        """Handle command by splitting into substrings and giving to parser."""
        # stub
        return ""
