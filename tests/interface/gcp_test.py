"""Test GCPInterface Class."""
from interface.gcp import GCPInterface, \
    new_create_permission_body, new_share_message
from googleapiclient.discovery import Resource
from unittest import mock, TestCase


class TestGCPInterface(TestCase):
    """Test Case for GCPInterface class."""

    def setUp(self):
        self.mock_drive = mock.MagicMock(Resource)
        self.gcp = GCPInterface(self.mock_drive,
                                subject="team@ubclaunchpad.com")

    def test_set_drive_permissions(self):
        mock_list = mock.MagicMock()
        mock_list.execute = mock.MagicMock(return_value={
            "permissions": [
                {
                    "id": "1",
                    "emailAddress": "not-team@ubclaunchpad.com",
                },
                {
                    "id": "2",
                    "emailAddress": "strategy@ubclaunchpad.com",
                },
                {
                    # should not be removed
                    "id": "3",
                    "emailAddress": "team@ubclaunchpad.com"
                }
            ]
        })

        mock_create = mock.MagicMock()
        mock_create.execute = mock.MagicMock(return_value={})

        mock_delete = mock.MagicMock()
        mock_delete.execute = mock.MagicMock(return_value={})

        mock_perms = mock.MagicMock()
        mock_perms.list = mock.MagicMock(return_value=mock_list)
        mock_perms.create = mock.MagicMock(return_value=mock_create)
        mock_perms.delete = mock.MagicMock(return_value=mock_delete)

        self.mock_drive.permissions = mock.MagicMock(return_value=mock_perms)
        self.gcp.set_drive_permissions('team', 'abcde', [
            'robert@bobheadxi.dev',
            'not-team@ubclaunchpad.com',
        ])

        # initial list
        mock_perms.list.assert_called()
        mock_list.execute.assert_called()
        # one email already exists, share to the new one
        mock_perms.create\
            .assert_called_with(fileId='abcde',
                                body=new_create_permission_body(
                                    'robert@bobheadxi.dev'),
                                emailMessage=new_share_message('team'),
                                sendNotificationEmail=True,
                                supportsAllDrives=True)
        mock_create.execute.assert_called()
        # one email should no longer be shared, it is removed
        mock_perms.delete.assert_called_with(
            fileId='abcde', permissionId='2', supportsAllDrives=True)
        mock_delete.execute.assert_called()
