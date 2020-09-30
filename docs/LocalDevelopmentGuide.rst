Local Development Guide
=======================

So, you want to see some progress, preferably on Slack, and not just in
the forms of unit testing? At this point, fear is actually a reasonable
response. With this guide, you can be talking to your locally-hosted
Slack bot in no time!

   **Warning**: This only works smoothly with a Unix machine (macOS or
   Linux variants). Windows users may be in for more pain than expected.

0. Developer Installation
-------------------------

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

1: Set up a HTTPS Tunnel
------------------------

Slack requires that all webhooks are passed through HTTPS. This is
rather inconvenient if you just want to test while running on your local
computer. There are several ways to get around this.

Ngrok
~~~~~

Ngrok is a forwarding service that hosts a public HTTPS URL that passes
to your local computer. Sign up for ngrok and download it
`here <https://ngrok.com/>`__.

After installing, run ``ngrok http 5000`` to create an ngrok URL that
will be passed to your local port 5000. As long as you run Rocket on
port 5000 (see below), you can then access it through the HTTPS URL that
ngrok gives you. Note that it is very important to use the HTTPS URL,
*not* the HTTP URL.

Localtunnel
~~~~~~~~~~~

An alternative to Ngrok is
`localtunnel <https://GitHub.com/localtunnel/localtunnel>`__, which
works similarly to Ngrok but allows you to use the same domain every
time. For example:

.. code:: bash

   $ lt --port 5000 --subdomain my-amazing-rocket2
   your url is: https://my-amazing-rocket2.loca.lt

2: Create a Slack Workspace
---------------------------

For testing, it’s useful to have your own Slack workspace set up. If you
do not already have one, go `here <https://slack.com/create>`__ to
create one, and follow the steps to set it up.

3: Create a Slack App
---------------------

Follow the link `here <https://api.slack.com/apps>`__ to create a new
Slack app - you can name it whatever you like - and install it to the
appropriate workspace.

3.1: Add a Bot Token
~~~~~~~~~~~~~~~~~~~~

In “OAuth and Permissions”, select the Bot Token Scopes described in
`the Slack configuration docs <slack-configuration>`__.

3.2: Install Slack App
~~~~~~~~~~~~~~~~~~~~~~

In “Install your app to your workspace,” click the button to install to
your workspace. This will take you to a permissions page for the
workspace - make sure this is for the correct workspace, and allow the
app to connect.

Once this is done, you will be provided with an API token.

3.3: Determine Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~

Make note of the app’s signing secret, found in Settings -> Basic
Information -> App Credentials, and the bot user OAuth access token,
found in Features -> OAuth & Permissions -> Tokens for Your Workspace.
These will be needed for the configuration step later.

4: Gain Access to AWS
---------------------

Rocket makes use of AWS DynamoDB as its database. There is also an
optional logging component that leverages AWS CloudWatch.

Using Real AWS
~~~~~~~~~~~~~~

If you do not already have access to DynamoDB and CloudWatch, you can
use it as part of the free tier of AWS. Create an AWS account for
yourself, then go to the IAM service and create a new user. The user
name doesn’t particularly matter (though ``rocket2-dev-$NAME`` is
recommended), but make sure you check “programmatic access.” In
permissions, go to “Attach existing permissions directly” and add the
following policies:

-  ``AmazonDynamoDBFullAccess``
-  ``CloudWatchLogsFullAccess``
-  ``CloudWatchPutMetricData``

You will have to create ``CloudWatchPutMetricData``. You can do this by going
to IAM -> Policies -> Create Policy. Choose service ``CloudWatch``. Choose
action ``PutMetricData``. Everything else should be set correctly - you can
create the policy with that.

As you may have noticed, we not only want to use DynamoDB, but also
CloudWatch. We send our logs to CloudWatch for easier storage and
querying. We also use it to track metrics.

Finally, copy the provided access key ID and secret access key after
creating the new user.

Note: if you are in the ``brussel-sprouts`` GitHub team, you should
already have AWS credentials. Just ask.

Using Local AWS
~~~~~~~~~~~~~~~

Alternatively, just set up `DynamoDB
locally <#running-dynamodb-locally>`__ (the Docker-based setup
is probably the easiest) and set ``AWS_LOCAL=True``.

CloudWatch integration is not currently supported in this manner.

5: Set up a GitHub App and organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a Rocket 2 Github under an appropriate testing organization. Make
sure to install the GitHub App to the organization in addition to
registering it. All this can be done from a GitHub organization’s
Settings > GitHub Apps page.

In the GitHub app’s settings, go to “Private keys” and click “Generate a
new private key”. This will generate and allow you to download a new
secret key for Rocket 2. Save this to the ``credentials/`` directory as
``gh_signing_key.pem`` - it should already be in the PEM file format,
bracketed by:

::

   -----BEGIN RSA PRIVATE KEY-----
   ...
   -----END RSA PRIVATE KEY-----

Authenticating Rocket 2 as a GitHub App and obtaining an access token
for the GitHub API should be automated, once the signing key is
available. Refer to the `GitHub key configuration
docs <Config.md#github-key>`__ for the required permissions.

