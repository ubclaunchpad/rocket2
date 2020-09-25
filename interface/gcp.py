"""Utility classes for interacting with Google APIs"""
from typing import Any, List
from googleapiclient.discovery import Resource
import logging


class GCPInterface:
    """Utility class for calling Google Cloud Platform (GCP) APIs."""

    def __init__(self, drive_client: Resource, subject=None):
        logging.info("Initializing Google client interface")
        self.drive = drive_client
        self.subject = subject

    def set_drive_permissions(self, scope, drive_id, emails: List[str]):
        """
        Creates permissions for the given emails, and removes everyone not
        on the list.

        In all cases of API errors, we log and continue, to try and get close
        to the desired state of permissions.
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
            logging.info(f"{scope} drive currently shared with {permissions}")
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
                          + f"({scope}, {drive_id}): {e}")

        logging.info(f"Found {len(existing)} permissions for {scope} "
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
                            emailMessage=new_share_message(scope),
                            sendNotificationEmail=True,
                            supportsAllDrives=True)\
                    .execute()
                created_shares += 1
            except Exception as e:
                logging.error("Failed to share drive item"
                              + f"({scope}, {drive_id}) with {email}: {e}")
        logging.info(f"Created {created_shares} permissions for {scope}")

        # Delete old permissions
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#delete # noqa
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
                logging.error(f"Failed to delete permission {p_id} for drive "
                              + f"item ({scope}, {drive_id}): {e}")
        logging.info(f"Deleted {deleted_shares} permissions for {scope}")


def new_share_message(scope):
    return f"Rocket has shared a folder with you for team '{scope}'!"


def new_create_permission_body(email):
    return {
        "emailAddress": email,
        "role": "writer",
        "type": "user",
        "sendNotificationEmail": True,
        "supportsAllDrives": True,
    }
