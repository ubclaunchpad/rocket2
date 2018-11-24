#!/usr/bin/env bash
set -euxo pipefail
pipenv run pycodestyle .
pipenv run pydocstyle .
mdl .

# We use nmap to check if dynamodb is running locally
# TODO: later should combine this with environmental variable checking (to see
# if we can use a remote server instead).
# XXX: Find a better way to check if dynamodb is running locally
COV_OPTIONS="--cov=./ --cov-branch --cov-config .coverageac"
if nmap localhost | egrep "8000.*http-alt"; then
    pipenv run pytest tests/ ${COV_OPTIONS}
else
    printf "Warning: DynamoDB not detected. Running without the tests.\n"
    pipenv run pytest tests/ -m "not db" ${COV_OPTIONS}
fi
