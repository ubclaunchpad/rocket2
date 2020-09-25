The Configuration System
========================

We use environmental variables for all of our configuration-related
things. A sample ``.env`` file (which is what ``pipenv`` looks for when
it tries to launch) can be found at ``sample-env``. Here is how each
variable works. **Note: all variables are strings**.

For variables that require newlines (such as signing keys), replace the
newlines with ``\n``. You can use the following command on most systems
to generate such a string:

.. code:: bash

   awk '{printf "%s\\n", $0}' $FILE

For JSON variables, you can just remove the newlines:

.. code:: bash

   awk '{printf "%s", $0}' $FILE

SLACK_SIGNING_SECRET
--------------------

Signing secret of the slack app. Can be found in the basic information
tab of your slack app (api.slack.com/apps).

SLACK_API_TOKEN
---------------

The Slack API token of your Slack bot. Can be found under OAuth &
Permissions tab of your slack app (under the name “Bot user OAuth access
token”).

The following permission scopes are required:

-  ``channels:read``
-  ``channels:manage``
-  ``chats:write``
-  ``users.profile:read``
-  ``users:read``
-  ``commands``
-  ``groups:read``
-  ``im:write``

You must also configure a slash command integration as well (under
“Slash commands”) for the URL path ``/slack/commands`` of your Rocket
instance.

SLACK_NOFICIATION_CHANNEL
-------------------------

Name of the channel you want to have our rocket 2 slack bot to make
service notifications in.

SLACK_ANNOUNCEMENT_CHANNEL
--------------------------

Name of the channel you want to have our rocket 2 slack bot to make
announcements in.

GITHUB_APP_ID
-------------

The ID of your Github app (found under your Github organization settings
-> Developer Settings -> Github Apps -> Edit).

GITHUB_ORG_NAME
---------------

The name of your Github organization (the string in the URL whenever you
go to the organization.

GITHUB_WEBHOOK_ENDPT
--------------------

The path GitHub posts webhooks to. Note that the following events must
be enabled (configured in GitHub app settings > “Permissions & events” >
“Subscribe to events”):

-  Membership
-  Organization
-  Team
-  Team add

When configuring webhooks, provide the URL path ``/slack/commands`` of
your Rocket instance.

GITHUB_WEBHOOK_SECRET
---------------------

A random string of characters you provide to Github to help further
obfuscate and verify that the webhook is indeed coming from Github.

GITHUB_KEY
----------

The Github app signing key (can be found under Github organization
settings -> Developer Settings -> Github Apps -> Edit (at the bottom you
generate and download the key)). Paste the contents of the file as a
string. See `deployment <Deployment.html#github-key>`__ for
troubleshooting.

The following permissions must be set to “Read & Write” for the
associated GitHub app (configured in GitHub app settings > “Permissions
& events” > “Organization permissions”):

-  Organization members

AWS_ACCESS_KEYID
----------------

The AWS access key id.

AWS_SECRET_KEY
--------------

The AWS secret key.

AWS_*_TABLE
-----------

The names of the various tables (leave these as they are).

AWS_REGION
----------

The region where the AWS instance is located (leave these as they are).

AWS_LOCAL
---------

Point all AWS DynamoDB requests to ``http://localhost:8000``. Optional,
and defaults to ``False``.
