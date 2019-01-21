# 🚀 Rocket 2

[![Build Status](https://travis-ci.org/ubclaunchpad/rocket2.svg?branch=master)](https://travis-ci.org/ubclaunchpad/rocket2)
[![codecov](https://codecov.io/gh/ubclaunchpad/rocket2/branch/master/graph/badge.svg)](https://codecov.io/gh/ubclaunchpad/rocket2)
[![Deployed with Inertia](https://img.shields.io/badge/deploying%20with-inertia-blue.svg)](https://github.com/ubclaunchpad/inertia)
[![Documentation Status](https://readthedocs.org/projects/rocket2/badge/?version=latest)](https://rocket2.readthedocs.io/en/latest/?badge=latest)

Rocket 2 is a from-the-ground-up rebuild of [Rocket](https://github.com/ubclaunchpad/rocket),
UBC Launch Pad's in-house management Slack bot.

## Developer Installation

We use [pipenv](https://pipenv.readthedocs.io/en/latest/) for dependency management.

```bash
git clone https://github.com/ubclaunchpad/rocket2.git
cd rocket2/
pip install pipenv
pipenv install --dev
```

`pipenv` will manage a [virtualenv](https://virtualenv.pypa.io/en/stable/),
so interacting with the program or using the development tools has to be done
through pipenv, like so:

```bash
pipenv run pycodestyle .
```

This can get inconvenient, so you can instead create a shell that runs in the managed
environment like so:

```bash
pipenv shell
```

and then commands like `pycodestyle` and `pytest` can be run like normal.

Additionally, we use [Travis CI](https://travis-ci.org/ubclaunchpad/rocket2) as
a CI system. To run the same checks locally, we provide `scripts/build_check.sh`;
this can be run with:

```bash
./scripts/build_check.sh
```

The above tests would be run with the assumption that other applications, such
as a local instance of DynamoDB, is also running. To run tests that explicitly do
**not** involve the running of any database, run pytest with the following arguments:

```bash
pytest -m "not db"
```

You can also install it as a
[pre-commit hook](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) for git:

```bash
cd scripts/
make install
```

Note that testing alongside a real Slack workspace, DynamoDB, and so on requires
quite a bit more setup. For a full guide to developer installation, see our
[local development guide](https://rocket2.readthedocs.io/en/latest/docs/LocalDevelopmentGuide.html).

### Running DynamoDB Locally

Some tests assume the existence of a local DynamoDB database. These are
primarily for automated testing, like on Travis CI, but if you would like to run
them yourself or are developing new tests, you can run as follows:

```bash
wget https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz
mkdir DynamoDB
tar -xvf dynamodb_local_latest.tar.gz --directory DynamoDB

# Configure AWS
scripts/setup_localaws.sh

# Run DynamoDB through Java
cd DynamoDB/
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
# Open a new terminal to continue interacting
```
