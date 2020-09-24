"""Test GCPInterface Class."""
from interface.gcp import GCPInterface, new_create_permission_body, \
    default_share_msg
from googleapiclient.discovery import Resource
from unittest import mock, TestCase


class TestGCPInterface(TestCase):
    """Test Case for GCPInterface class."""

    def setUp(self):
        self.mock_drive = mock.MagicMock(Resource)
        self.gcp = GCPInterface(self.mock_drive)

    def test_set_drive_permissions(self):
        mock_perms = mock.MagicMock()
        mock_perms.list = mock.MagicMock(return_value={
            "permissions": [
                {
                    "id": "1",
                    "emailAddress": "team@ubclaunchpad.com",
                },
                {
                    "id": "2",
                    "emailAddress": "strategy@ubclaunchpad.com",
                },
            ]
        })
        mock_perms.create = mock.MagicMock(return_value={})
        mock_perms.delete = mock.MagicMock(return_value={})
        self.mock_drive.permissions = mock.MagicMock(return_value=mock_perms)
        self.gcp.set_drive_permissions('team', 'abcde', [
            'robert@bobheadxi.dev',
            'team@ubclaunchpad.com',
        ])

        # initial list
        mock_perms.list.assert_called()
        # one email already exists, share to the new one
        mock_perms.create.assert_called_with('abcde',
                                             body=new_create_permission_body(
                                                 'team',
                                                 'robert@bobheadxi.dev'),
                                             emailMessage=default_share_msg,
                                             sendNotificationEmail=True,
                                             supportsAllDrives=True)
        # one email should no longer be shared, it is removed
        mock_perms.delete.assert_called_with('2', supportsAllDrives=True)
