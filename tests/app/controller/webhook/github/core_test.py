"""Test the GitHub webhook handler."""
from db import DBFacade
from unittest import mock
from app.controller.webhook.github import GitHubWebhookHandler


@mock.patch('config.Config')
@mock.patch('app.controller.webhook.github.core.hmac.new')
def test_verify_correct_hash(mock_hmac_new, config):
    """Test that correct hash signatures can be properly verified."""
    config.github_webhook_secret = ''
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, config)
    test_signature = "signature"
    mock_hmac_new.return_value.hexdigest.return_value = test_signature
    assert webhook_handler.verify_hash(b'body', "sha1=" + test_signature)


@mock.patch('config.Config')
@mock.patch('app.controller.webhook.github.core.hmac.new')
def test_verify_incorrect_hash(mock_hmac_new, config):
    """Test that incorrect hash signaures can be properly ignored."""
    config.github_webhook_secret = ''
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, config)
    test_signature = "signature"
    mock_hmac_new.return_value.hexdigest.return_value = test_signature
    assert not webhook_handler.verify_hash(b'body', "sha1=helloworld")


@mock.patch('config.Config')
@mock.patch('app.controller.webhook.github.'
            'core.GitHubWebhookHandler.verify_hash')
@mock.patch('app.controller.webhook.github.'
            'core.OrganizationEventHandler.handle')
def test_verify_and_handle_org_event(mock_handle_org_event, mock_verify_hash,
                                     config):
    """Test that the handle function can handle organization events."""
    mock_verify_hash.return_value = True
    mock_handle_org_event.return_value = ("rsp", 0)
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, config)
    rsp, code = webhook_handler.handle(None, None, {"action": "member_added"})
    webhook_handler.handle(None, None, {"action": "member_removed"})
    assert mock_handle_org_event.call_count == 2
    assert rsp == "rsp"
    assert code == 0


@mock.patch('config.Config')
@mock.patch('app.controller.webhook.github.'
            'core.GitHubWebhookHandler.verify_hash')
@mock.patch('app.controller.webhook.github.'
            'core.TeamEventHandler.handle')
def test_verify_and_handle_team_event(mock_handle_team_event,
                                      mock_verify_hash,
                                      config):
    """Test that the handle function can handle team events."""
    mock_verify_hash.return_value = True
    mock_handle_team_event.return_value = ("rsp", 0)
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, config)
    rsp, code = webhook_handler.handle(None, None, {"action": "created"})
    webhook_handler.handle(None, None, {"action": "deleted"})
    webhook_handler.handle(None, None, {"action": "edited"})
    webhook_handler.handle(None, None, {"action": "added_to_repository"})
    webhook_handler.handle(None, None, {"action": "removed_from_repository"})
    assert mock_handle_team_event.call_count == 5
    assert rsp == "rsp"
    assert code == 0


@mock.patch('config.Config')
@mock.patch('app.controller.webhook.github.'
            'core.GitHubWebhookHandler.verify_hash')
@mock.patch('app.controller.webhook.github.'
            'core.MembershipEventHandler.handle')
def test_verify_and_handle_membership_event(mock_handle_mem_event,
                                            mock_verify_hash,
                                            config):
    """Test that the handle function can handle membership events."""
    mock_verify_hash.return_value = True
    mock_handle_mem_event.return_value = ("rsp", 0)
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, config)
    rsp, code = webhook_handler.handle(None, None, {"action": "added"})
    webhook_handler.handle(None, None, {"action": "removed"})
    assert mock_handle_mem_event.call_count == 2
    assert rsp == "rsp"
    assert code == 0


@mock.patch('config.Config')
@mock.patch('app.controller.webhook.github.'
            'core.GitHubWebhookHandler.verify_hash')
def test_verify_and_handle_unknown_event(mock_verify_hash, config):
    """Test that the handle function can handle unknown events."""
    mock_verify_hash.return_value = True
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, config)
    rsp, code = webhook_handler.handle(None, None, {"action": ""})
    assert rsp == "Unsupported payload received"
    assert code == 500


@mock.patch('config.Config')
@mock.patch('app.controller.webhook.github.'
            'core.GitHubWebhookHandler.verify_hash')
def test_handle_unverified_event(mock_verify_hash, config):
    """Test that the handle function can handle invalid signatures."""
    mock_verify_hash.return_value = False
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, config)
    rsp, code = webhook_handler.handle(None, None, {"action": "member_added"})
    assert rsp == "Hashed signature is not valid"
    assert code == 403
