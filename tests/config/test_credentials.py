"""Test the loading of credentials."""
import pytest
from config.credentials import Credentials, MissingCredentialsError


@pytest.fixture
def complete_credentials():
    """Return a credentials object with complete attributes."""
    return Credentials('tests/credentials/complete')


def test_load_slack_signing_secret(complete_credentials):
    """Assert that the slack signing secret can be loaded correctly."""
    assert complete_credentials.slack_signing_secret == "signing_secret"


def test_load_slack_api_token(complete_credentials):
    """Assert that the slack api token can be loaded correctly."""
    assert complete_credentials.slack_api_token == 'api_token'


def test_load_aws_access_key_id(complete_credentials):
    """Assert that the aws access key id can be loaded correctly."""
    assert complete_credentials.aws_access_key_id == 'access_key_id'


def test_load_aws_secret_access_key(complete_credentials):
    """Assert that the aws secret access key can be loaded correctly."""
    assert complete_credentials.aws_secret_access_key == 'secret_access_key'


def test_load_github_signing_key_path(complete_credentials):
    """Assert that the github signing key path can be loaded correctly."""
    assert complete_credentials.github_signing_key_path == \
        'tests/credentials/complete/github_signing_key.pem'


def test_exception_raised_on_missing_fields():
    """Assert that loading files without proper fields raises an exception."""
    with pytest.raises(MissingCredentialsError):
        Credentials('tests/credentials/missing_fields/')
