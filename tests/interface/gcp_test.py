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

    def test_ensure_drive_permissions(self):
        # Mocks for files
        mock_files_get = mock.MagicMock()
        mock_files_get.execute = mock.MagicMock(return_value={
            "parents": [
                "parent-drive",
            ]
        })

        mock_files = mock.MagicMock()
        mock_files.get = mock.MagicMock(return_value=mock_files_get)

        # Mocks for permissions
        mock_perms_list_parent = mock.MagicMock()
        mock_perms_list_parent.execute = mock.MagicMock(return_value={
            "permissions": [
                {
                    # should not be removed (inherited)
                    "id": "99",
                    "emailAddress": "inherited-permission@ubclaunchpad.com",
                },
            ]
        })
        mock_perms_list_target = mock.MagicMock()
        mock_perms_list_target.execute = mock.MagicMock(return_value={
            "permissions": [
                {
                    # should not be removed or created (exists in email list)
                    "id": "1",
                    "emailAddress": "not-team@ubclaunchpad.com",
                },
                {
                    # should be removed (does not exist in email list)
                    "id": "2",
                    "emailAddress": "strategy@ubclaunchpad.com",
                },
                {
                    # should not be removed (actor)
                    "id": "3",
                    "emailAddress": "team@ubclaunchpad.com",
                },
                {
                    # should not be removed (inherited)
                    "id": "99",
                    "emailAddress": "inherited-permission@ubclaunchpad.com",
                },
            ]
        })
        mock_perms_create = mock.MagicMock()
        mock_perms_create.execute = mock.MagicMock(return_value={})
        mock_perms_delete = mock.MagicMock()
        mock_perms_delete.execute = mock.MagicMock(return_value={})

        def perms_list_effect(**kwargs):
            if kwargs['fileId'] == 'target-drive':
                return mock_perms_list_target
            if kwargs['fileId'] == 'parent-drive':
                return mock_perms_list_parent

        mock_perms = mock.MagicMock()
        mock_perms.list = mock.MagicMock(side_effect=perms_list_effect)
        mock_perms.list_next = mock.MagicMock(return_value=None)
        mock_perms.create = mock.MagicMock(return_value=mock_perms_create)
        mock_perms.delete = mock.MagicMock(return_value=mock_perms_delete)

        # Create Google Drive API
        self.mock_drive.files = mock.MagicMock(return_value=mock_files)
        self.mock_drive.permissions = mock.MagicMock(return_value=mock_perms)
        self.gcp.ensure_drive_permissions('team', 'target-drive', [
            'robert@bobheadxi.dev',
            'not-team@ubclaunchpad.com',
        ])

        # initial parent search
        mock_files.get.assert_called_with(fileId='target-drive',
                                          fields=mock.ANY)
        mock_files_get.execute.assert_called()
        # perms listing
        mock_perms.list.assert_has_calls([
            mock.call(fileId='parent-drive',
                      fields=mock.ANY, pageSize=mock.ANY),
            mock.call(fileId='target-drive',
                      fields=mock.ANY, pageSize=mock.ANY),
        ])
        mock_perms_list_parent.execute.assert_called()
        mock_perms_list_target.execute.assert_called()
        # one email already exists, share to the new one
        mock_perms.create\
            .assert_called_with(fileId='target-drive',
                                body=new_create_permission_body(
                                    'robert@bobheadxi.dev'),
                                emailMessage=new_share_message('team'),
                                sendNotificationEmail=True)
        mock_perms_create.execute.assert_called()
        # one email should no longer be shared, it is removed
        mock_perms.delete.assert_called_with(
            fileId='target-drive', permissionId='2')
        mock_perms_delete.execute.assert_called()
