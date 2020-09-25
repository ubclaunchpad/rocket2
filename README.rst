🚀 Rocket 2
===========

|codecov| |Deployed with Inertia| |Documentation Status|

Rocket 2 is a from-the-ground-up rebuild of
`Rocket <https://github.com/ubclaunchpad/rocket>`__, UBC Launch Pad’s
in-house management Slack bot.

Developer Installation
----------------------

We use `pipenv <https://pipenv.readthedocs.io/en/latest/>`__ for
dependency management.

.. code:: bash

   git clone https://github.com/ubclaunchpad/rocket2.git
   cd rocket2/
   pip install pipenv
   pipenv install --dev

``pipenv`` will manage a
`virtualenv <https://virtualenv.pypa.io/en/stable/>`__, so interacting
with the program or using the development tools has to be done through
pipenv, like so:

.. code:: bash

   pipenv run pycodestyle .

This can get inconvenient, so you can instead create a shell that runs
in the managed environment like so:

.. code:: bash

   pipenv shell

and then commands like ``pycodestyle`` and ``pytest`` can be run like
normal.

Additionally, we use Github Actions as a CI system. To run the same
checks locally, we provide ``scripts/build_check.sh``; this can be run
with:

.. code:: bash

   ./scripts/build_check.sh

The above tests would be run with the assumption that other
applications, such as a local instance of DynamoDB, is also running. To
run tests that explicitly do **not** involve the running of any
database, run pytest with the following arguments:

.. code:: bash

   pytest -m "not db"

You can also install it as a `pre-commit
hook <https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks>`__ for
git:

.. code:: bash

   cd scripts/
   make install

Note that testing alongside a real Slack workspace, DynamoDB, and so on
requires quite a bit more setup. For a full guide to developer
installation, see our `local development
guide <https://rocket2.readthedocs.io/en/latest/docs/LocalDevelopmentGuide.html>`__.

Running DynamoDB Locally
~~~~~~~~~~~~~~~~~~~~~~~~

Some tests assume the existence of a local DynamoDB database. These are
primarily for automated testing, like on Github Actions CI, but if you
would like to run them yourself or are developing new tests, you can run
as follows:

.. code:: bash

   wget https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz
   mkdir DynamoDB
   tar -xvf dynamodb_local_latest.tar.gz --directory DynamoDB

   # Configure AWS
   scripts/setup_localaws.sh

   # Run DynamoDB through Java
   cd DynamoDB/
   java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
   # Open a new terminal to continue interacting

For a more sandboxed approach, you can use Docker and docker-compose to
spin up a local DynamoDB instance:

.. code:: bash

   docker-compose -f sandbox.yml up

You can then point a Rocket instance at this DynamoDB database by
setting ``AWS_LOCAL=True``.

.. |codecov| image:: https://codecov.io/gh/ubclaunchpad/rocket2/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/ubclaunchpad/rocket2
.. |Deployed with Inertia| image:: https://img.shields.io/badge/deploying%20with-inertia-blue.svg
   :target: https://github.com/ubclaunchpad/inertia
.. |Documentation Status| image:: https://readthedocs.org/projects/rocket2/badge/?version=latest
   :target: https://rocket2.readthedocs.io/en/latest/?badge=latest
