Development Scripts
===================

There are a few scripts in the ``scripts/`` directory that aid in the
development of this project.

build_check.sh
--------------

.. code:: sh

   scripts/build_check.sh

This is just the list of commands run to check the code for violations
of Python style. It also runs the tests, and is the script that is run
in our Github CI. Make sure to run before submitting a pull request!

This script also checks to see if the user is running DynamoDB locally,
and if so, would include tests for it; if not, the tests that use
DynamoDB will be deselected.

See `git hooks <#makefile-for-git-hooks>`__.

port_busy.py
------------

.. code:: sh

   pipenv run python scripts/port_busy.py 8000

This is to check if a port is busy on the machine you are running on.

Used in place of ``nmap`` for automatically checking if the port used
for local instances of DynamoDB is in use.

-  Exits with 0 if the port is in use.
-  Exits with 1 if there is an issue connecting with the port you
   provided.
-  Exits with 2 if the port you provided couldn't be converted to an
   integer.
-  Exits with 3 if you didn't provide exactly 1 argument.
-  Exits with 4 if the port is not already in use.

update.sh
---------

.. code:: sh

   scripts/update.sh

This should be run whenever any change to ``Pipfile`` or
``Pipfile.lock`` occurs on your local copy of a branch. It updates any
changed dependencies into your virtual environment. This is equivalent
to the user running:

.. code:: sh

   pipenv sync --dev

Which, coincidentally, require the same number of characters to be
typed. The script should ideally be run after any instance of
``git pull``.

See `git hooks <#makefile-for-git-hooks>`__.

download_dynamodb_and_run.sh
----------------------------

.. code:: sh

   scripts/download_dynamodb_and_run.sh

This script downloads a copy of the latest local version of DynamoDB and
forks the process. It also sets up the environment in which you should
run it in using ``scripts/setup_localaws.sh``.

Please do not use this script; it is meant to be run by Github CI.
Unless you enjoy having to download and run multiple DynamoDB processes.

setup_localaws.sh
-----------------

.. code:: sh

   scripts/setup_localaws.sh

This script automatically sets up your environment to better benefit a
local instance of DynamoDB. Only should be run once by users (though
running it multiple times would not hurt too too much). It requires
``aws`` to be installed through ``pipenv``.

docker_build.sh
---------------

.. code:: sh

   scripts/docker_build.sh

This script builds a docker image ``rocket2-dev-img``, according to the
``Dockerfile``. Equivalent to:

.. code:: sh

   docker build -t rocket2-dev-img .

Make sure you have docker installed on your system beforehand.

docker_run_local.sh
-------------------

.. code:: sh

   scripts/docker_run_local.sh

This script runs a local docker image on your system, port 5000.
Equivalent to:

.. code:: sh

   docker run --rm -it -p 0.0.0.0:5000:5000 rocket2-dev-img

Make sure you have already built a ``rocket2-dev-img``, or have run
``scripts/docker_build.sh`` before-hand. ``docker`` must also be
installed.

Makefile for Git Hooks
----------------------

.. code:: sh

   cd scripts
   make

This script simply installs the pre-commit hooks and post-merge hooks.
``build_check.sh`` is copied to ``.git/hooks/pre-commit``, and
``update.sh`` is copied to ``.git/hooks/post-merge``.

After installation, every time you try to make a commit, all the tests
will be run automatically to ensure compliance. Every time you perform a
``pull`` or ``merge`` or ``rebase``, ``pipenv`` will try to sync all
packages and dependencies.

Makefile for Documentation
--------------------------

.. code:: sh

   make clean html

This script builds all documentation and places the html into
``_build/`` directory. Should mostly be used to test your documentation
locally. Should be run within a ``pipenv shell`` environment.

We use Python ``sphinx`` to generate documentation from reStructuredText
and Markdown files in this project. To configure (and change versions
for the documentation), edit ``conf.py``. ``docs/index.rst`` is the
index for all documentation.
