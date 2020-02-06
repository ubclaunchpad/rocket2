# The Configuration System

We use environmental variables for all of our configuration-related things. A
sample `.env` file (which is what `pipenv` looks for when it tries to launch)
can be found at `sample-env`. Here is how each variable works. **Note: all
variables are strings**

## SLACK\_SIGNING\_SECRET

Signing secret of the slack app. Can be found in the basic information tab of
your slack app (api.slack.com/apps).

## SLACK\_API\_TOKEN

The slack api token of your slack bot. Can be found under OAuth & Permissions
tab of your slack app (under the name "Bot user OAuth access token").

## SLACK\_NOFICIATION\_CHANNEL

Name of the channel you want to have our rocket 2 slack bot to make
service notifications in.

## SLACK\_ANNOUNCEMENT\_CHANNEL

Name of the channel you want to have our rocket 2 slack bot to make
announcements in.

## GITHUB\_APP\_ID

The id of your Github app (found under your Github organization settings ->
Developer Settings -> Github Apps -> Edit).

## GITHUB\_ORG\_NAME

The name of your Github organization (the string in the URL whenever you go to
the organization.

## GITHUB\_WEBHOOK\_ENDPT

The path Github posts webhooks to.

## GITHUB\_WEBHOOK\_SECRET

A random string of characters you provide to Github to help further obfuscate
and verify that the webhook is indeed coming from Github.

## GITHUB\_KEY

The Github app signing key (can be found under Github organization settings ->
Developer Settings -> Github Apps -> Edit (at the bottom you generate and
download the key)). Paste the contents of the file as a string. See
[deployment](Deployment.html#github-key) for troubleshooting.

## AWS\_ACCESS\_KEYID

The AWS access key id.

## AWS\_SECRET\_KEY

The AWS secret key.

## AWS\_\*\_TABLE

The names of the various tables (leave these as they are).

## AWS\_REGION

The region where the AWS instance is located (leave these as they are).

## AWS\_LOCAL

Point all AWS DynamoDB requests to `http://localhost:8000`. Optional, and
defaults to `False`.
