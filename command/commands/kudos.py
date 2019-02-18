import argparse
import logging
import shlex

class KudosCommand:
    """Kudos command parser"""

    command_name = "kudos"
    help = "Kudos command reference:\n\n /rocket kudos"\
            "\n\nOptions:\n\n" \
            "user"
    lookup_error = "User doesn't exist"
    desc = "for dealing with " + command_name

    def __init__(self, db_facade):
        """Initialize kudos command"""
        logging.info("Starting kudos command initializer")
        self.parser = argparse.ArgumentParser(prog="kudos")
        self.parser.add_argument("kudos")
        self.facade = db_facade

    def handle(self, command, user_id):
        logging.debug('Handling Kudos Command')
        command_arg = shlex.split(command)
        reciever = self.parse_reciever(command_arg)
        print("called handle in kudos")
        print("kudos to " + reciever)
        print("Called from id: " + user_id)


        return self.help, 200

    def parse_reciever(self, command_arg):
        """Gets the reciever from the command arg"""
        return command_arg[1]
