#!/usr/bin/env bash
set -euxo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
pushd "${REPO_ROOT}"

pipenv run pycodestyle .
pipenv run flake8 .
pipenv run pydocstyle .
pipenv run mypy .
mdl .

# We use a script to check if dynamodb is running locally
COV_OPTIONS="--mypy --cov=./ --cov-branch --cov-config .coverageac"
PORT_CHECKER="scripts/port_busy.py"
TESTS="tests/"
PORT_BUSY="pipenv run python ${PORT_CHECKER} 8000"
if ${PORT_BUSY}; then
    printf "DynamoDB detected. Running all tests.\n"
    pipenv run pytest "${TESTS}" ${COV_OPTIONS}
else
    printf "Warning: DynamoDB not detected. Running without the tests.\n"
    pipenv run pytest "${TESTS}" -m "not db" ${COV_OPTIONS}
fi

popd
