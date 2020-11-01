"""Utilities for common interactions with Google API."""
import logging
from typing import List, Optional
from interface.gcp import GCPInterface, standardize_email
from db import DBFacade
from db.utils import get_team_members
from app.model import User, Team


def sync_user_email_perms(gcp: Optional[GCPInterface],
                          db: DBFacade,
                          user: User):
    """
    Refresh Google Drive permissions for a provided user. If no GCP client is
    provided, this function is a no-op.

    Finds folders for user by checking all teams the user is a part of, and
    calling :func:`sync_team_email_perms`.

    :param gcp: the interface to do this from; can be `None` to function as
        no-op
    :param db: the database facade interface
    :param user: user model to refresh Google Drive permissions
    """
    if gcp is None:
        logging.debug('GCP not enabled, skipping drive permissions')
        return

    if len(user.email) == 0 or len(user.github_id) == 0:
        return

    teams_user_is_in = db.query(Team, [('members', user.github_id)])
    for team in teams_user_is_in:
        sync_team_email_perms(gcp, db, team)


def sync_team_email_perms(gcp: Optional[GCPInterface],
                          db: DBFacade,
                          team: Team):
    """
    Refresh Google Drive permissions for provided team. If no GCP client
    is provided, this function is a no-op.

    :param gcp: the interface to do this from; can be `None` to function as
        no-op
    :param db: the database facade interface
    :param team: refresh Google Drive permissions based on team model; if there
        is no folder for the team model, functions as no-op
    """
    if gcp is None:
        logging.debug("GCP not enabled, skipping drive permissions")
        return

    if len(team.folder) == 0:
        return

    # Generate who to share with
    team_members = get_team_members(db, team)
    emails: List[str] = []
    for user in team_members:
        if len(user.email) > 0:
            try:
                emails.append(standardize_email(user.email))
            except Exception as e:
                logging.warn(f'Found malformed email {user.email} for user '
                             + f'{user.github_username}: {e}')

    # Sync permissions
    if len(emails) > 0:
        logging.info("Synchronizing permissions for "
                     + f"{team.github_team_name}'s folder ({team.folder})")
        gcp.ensure_drive_permissions(
            team.github_team_name, team.folder, emails)
