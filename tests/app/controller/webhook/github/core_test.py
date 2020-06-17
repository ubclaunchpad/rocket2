"""Test the GitHub webhook handler."""
from unittest import mock, TestCase
from app.controller.webhook.github import GitHubWebhookHandler


class TestGithubWebhookCore(TestCase):
    """Test Github webhook functions."""

    def setUp(self):
        """Set up variables for testing."""
        self.config = mock.Mock()
        self.config.github_webhook_secret = ''
        self.dbf = mock.Mock()
        self.gh = mock.Mock()
        self.webhook_handler = GitHubWebhookHandler(self.dbf, self.gh,
                                                    self.config)

    @mock.patch('app.controller.webhook.github.core.hmac.new')
    def test_verify_correct_hash(self, mock_hmac_new):
        """Test that correct hash signatures can be properly verified."""
        test_signature = "signature"
        mock_hmac_new.return_value.hexdigest.return_value = test_signature
        self.assertTrue(self.webhook_handler.verify_hash(
            b'body', "sha1=" + test_signature))

    @mock.patch('app.controller.webhook.github.core.hmac.new')
    def test_verify_incorrect_hash(self, mock_hmac_new):
        """Test that incorrect hash signaures can be properly ignored."""
        test_signature = "signature"
        mock_hmac_new.return_value.hexdigest.return_value = test_signature
        self.assertFalse(self.webhook_handler.verify_hash(
            b'body', "sha1=helloworld"))

    @mock.patch('app.controller.webhook.github.'
                'core.GitHubWebhookHandler.verify_hash')
    @mock.patch('app.controller.webhook.github.'
                'core.OrganizationEventHandler.handle')
    def test_verify_and_handle_org_event(self, mock_handle_org_event,
                                         mock_verify_hash):
        """Test that the handle function can handle organization events."""
        mock_verify_hash.return_value = True
        mock_handle_org_event.return_value = ("rsp", 0)
        rsp, code =\
            self.webhook_handler.handle(None, None, {"action": "member_added"})
        self.webhook_handler.handle(None, None, {"action": "member_removed"})
        self.assertEqual(mock_handle_org_event.call_count, 2)
        self.assertEqual(rsp, 'rsp')
        self.assertEqual(code, 0)

    @mock.patch('app.controller.webhook.github.'
                'core.GitHubWebhookHandler.verify_hash')
    @mock.patch('app.controller.webhook.github.'
                'core.TeamEventHandler.handle')
    def test_verify_and_handle_team_event(self, mock_handle_team_event,
                                          mock_verify_hash):
        """Test that the handle function can handle team events."""
        mock_verify_hash.return_value = True
        mock_handle_team_event.return_value = ("rsp", 0)
        rsp, code = self.webhook_handler.handle(None, None,
                                                {"action": "created"})
        self.webhook_handler.handle(None, None,
                                    {"action": "deleted"})
        self.webhook_handler.handle(None, None,
                                    {"action": "edited"})
        self.webhook_handler.handle(None, None,
                                    {"action": "added_to_repository"})
        self.webhook_handler.handle(None, None,
                                    {"action": "removed_from_repository"})
        self.assertEqual(mock_handle_team_event.call_count, 5)
        self.assertEqual(rsp, 'rsp')
        self.assertEqual(code, 0)

    @mock.patch('app.controller.webhook.github.'
                'core.GitHubWebhookHandler.verify_hash')
    @mock.patch('app.controller.webhook.github.'
                'core.MembershipEventHandler.handle')
    def test_verify_and_handle_membership_event(self, mock_handle_mem_event,
                                                mock_verify_hash):
        """Test that the handle function can handle membership events."""
        mock_verify_hash.return_value = True
        mock_handle_mem_event.return_value = ("rsp", 0)
        rsp, code = self.webhook_handler.handle(None, None,
                                                {"action": "added"})
        self.webhook_handler.handle(None, None, {"action": "removed"})
        self.assertEqual(mock_handle_mem_event.call_count, 2)
        self.assertEqual(rsp, 'rsp')
        self.assertEqual(code, 0)

    @mock.patch('app.controller.webhook.github.'
                'core.GitHubWebhookHandler.verify_hash')
    def test_verify_and_handle_unknown_event(self, mock_verify_hash):
        """Test that the handle function can handle unknown events."""
        mock_verify_hash.return_value = True
        rsp, code = self.webhook_handler.handle(None, None, {"action": ""})
        self.assertEqual(rsp, 'Unsupported payload received')
        self.assertEqual(code, 500)

    @mock.patch('app.controller.webhook.github.'
                'core.GitHubWebhookHandler.verify_hash')
    def test_handle_unverified_event(self, mock_verify_hash):
        """Test that the handle function can handle invalid signatures."""
        mock_verify_hash.return_value = False
        rsp, code = self.webhook_handler.handle(None, None,
                                                {"action": "member_added"})
        self.assertEqual(rsp, 'Hashed signature is not valid')
        self.assertEqual(code, 403)
