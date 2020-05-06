"""The following are a few functions to help in handling command."""
import re
from app.model import Permissions, User, Team
from typing import Optional


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

        /rocket user edit --username <@U1143214|su> --name "Steven Universe"

    After::

        /rocket user edit --username U1143214 --name "Steven Universe"

    :param s: string to convert
    :return: string where all instances of escaped ID is replaced with IDs
    """
    return re.sub(r"<[#@](\w+)\|[^>]+>",
                  r"\1",
                  s)


def ios_dash(s: str) -> str:
    """
    Convert a string with a dash (—) to just double-hyphens (--).

    Before::

        /rocket user edit —name "Steven Universe"

    After::

        /rocket user edit --name "Steven Universe"

    :param s: string to convert
    :return: string where all dashes are replaced with double-hyphens
    """
    return s.replace("—", "--")


def check_permissions(user: User, team: Optional[Team]) -> bool:
    """
    Check if given user is admin or team lead.

    If team is specified and user is not admin, check if user is team lead in
    team. If team is not specified, check if user is team lead.

    :param user: user who's permission needs to be checked
    :param team: team you want to check that has user as team lead
    :return: true if user is admin or a team lead, false otherwise
    """
    if user.permissions_level == Permissions.admin:
        return True
    if team is None:
        return user.permissions_level == Permissions.team_lead
    else:
        return team.has_team_lead(user.github_id)


def is_slack_id(id: str) -> bool:
    """
    Check if id given is a valid slack id.

    :param id: string of the object you want to check
    :return: true if object is a slack id, false otherwise
    """
    if re.match("^[UW][A-Z0-9]{8}$", id) is not None:
        return True
    else:
        return False


def escape_email(email: str) -> str:
    """
    Convert a string with escaped emails to just the email.

    Before::

        <mailto:email@a.com|email@a.com>

    After::

        email@a.com

    :param email: email to convert
    :return: unescaped email
    """
    return email.split('|')[0][8:]
