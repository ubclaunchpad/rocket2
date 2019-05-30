#!/usr/bin/bash

# First, we try to get as much information as possible from `config.toml`
CONF="config.toml"
if [[ ! -e "$CONF" ]]; then
    echo "Cannot find 'config.toml'. Exiting."
    exit 1
fi

problems=0
CREDS=$(grep creds_path "$CONF" | cut -d ' ' -f 3 | tr -d '"')
SIGNING=$(grep signing_key_path "$CONF" | cut -d ' ' -f 3 | tr -d '"')
declare -A FILESCHANGED         # We use a map as a set

# Check to see if the credentials directory exists, and make it if not.
# We don't count this as a problem; if the user does not have the directory in
# place, there are bigger problems with their directory structures anyway.
if [[ ! -d "$CREDS" ]]; then
    mkdir "$CREDS"
fi

# Check to see if the variables are there, and insert them if not
# ------------- AWS.TOML
if ! grep -sq access_key_id "$CREDS/aws.toml"; then
    echo 'access_key_id = "YOUR_KEY_ID"' >> "$CREDS/aws.toml"
    FILESCHANGED["$CREDS/aws.toml"]=1
    ((problems++))
fi
if ! grep -sq secret_access_key "$CREDS/aws.toml"; then
    echo 'secret_access_key = "YOUR_SECRET_KEY"' >> "$CREDS/aws.toml"
    FILESCHANGED["$CREDS/aws.toml"]=1
    ((problems++))
fi
# ------------- GITHUB.TOML
if ! grep -sq app_id "$CREDS/github.toml"; then
    echo 'app_id = -1' >> "$CREDS/github.toml"
    FILESCHANGED["$CREDS/github.toml"]=1
    ((problems++))
fi
if ! grep -sq organization "$CREDS/github.toml"; then
    echo 'organization = "YOUR_ORGANIZATION"' >> "$CREDS/github.toml"
    FILESCHANGED["$CREDS/github.toml"]=1
    ((problems++))
fi
if ! grep -sq webhook_secret "$CREDS/github.toml"; then
    echo 'webhook_secret = "NANI DA HECK"' >> "$CREDS/github.toml"
    FILESCHANGED["$CREDS/github.toml"]=1
    ((problems++))
fi
# ------------- SLACK.TOML
if ! grep -sq signing_secret "$CREDS/slack.toml"; then
    echo 'signing_secret = "SECRET SIGN"' >> "$CREDS/slack.toml"
    FILESCHANGED["$CREDS/slack.toml"]=1
    ((problems++))
fi
if ! grep -sq api_token "$CREDS/slack.toml"; then
    echo 'api_token = "API TOKEN"' >> "$CREDS/slack.toml"
    FILESCHANGED["$CREDS/slack.toml"]=1
    ((problems++))
fi
# ------------- SIGNING_KEY
if [[ ! -e "$SIGNING" ]]; then
    touch "$SIGNING"
    FILESCHANGED["$SIGNING"]=1
    ((problems++))
fi

if [[ "$problems" -eq "0" ]]; then
    echo "We found no problems with your credentials."
    echo "No missing fields or files."
else
    echo "We found $problems issues in your credentials."
    echo "We added the required fields and files."
    echo ""
    echo "Below are a list of files that were changed."
    echo ""
    for key in "${!FILESCHANGED[@]}"; do
        printf "\t%s\n" "$key"
    done
fi
