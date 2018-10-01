# 🚀 Rocket 2.0

Rocket 2.0 is a from-the-ground-up rebuild of [Rocket](https://github.com/ubclaunchpad/rocket),
UBC Launch Pad's in-house management Slack bot.

## Developer Installation

We use [`pipenv`](https://pipenv.readthedocs.io/en/latest/) for dependency management.

```bash
git clone https://github.com/ubclaunchpad/rocket2.0.git
cd rocket2.0/
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