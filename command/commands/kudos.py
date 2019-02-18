import argparse
import logging
import shlex
import re

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
        """Handle command by splitting into substrings"""
        logging.debug('Handling Kudos Command')
        command_arg = shlex.split(command)

        if(self.is_user(command_arg[0])):
            return self.short_kudos_helper(user_id, command_arg[0], command_arg[1])
        elif(command_arg[0] == "kudos" and self.is_user(command_arg[1])):
            reciever = self.parse_reciever(command_arg)
            return self.kudos_helper(user_id, reciever, 1)
        elif(command_arg[0] == "kudos" and command_arg[1] == "sub" and self.is_user(command_arg[3])):
            return self.kudos_helper(user_id, reciever, -1)

    def short_kudos_helper(self, giver, reciever, amount):
        logging.info("called short kudos helper")
        print("amount: " + amount)
        print("reciever: " + reciever)
        if(amount == "++"):
            return self.kudos_helper(giver, reciever, 1)
        elif(amount == "--"):
            return self.kudos_helper(giver, reciever, -1)
        return "ok", 200

    def kudos_helper(self, giver, receiver, amount):
        if(giver == receiver):
            return "cannot give karma to self", 200
        try:
            user = self.facade.retrieve_user(receiver)
            print(user)
        except:
            return self.lookup_error, 200

    def parse_reciever(self, command_arg):
        """Gets the reciever from the command arg"""
        return command_arg[1]

    def is_user(self, id):
        return re.match("^[UW][A-Z0-9]{8}$", id)
