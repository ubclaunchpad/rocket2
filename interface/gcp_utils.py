"""Utilities for common-used interactions with Google API."""
import logging
from interface.gcp import GCPInterface
from db import DBFacade
from app.model import User, Team


def sync_user_email_perms(gcp: GCPInterface, db: DBFacade, user: User):
    """
    Refresh Google Drive permissions for a provided user. If no GCP client is
    provided, this function is a no-op.

    Finds folders for user by checking all teams the user is a part of, and
    calling ``sync_team_email_perms()``.
    """
    if gcp is None:
        logging.debug('GCP not enabled, skipping drive permissions')
        return

    if len(user.email) == 0 or len(user.github_id) == 0:
        return

    teams_user_is_in = db.query(Team, [('members', user.github_id)])
    for team in teams_user_is_in:
        sync_team_email_perms(gcp, db, team)


def sync_team_email_perms(gcp: GCPInterface, db: DBFacade, team: Team):
    """
    Refresh Google Drive permissions for provided team. If no GCP client
    is provided, this function is a no-op.
    """
    if gcp is None:
        logging.debug("GCP not enabled, skipping drive permissions")
        return

    if len(team.folder) == 0:
        return

    # Generate who to share with
    emails: List[str] = []
    for github_id in team.members:
        users = db.query(User, [('github_user_id', github_id)])
        if len(users) != 1:
            logging.warn(f"None/multiple users for GitHub ID {github_id}")

        # For now, naiively iterate over all users, due to
        # https://github.com/ubclaunchpad/rocket2/issues/493
        for user in users:
            if len(user.email) > 0:
                emails.append(user.email)

    # Sync permissions
    if len(emails) > 0:
        logging.info("Synchronizing permissions for "
                     + f"{team.github_team_name}'s folder ({team.folder}) "
                     + f"to {emails}")
        gcp.set_drive_permissions(
            team.github_team_name, team.folder, emails)
