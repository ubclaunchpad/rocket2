"""Utility classes for interacting with Google APIs"""
from typing import List, Iterator
from googleapiclient.discovery import Resource
import logging


class GCPDrivePermission:
    """Represents a 'share' on a Google Drive item."""

    def __init__(self, id: str, email: str):
        self.id = id
        self.email = standardize_email(email)


class GCPInterface:
    """Utility class for calling Google Cloud Platform (GCP) APIs."""

    def __init__(self, drive_client: Resource, subject=None):
        logging.info("Initializing Google client interface")
        self.drive = drive_client
        self.subject = subject

    def get_drive_parents(self, drive_id: str) -> List[str]:
        """
        Retrieves list of parents of the given Drive folder, returned as ID
        strings.
        """
        # pylint: disable=no-member
        file = self.drive.files()\
            .get(fileId=drive_id, fields="parents")\
            .execute()
        if 'parents' in file:
            parents: List[str] = file['parents']
            if len(parents) > 0:
                return parents
        return []

    def get_drive_permissions(self, drive_id: str) -> List[GCPDrivePermission]:
        """
        Retrieves list of permissions present on the given Drive item. It
        pages through all results and returns a subset of permission fields,
        as defined in :class:`GCPDrivePermission`.
        """
        fields = [
            "permissions/id",
            "permissions/emailAddress",
        ]

        def paginated_permissions() -> Iterator[GCPDrivePermission]:
            # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#list # noqa
            # pylint: disable=no-member
            req = self.drive.permissions()\
                .list(fileId=drive_id,
                      fields=', '.join(fields))
            while req is not None:
                resp = req.execute()
                for p in resp['permissions']:
                    if 'emailAddress' in p:
                        perm = GCPDrivePermission(p['id'], p['emailAddress'])
                        yield perm
                # see https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#list_next # noqa
                # pylint: disable=no-member
                req = self.drive.permissions().list_next(req, resp)

        # collect all permissions for this drive
        perms = [p for p in paginated_permissions()]
        logging.info(f"Found {len(perms)} permissions for {drive_id}")
        return perms

    def get_parents_permissions(self,
                                drive_id: str) -> List[GCPDrivePermission]:
        """
        Retrieves list of permissions associated with one level of parents to
        the given Drive.
        """
        parents = self.get_drive_parents(drive_id)
        perms: List[GCPDrivePermission] = []
        for parent_id in parents:
            parent_perms = self.get_drive_permissions(parent_id)
            for p in parent_perms:
                perms.append(p)
        return perms

    def ensure_drive_permissions(self,
                                 team_name: str,
                                 drive_id: str,
                                 emails: List[str]):
        """
        Create permissions for the given emails on the given Drive item, and
        removes everyone not on the list, to ensure the state of shares on the
        Drive item matches the email list provided.

        It respects permissions inherited by one level of parents of the given
        Drive item - permissions inherited from two levels of parents are at
        risk of being deleted if the user is not on the provided email list.

        In all cases of API errors, we log and continue, to try and get as
        close to the desired state of permissions as possible.

        :param team_name: name of the team for the drive permissions; serves
            aesthetic purposes only
        :param drive_id: id of the Google Drive object to share
        :param emails: a list of emails to share with
        """
        # Get parents so that we do not remove or duplicate inherited shares.
        inherited: List[str] = []  # emails
        try:
            parents_perms = self.get_parents_permissions(drive_id)
            inherited = [p.email for p in parents_perms]
        except Exception as e:
            logging.warning("Unable to fetch parents for drive item"
                            + f"({team_name}, {drive_id}): {e}")

        # Collect existing permissions and determine which emails to delete.
        existing: List[str] = []   # emails
        to_delete: List[GCPDrivePermission] = []
        try:
            perms = self.get_drive_permissions(drive_id)
            for p in perms:
                if p.email in emails:
                    # keep shares that should exist
                    existing.append(p.email)
                elif p.email == self.subject:
                    # do not remove actor from shared (actor needs permissions
                    # on this Drive item to perform a share)
                    continue
                elif p.email in inherited:
                    # do not remove inherited permissions
                    continue
                else:
                    # delete unknown permissions
                    to_delete.append(p)
        except Exception as e:
            logging.error("Failed to load permissions for drive item"
                          + f"({team_name}, {drive_id}): {e}")
        logging.info(f"Found {len(existing)} permissions for {team_name} "
                     + "that do not require updating")

        # Ensure the folder is shared with everyone as required.
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#create # noqa
        created_shares = []
        for email in emails:
            # Do not re-share (causes email spam)
            if email in existing or email in inherited:
                continue

            body = new_create_permission_body(email)
            try:
                # pylint: disable=no-member
                self.drive.permissions()\
                    .create(fileId=drive_id,
                            body=body,
                            emailMessage=new_share_message(team_name),
                            sendNotificationEmail=True)\
                    .execute()
                created_shares.append(email)
            except Exception as e:
                logging.error("Failed to share drive item"
                              + f"({team_name}, {drive_id}) with {email}: {e}")
        logging.info(f"Created {len(created_shares)} permissions for "
                     + f"{team_name} ({', '.join(created_shares)})")

        # Delete unknown permissions
        # See http://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.permissions.html#delete # noqa
        deleted_shares = []
        for perm in to_delete:
            try:
                self.drive.permissions()\
                    .delete(fileId=drive_id,
                            permissionId=perm.id)\
                    .execute()
                deleted_shares.append(perm.email)
            except Exception as e:
                logging.error(
                    f'Failed to delete permission {perm.id} for '
                    + f'drive item ({team_name}, {drive_id}): {e}')
        logging.info(f"Deleted {len(deleted_shares)} permissions for "
                     + f"{team_name} ({', '.join(deleted_shares)})")


def new_share_message(team_name):
    return f"Rocket has shared a folder with you for team '{team_name}'!"


def new_create_permission_body(email):
    return {
        "emailAddress": email,
        "role": "writer",
        "type": "user",
        "sendNotificationEmail": True,
    }


def standardize_email(email: str) -> str:
    """
    Standardize email by:

    * lowercasing: https://stackoverflow.com/questions/9807909/are-email-addresses-case-sensitive # noqa
    * removing dots: https://support.google.com/mail/answer/7436150?hl=en#:~:text=If%20someone%20accidentally%20adds%20dots,john.smith%40gmail.com # noqa
    """
    split = email.split('@')
    if len(split) != 2:
        raise Exception(f'malformed email: split on @ has {len(split)} parts')
    return f'{split[0].lower().replace(".", "")}@{split[1].lower()}'
