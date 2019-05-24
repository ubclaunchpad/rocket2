#!/usr/bin/bash

# First, we try to get as much information as possible from `config.toml`
CONF="config.toml"
if [[ ! -e "$CONF" ]]; then
    echo "Cannot find 'config.toml'. Exiting."
    exit 1
fi

CREDS=$(grep creds_path "$CONF" | cut -d ' ' -f 3 | tr -d '"')

# Check to see if the variables are there, and insert them if not
# ------------- AWS.TOML
if ! grep -q access_key_id "$CREDS/aws.toml"; then
    echo 'access_key_id = "YOUR_KEY_ID"' >> "$CREDS/aws.toml"
fi
if ! grep -q secret_access_key "$CREDS/aws.toml"; then
    echo 'secret_access_key = "YOUR_SECRET_KEY"' >> "$CREDS/aws.toml"
fi
# ------------- GITHUB.TOML
if ! grep -q app_id "$CREDS/github.toml"; then
    echo 'app_id = -1' >> "$CREDS/github.toml"
fi
if ! grep -q organization "$CREDS/github.toml"; then
    echo 'organization = "YOUR_ORGANIZATION"' >> "$CREDS/github.toml"
fi
if ! grep -q webhook_secret "$CREDS/github.toml"; then
    echo 'webhook_secret = "NANI DA HECK"' >> "$CREDS/github.toml"
fi
# ------------- SLACK.TOML
if ! grep -q signing_secret "$CREDS/slack.toml"; then
    echo 'signing_secret = "SECRET SIGN"' >> "$CREDS/slack.toml"
fi
if ! grep -q api_token "$CREDS/slack.toml"; then
    echo 'api_token = "API TOKEN"' >> "$CREDS/slack.toml"
fi
