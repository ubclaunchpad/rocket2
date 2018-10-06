#!/usr/bin/env bash
set -euxo pipefail
pipenv run pycodestyle .
pipenv run pydocstyle .
mdl .
pipenv run pytest tests/
