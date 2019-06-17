"""Test the GitHub webhook handler."""
import pytest

from db import DBFacade
from unittest import mock
from webhook.github import GitHubWebhookHandler
from config import Credentials
from tests.webhook.github.events.organization_test import \
    org_default_payload, org_add_payload, org_rm_payload, org_inv_payload
from tests.webhook.github.events.organization_test import \
    org_default_payload, org_add_payload, org_rm_payload, org_inv_payload, \
    org_empty_payload
from tests.webhook.github.events.team_test import \
    team_default_payload, team_created_payload, team_deleted_payload, \
    team_edited_payload, team_added_to_repository_payload, \
    team_rm_from_repository_payload
from tests.webhook.github.events.membership_test import \
    mem_default_payload, mem_add_payload, mem_rm_payload


@pytest.fixture
def credentials():
    """Return a credentials object with complete attributes."""
    return Credentials('tests/credentials/complete')


@mock.patch('webhook.github.core.logging')
@mock.patch('webhook.github.core.hmac.new')
def test_verify_correct_hash(mock_hmac_new, mock_logging, credentials):
    """Test that correct hash signatures can be properly verified."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, credentials)
    test_signature = "signature"
    mock_hmac_new.return_value.hexdigest.return_value = test_signature
    assert webhook_handler.verify_hash(b'body', "sha1=" + test_signature)
    mock_logging.debug.assert_called_once_with("Webhook signature verified")


@mock.patch('webhook.github.core.logging')
@mock.patch('webhook.github.core.hmac.new')
def test_verify_incorrect_hash(mock_hmac_new, mock_logging, credentials):
    """Test that incorrect hash signaures can be properly ignored."""
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, credentials)
    test_signature = "signature"
    mock_hmac_new.return_value.hexdigest.return_value = test_signature
    assert not webhook_handler.verify_hash(b'body', "sha1=helloworld")
    mock_logging.warning.assert_called_once_with(
        "Webhook not from GitHub; signature: sha1=helloworld")


@mock.patch('webhook.github.core.GitHubWebhookHandler.verify_hash')
@mock.patch('webhook.github.core.OrganizationEventHandler.handle')
def test_verify_and_handle_org_event(mock_handle_org_event, mock_verify_hash,
                                     credentials, org_add_payload,
                                     org_rm_payload, org_inv_payload):
    """Test that the handle function can handle organization events."""
    mock_verify_hash.return_value = True
    mock_handle_org_event.return_value = ("rsp", 0)
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, credentials)
    rsp, code = webhook_handler.handle(None, None, org_add_payload)
    webhook_handler.handle(None, None, org_rm_payload)
    webhook_handler.handle(None, None, org_inv_payload)
    assert mock_handle_org_event.call_count == 3
    assert rsp == "rsp"
    assert code == 0


@mock.patch('webhook.github.core.GitHubWebhookHandler.verify_hash')
@mock.patch('webhook.github.core.TeamEventHandler.handle')
def test_verify_and_handle_team_event(mock_handle_team_event, mock_verify_hash,
                                      credentials, team_created_payload,
                                      team_deleted_payload,
                                      team_edited_payload,
                                      team_added_to_repository_payload,
                                      team_rm_from_repository_payload):
    """Test that the handle function can handle team events."""
    mock_verify_hash.return_value = True
    mock_handle_team_event.return_value = ("rsp", 0)
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, credentials)
    rsp, code = webhook_handler.handle(None, None, team_created_payload)
    webhook_handler.handle(None, None, team_deleted_payload)
    webhook_handler.handle(None, None, team_edited_payload)
    webhook_handler.handle(None, None, team_added_to_repository_payload)
    webhook_handler.handle(None, None, team_rm_from_repository_payload)
    assert mock_handle_team_event.call_count == 5
    assert rsp == "rsp"
    assert code == 0


@mock.patch('webhook.github.core.GitHubWebhookHandler.verify_hash')
@mock.patch('webhook.github.core.MembershipEventHandler.handle')
def test_verify_and_handle_membership_event(mock_handle_mem_event,
                                            mock_verify_hash,
                                            credentials, mem_add_payload,
                                            mem_rm_payload):
    """Test that the handle function can handle membership events."""
    mock_verify_hash.return_value = True
    mock_handle_mem_event.return_value = ("rsp", 0)
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, credentials)
    rsp, code = webhook_handler.handle(None, None, mem_add_payload)
    webhook_handler.handle(None, None, mem_rm_payload)
    assert mock_handle_mem_event.call_count == 2
    assert rsp == "rsp"
    assert code == 0


@mock.patch('webhook.github.core.GitHubWebhookHandler.verify_hash')
def test_verify_and_handle_unknown_event(mock_verify_hash, credentials,
                                         org_empty_payload):
    """Test that the handle function can handle invalid signatures."""
    mock_verify_hash.return_value = True
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, credentials)
    rsp, code = webhook_handler.handle(None, None, org_empty_payload)
    assert rsp == "Unsupported payload received"
    assert code == 500


@mock.patch('webhook.github.core.GitHubWebhookHandler.verify_hash')
def test_handle_unverified_event(mock_verify_hash, credentials):
    """Test that the handle function can handle invalid signatures."""
    mock_verify_hash.return_value = False
    mock_facade = mock.MagicMock(DBFacade)
    webhook_handler = GitHubWebhookHandler(mock_facade, credentials)
    rsp, code = webhook_handler.handle(None, None, team_created_payload)
    assert rsp == "Hashed signature is not valid"
    assert code == 403
