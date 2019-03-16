"""Pack the modules contained in the configuration directory."""
import config.credentials

Credentials = config.credentials.Credentials
MissingCredentialsError = config.credentials.MissingCredentialsError
