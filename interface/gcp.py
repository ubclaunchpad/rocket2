"""Utility classes for interacting with Google APIs"""
from typing import Any, List
from googleapiclient.discovery import Resource
import logging

# Set to False to resolve https://github.com/ubclaunchpad/rocket2/issues/510
# temporarily. Longer-term fix is being tracked in the actual problem,
# https://github.com/ubclaunchpad/rocket2/issues/497
DELETE_OLD_DRIVE_PERMISSIONS = False


class GCPInterface:
    """Utility class for calling Google Cloud Platform (GCP) APIs."""

    def __init__(self, drive_client: Resource, subject=None):
        logging.info("Initializing Google client interface")
        self.drive = drive_client
        self.subject = subject

    def set_drive_permissions(self,
                              team_name: str,
                              drive_id: str,
                              emails: List[str],
                              delete_permissions=DELETE_OLD_DRIVE_PERMISSIONS):
        """
        Create permissions for the given emails, and removes everyone not on
        the list.

        In all cases of API errors, we log and continue, to try and get close
        to the desired state of permissions.

        :param team_name: name of the team for the drive permissions; serves
            aesthetic purposes only
        :param drive_id: id of the Google Drive object to share
        :param emails: a list of emails to share with
        :param bool delete_permissions: option whether we delete the old
            permissions in favour of the new emails (previously added emails
            would be removed if they aren't in the `emails` parameter)
        """

        # List existing permissions - we use this to avoid duplicate
        # permissions, and to delete ones that should not longer exist.
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#list # noqa
        existing: List[str] = []  # emails
        to_delete: List[str] = []  # permission IDs
        try:
            # pylint: disable=no-member
            list_res = self.drive.permissions()\
                .list(fileId=drive_id,
                      supportsAllDrives=True,
                      fields="permissions(id, emailAddress, role)")\
                .execute()
            permissions: List[Any] = list_res['permissions']
            logging.info(
                f'{team_name} drive currently shared with {permissions}')
            for p in permissions:
                if 'emailAddress' in p:
                    email: str = p['emailAddress']
                    if email in emails:
                        # track permission we do not need to recreate
                        existing.append(email)
                    elif email == self.subject:
                        # do not remove actor from shared
                        continue
                    else:
                        # delete unknown emails
                        to_delete.append(p['id'])
        except Exception as e:
            logging.error("Failed to load permissions for drive item"
                          + f"({team_name}, {drive_id}): {e}")

        logging.info(f"Found {len(existing)} permissions for {team_name} "
                     + "that do not require updating")

        # Ensure the folder is shared with everyone as required.
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#create # noqa
        created_shares = 0
        for email in emails:
            if email in existing:
                continue

            body = new_create_permission_body(email)
            try:
                # pylint: disable=no-member
                self.drive.permissions()\
                    .create(fileId=drive_id,
                            body=body,
                            emailMessage=new_share_message(team_name),
                            sendNotificationEmail=True,
                            supportsAllDrives=True)\
                    .execute()
                created_shares += 1
            except Exception as e:
                logging.error("Failed to share drive item"
                              + f"({team_name}, {drive_id}) with {email}: {e}")
        logging.info(f"Created {created_shares} permissions for {team_name}")

        # Delete old permissions
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#delete # noqa
        if delete_permissions is True:
            deleted_shares = 0
            for p_id in to_delete:
                try:
                    self.drive.permissions()\
                        .delete(fileId=drive_id,
                                permissionId=p_id,
                                supportsAllDrives=True)\
                        .execute()
                    deleted_shares += 1
                except Exception as e:
                    logging.error(
                        f'Failed to delete permission {p_id} for '
                        + f'drive item ({team_name}, {drive_id}): {e}')
            logging.info(
                f'Deleted {deleted_shares} permissions for {team_name}')
        else:
            logging.info("DELETE_OLD_DRIVE_PERMISSIONS is set to false")


def new_share_message(team_name):
    return f"Rocket has shared a folder with you for team '{team_name}'!"


def new_create_permission_body(email):
    return {
        "emailAddress": email,
        "role": "writer",
        "type": "user",
        "sendNotificationEmail": True,
        "supportsAllDrives": True,
    }
