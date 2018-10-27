#!/usr/bin/env bash
# AWS CLI asks for:
# - AWS Access Key ID (random key id for local db)
# - AWS Secret Access Key (random key id for local db)
# - Default region name (any region name should do; check list at
#   https://goo.gl/BcTEGn)
# - Default output format (we use json, but text or table works as well)
pipenv run aws configure << EOF
Access_Key_ID_Dont_Look
Super_Secret_Access_Key
ca-central-1
json
EOF
