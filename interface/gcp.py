"""Utility classes for interacting with Google APIs"""
from typing import Any, List
from googleapiclient.discovery import Resource
import logging

default_share_msg = "Rocket has shared a folder with you!"


class GCPInterface:
    """Utility class for calling Google Cloud Platform (GCP) APIs."""

    def __init__(self, drive_client: Resource):
        logging.info("Initializing Google client interface")
        self.drive = drive_client

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
            list_res = self.drive.permissions().\
                list(drive_id, supportsAllDrives=True)
            permissions: List[Any] = list_res['permissions']
            for p in permissions:
                email: str = p['emailAddress']
                if email in emails:
                    existing.append(email)
                else:
                    to_delete.append(p['id'])
        except Exception as e:
            logging.error("Failed to load permissions for drive item"
                          + f"({scope}, {drive_id}): {e}")

        # Ensure the folder is shared with everyone as required.
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#create # noqa
        for email in emails:
            if email in existing:
                continue

            body = new_create_permission_body(scope, email)
            try:
                # pylint: disable=no-member
                self.drive.permissions().create(drive_id,
                                                body=body,
                                                emailMessage=default_share_msg,
                                                sendNotificationEmail=True,
                                                supportsAllDrives=True)
            except Exception as e:
                logging.error("Failed to share drive item"
                              + f"({scope}, {drive_id}) with {email}: {e}")

        # Delete old permissions
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#delete # noqa
        for p in to_delete:
            try:
                self.drive.permissions().delete(p,
                                                supportsAllDrives=True)
            except Exception as e:
                logging.error(f"Failed to delete permission {p} for drive item"
                              + f" ({scope}, {drive_id}): {e}")


def new_create_permission_body(scope, email):
    return {
        "displayName": f"{scope} (Rocket)",
        "emailAddress": email,
        "role": "writer",
        "sendNotificationEmail": True,
        "supportsAllDrives": True,
    }
