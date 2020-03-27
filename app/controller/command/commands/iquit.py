"""Command parsing for quitting events."""
import logging
import shlex
import random

from argparse import ArgumentParser, _SubParsersAction
from app.controller import ResponseTuple
from app.controller.command.commands.base import Command
from db.facade import DBFacade
from db.utils import get_users_by_ghid
from interface.github import GithubAPIException, GithubInterface
from app.model import User, Team, Permissions
from typing import Dict, List, Tuple
from utils.slack_parse import escape_email


class IQuitCommand(Command):
    """Represent iquit command parser."""

    command_name = "i-quit"
    lookup_error = "Lookup error! User not found!"
    delete_text = "Deleted user with Slack ID: "
    desc = f"`New!` for dealing with quitting users. Try it out!"
    snowflake = "You think you are so special, huh?"
    adminmsg = "Oh well. You can do whatever you want I guess."
    teamleadmsg = "Resignation processed successfully. Notifying admins:"
    membermsg = "Resignation processed successfully. Notifying team leads " +\
        "and admins:"
    remfromall = "Removing from Github Organization, teams, and projects. " +\
        "Reverting commits you have made."

    def __init__(self, dbf: DBFacade):
        """Initialize iquit command."""
        logging.info("Initializing IQuitCommand instance")
        self.parser = ArgumentParser(prog="/rocket")
        self.parser.add_argument("i-quit")
        self.facade = dbf

    def handle(self, command: str, user_id: str) -> ResponseTuple:
        """
        Handle the command if it is called in any way shape or form.

        - For normal users, we display a message including the names of their
          team leads and the admins.
        - For team leads, we display a message including the names of the
          admins.
        - Nothing happens for admins.
        """
        logging.debug("Handling IQuitCommand")
        user: User = None
        try:
            user = self.facade.retrieve(User, user_id)
        except LookupError:
            return self.lookup_error, 200

        if user.permissions_level == Permissions.member:
            # User is a member
            leads = self.get_leads(user)
            leads.extend(self.get_admins())
            return self.membermsg + "\n(Pinging {})".format(
                ", ".join(map(lambda u: f"<@{u.slack_id}>", leads))
            ) + "\n\n" + self.remfromall, 200
        if user.permissions_level == Permissions.team_lead:
            # User is a team lead
            admins = self.get_admins()
            return self.teamleadmsg + "\n(Pinging {})".format(
                ", ".join(map(lambda u: f"<@{u.slack_id}>", admins))
            ) + "\n\n" + self.get_teamlead_specialtext(user), 200
        if user.permissions_level == Permissions.admin:
            # User is an admin
            return self.adminmsg, 200

        return self.snowflake, 200

    def get_leads(self, user: User) -> List[User]:
        """Return a list of team leads user is in a team with."""
        teams: List[Team] = self.facade.query(Team)
        leads: List[User] = []
        for team in teams:
            if team.has_member(user.github_id):
                leads.extend(get_users_by_ghid(self.facade, team.team_leads))
        return leads

    def get_admins(self) -> List[User]:
        """Return a list of current admins."""
        admins: List[User] = self.facade.query(User, [("permission_level",
                                                       "admin")])
        return admins

    def get_teamlead_specialtext(self, user: User) -> str:
        """Return special text for team leads."""
        teams: List[Team] = self.facade.query_or(Team, [("team_leads",
                                                         user.github_id)])
        ctx: Dict[str, str] = {}
        for team in teams:
            # Find a random member in the team and use them to replace you. If
            # we cannot another random member, just say that we deleted the
            # team.
            members = team.members - team.team_leads
            if members:
                random.shuffle(members)
                for gh_id in members:
                    # Try all members until we exhaust the pool and then quit
                    # trying
                    users = get_users_by_ghid(self.facade, [gh_id])
                    if len(users) == 0:
                        continue

                    ctx[team.github_team_name] =\
                        f"replacing you with <@{users[0].slack_id}>"
                    break
                if team.github_team_name not in ctx:
                    ctx[team.github_team_name] =\
                        "cannot find your replacement; deleting team"
            else:
                ctx[team.github_team_name] =\
                    "cannot find your replacement; deleting team"

        return "\n".join(
            map(lambda i: f"*Team {i[0]}*: {i[1]}", ctx.items())
        )
