"""
Some utility functions.

The following are a few function to help in command handling.
"""
import re
from model.permissions import Permissions

def regularize_char(c: str) -> str:
    """
    Convert any unicode quotation marks to ascii ones.

    Leaves all other characters alone.

    :param c: character to convert
    :return: ascii equivalent (only quotes are changed)
    """
    if c == "‘" or c == "’":
        return "'"
    if c == '“' or c == '”':
        return '"'
    return c


def escaped_id_to_id(s: str) -> str:
    """
    Convert a string with escaped IDs to just the IDs.

    Before::

        /rocket user edit --member <@U1143214|su> --name "Steven Universe"

    After::

        /rocket user edit --member U1143214 --name "Steven Universe"

    :param s: string to convert
    :return: string where all instances of escaped ID is replaced with IDs
    """
    return re.sub(r"<@(\w+)\|[^>]+>",
                  r"\1",
                  s)


def check_credentials(user, team):
    """
    Check if given user is admin or team lead.

    If team is specified and user is not admin, check if user is
    team lead in team. If team is not specified, check if user
    is team lead.
    :param user: user who's permission needs to be checked
    :param team: team you want to check has user as team lead
    :return: true if proper permission level, false otherwise
    """
    if user.permissions_level == Permissions.admin:
        return True
    if team is None:
        return user.permissions_level == Permissions.team_lead
    else:
        return team.has_team_lead(user.github_id)