After doing this, remember to put your tunneled HTTPS URL with
``/webhook`` appended at the end into the “Webhook URL” box. Refer to
the `GitHub webhook configuration
docs <Config.md#github-webhook-endpt>`__ for the required subscriptions.

6: Set Up Configuration
-----------------------

Our repo already contains ``sample-env``, the main environmental
configuration file for the entire app, as well as the ``credentials/``
directory, where you will put credential files like the GitHub app
private key.

Please `read the configuration docs <Config.html>`__ for more details.

7: Build and Run Rocket 2
-------------------------

This section assumes you already have installed Docker. Assuming you are
in the directory containing the Dockerfile, all you need to do to build
and run is the following two commands (run from the root of your project
directory):

.. code:: bash

   scripts/docker_build.sh
   scripts/docker_run_local.sh --env-file .env

Optionally, for `local DynamoDB <#using-local-aws>`__:

.. code:: bash

   scripts/docker_run_local.sh --env-file .env --network="host"

The option
```--env-file`` <https://docs.docker.com/engine/reference/commandline/run/#set-environment-variables--e---env---env-file>`__
lets you pass in your `configuration options <Config.html>`__.

For the curious, you can take a look at the contents of the referenced
scripts above. Note that the options passed to ``-p`` in ``docker run``
tell Docker what port to run Rocket on. ``0.0.0.0`` is the IP address
(in this case, localhost), the first ``5000`` is the port exposed inside
the container, and the second ``5000`` is the port exposed outside the
container. The port exposed outside the container can be changed (for
instance, if port 5000 is already in use in your local development
environment), but in that case ensure that your tunnel is running on the
same port.

6.1: [Optional] Running without Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We highly recommend building and running on Docker, but building every
time you make a tiny change can be inconvenient. If you would like to
run without building a new Docker image every time, you can do so with
``pipenv run launch``. This is in fact the same command Docker runs, but
if you run outside Docker, you may run into errors due to unexpected
changes in your local development environment.

7: Configure Slack App Features
-------------------------------

In addition to a bot user, there are a couple other features that need
to be enabled in the Slack app once the local instance of Rocket is
running.

7.1: Add Event Subscriptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In “Add features and functionality”, add event subscriptions. In
particular, under Request URL, submit the ngrok HTTPS URL with
``/slack/events`` appended to the end. Note that ngrok will generate a
new HTTPS URL every time it runs, so you will have to repeat this step
every time you launch ngrok. You will then have to enable workspace
and/or bot events that we want Rocket to listen for, like the
``team_join`` workspace event - ask the team for the most up-to-date
list of these.

7.2: Add Slash Command
~~~~~~~~~~~~~~~~~~~~~~

In “Add features and functionality”, add a slash command. In particular,
under Request URL, submit the ngrok HTTPS URL with ``/slack/commands``
appended to the end. For the actual command, anything will work, though
the final app will use ``/rocket``. Make sure you tick the box marked
“Escape channels, users, and links sent to your app”, or else none of
the @ signs will work properly!

8: Testing
----------

This is the final and most important part: testing if it actually works
or not. Go to your Slack workspace and add Rocket (or whatever you named
your Slack bot) to the channel if you have yet to do so (just type
``@<bot name>`` and Slack will ask if you want to invite the bot into
the channel).

To test if Rocket is running, type the command:

::

   /rocket user help

If you see a list of options, Rocket is working!

8.1: Setting Up Admin Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We currently haven’t finished the command to add a user to the database
or make them an admin, so we have to do it manually.

First, determine your Slack ID by reading the logs. The logs are
formatted like so:

::

   {slackid_making_the_command}:{command_itself}

The Slack IDs of other users will appear when you type ``@`` followed by
whatever the user’s handle is. Slack automatically converts that handle
into an ID.

Then, you have an option of either using the AWS command-line interface
or using the AWS web interface.

You should already have the command line interface installed via pipenv.
If not, run the command ``pipenv install --dev``. Note that to run
commands, you will either have to go into the pipenv environment (with
``pipenv shell``) or prefix every command with ``pipenv run``. Here is
the command to create a user with a:

.. code:: bash

   # The following command is split into multiple lines because it is long. Make
   # sure that the actal command isn't split into multiple lines because it may
   # complicate things.
   aws dynamodb put-item --table-name USERS_TABLE\
                         --item '{"slack_id":{"S": "UE7PAG75L"},
                                  "permission_level":{"S": "admin"}}'\
                         --endpoint-url http://localhost:8000

Replace ``USERS_TABLE`` with whatever name you set in ``config.toml``.

Alternatively, you can directly edit the DynamoDB table via the AWS web
interface. Go to the DynamoDB service in the AWS web interface and open
the appropriate table. Click on the Items tab and then on “Create item”.
Make sure there’s a column for ``slack_id`` and ``permission_level``,
where ``slack_id`` is a ``String`` with the appropriate value and
``permission_level`` is a ``String`` with the value ``admin``.

8.2: Viewing a User
~~~~~~~~~~~~~~~~~~~

::

   /rocket user view

The output of this command should be a stylish table displaying your
Slack id and permissions level.

Now, you can continue with whatever testing you originally wanted to do.
Remember to rebulid your Docker image every time you make a change!
