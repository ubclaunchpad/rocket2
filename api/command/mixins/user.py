"""Encapsulate the common business logic of user commands."""
import logging
from app.model import User, Permissions
from utils.slack_parse import escape_email
from typing import cast


class UserCommandApis:
    """Encapsulate the various APIs for user command logic."""

    def __init__(self):
        """Declare the interfaces needed."""
        self._db_facade = None
        self._gh_interface = None

    def user_edit(self,
                  caller_id: str,
                  member: str = None,
                  name: str = None,
                  email: str = None,
                  pos: str = None,
                  github: str = None,
                  major: str = None,
                  bio: str = None,
                  permission: Permissions = None) -> bool:
        """
        Edit a user in the database.

        If ``member`` is not None, and the calling user is an admin, this
        function edits the user with ID ``member``. Otherwise, the calling
        user is edited.

        :param caller_id: Slack ID of the user who is calling the API
        :param member: Slack ID of the user to edit
        :param name: display name to change to for the user
        :param email: email to change to for the user
        :param pos: position to change to for the user
        :param github: Github username to change to for the user
        :param major: major to change to for the user
        :param bio: bio to change to for the user
        :param permission: permission level to change to for the user
        :raises: LookupError if the calling user or the desired user to edit
                 could not be found in the database
        :raises: PermissionError if the calling user is attempting to edit
                 another user and they are not an admin, or are trying to
                 edit their own permission level without being an admin
        :raises: GithubAPIException if setting the Github username fails to
                 add the corresponding user to the Github organization
        :return: True if user was successfully edited in the database,
                 False otherwise
        """
        logging.info("User edit command API called")

        calling_user = self._db_facade.retrieve(User, caller_id)

        is_admin = calling_user.permissions_level == Permissions.admin
        edited_user = calling_user

        if member is not None:
            if is_admin:
                edited_user = self._db_facade.retrieve(User, member)
            else:
                msg = f"Calling user with Slack ID {caller_id} has" \
                    " permission level " \
                    f"{str(calling_user.permissions_level)}, insufficient " \
                    "for editing another user!"
                logging.error(msg)
                raise PermissionError(msg)
        else:
            edited_user = calling_user

        if permission and is_admin:
            edited_user.permissions_level = cast(Permissions, permission)
        elif permission and not is_admin:
            msg = f"Calling user with Slack ID {caller_id} has permission" \
                f" level {str(calling_user.permissions_level)}, " \
                "insufficient for editing own permission level!"
            logging.error(msg)
            raise PermissionError(msg)
        if github:
            github_id = self._gh_interface.org_add_member(github)
            edited_user.github_username = github
            edited_user.github_id = github_id
        if name:
            edited_user.name = name
        if email:
            edited_user.email = escape_email(email)
        if pos:
            edited_user.position = pos
        if major:
            edited_user.major = major
        if bio:
            edited_user.biography = bio

        return cast(bool, self._db_facade.store(edited_user))

    def user_delete(self,
                    caller_id: str,
                    del_user_id: str) -> None:
        """
        Delete a user from the database.

        Delete user with ``slack_id`` if user with  ``caller_id`` has admin
        permission level.

        **Note**: users can delete themselves.

        :param caller_id: Slack ID of user who is calling the command
        :param del_user_id: Slack ID of user who is being deleted
        :raises: LookupError if the calling user or the desired user to delete
                 could not be found in the database
        :raises: PermissionError if the calling user is attempting delete edit
                 another user and they are not an admin
        """
        calling_user = self._db_facade.retrieve(User, caller_id)

        if calling_user.permissions_level == Permissions.admin:
            self._db_facade.delete(User, del_user_id)
            logging.info(f"Deleted user with Slack ID {del_user_id}")
        else:
            msg = f"Calling user with Slack ID {caller_id} has permission" \
                f" level {str(calling_user.permissions_level)}, " \
                "insufficient for deleting a user!"
            logging.error(msg)
            raise PermissionError(msg)

    def user_view(self,
                  caller_id: str,
                  view_user_id: str = None) -> User:
        """
        View user information from the database.

        If ``view_user_id`` is None, return information of ``caller_id``, else
        return information of ``view_user_id``.

        :param caller_id: Slack ID of the user who is calling the command
        :param view_user_id: Slack ID of user whose info is being retrieved
        :raises: LookupError if the calling user or the desired user to view
                 could not be found in the database
        :return: ``User`` object whose information was retrieved
        """
        user_to_view_id = caller_id if view_user_id is None else view_user_id
        return cast(User, self._db_facade.retrieve(User, user_to_view_id))

    def user_add(self,
                 add_user_id: str,
                 use_force: bool = False) -> bool:
        """
        Add a user to the database via user ID.

        :param add_user_id: Slack ID of the user to be added
        :param use_force: If this is set, we store the user even iff they are
                          already added in the database
        :raises: RuntimeError if the user has already been added and
                 ``user_force`` is False
        :return: True if the user was successfully added, False otherwise
        """
        # Try to look up and avoid overwriting if we are not using force
        if not use_force:
            try:
                self._db_facade.retrieve(User, add_user_id)
                msg = f"User with Slack ID {add_user_id} already exists"
                logging.error(msg)
                raise RuntimeError(msg)
            except LookupError:
                logging.info(f"User with Slack ID {add_user_id} "
                             "not in database")

        return cast(bool, self._db_facade.store(User(add_user_id)))
