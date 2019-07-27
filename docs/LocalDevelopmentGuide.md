# Local Development Guide

So, you want to see some progress, preferably on Slack, and not just in the
forms of unit testing? At this point, fear is actually a reasonable response.
With this guide, you can be talking to your locally-hosted Slack bot in no time!

> **Warning**: This only works smoothly with a Unix machine (macOS or Linux
> variants). Windows users may be in for more pain than expected.

## 1: Install ngrok

Slack requires that all webhooks are passed through HTTPS. This is rather inconvenient
if you just want to test while running on your local computer. Luckily, we have ngrok,
a forwarding service that hosts a public HTTPS URL that passes to your local computer.
Sign up for ngrok and download it [here][download-ngrok].

After installing, run `ngrok http 5000` to create an ngrok URL that will be passed
to your local port 5000. As long as you run Rocket on port 5000 (see below),
you can then access it through the HTTPS URL that ngrok gives you. Note that it is
very important to use the HTTPS URL, *not* the HTTP URL.

## 2: Create a Slack Workspace

For testing, it's useful to have your own Slack workspace set up. If you do not
already have one, go [here][create-workspace] to create one, and follow the steps
to set it up.

## 3: Create a Slack App

Follow the link [here][make-slack-app] to create a new Slack app - you can name it
whatever you like - and install it to the appropriate workspace.

### 3.1: Add a Bot User

In "Add features and functionality", add a bot user. Since this is just for testing,
you can name the bot user whatever you like.

### 3.2: Install Slack App

In "Install your app to your workspace," click the button to install to your
workspace. This will take you to a permissions page for the workspace - make sure
this is for the correct workspace, and allow the app to connect.

### 3.3: Determine Credentials

Make note of the app's signing secret, found in Settings -> Basic Information ->
App Credentials, and the bot user OAuth access token, found in Features ->
OAuth & Permissions -> Tokens for Your Workspace. These will be needed for the
configuration step later.

## 4: Gain Access to AWS

Rocket makes use of AWS DynamoDB as its database, and for testing you will want
to test on the "real" DynamoDB. If you do not already have access to DynamoDB,
you can use it as part of the free tier of AWS. Create an AWS account for
yourself, then go to the IAM service and create a new user. The user name
doesn't particularly matter (though `rocket2-dev-$NAME` is recommended),
but make sure you check "programmatic access." In permissions, go to
"Attach existing permissions directly" and add the `AmazonDynamoDBFullAccess`
policy. Finally, copy the provided access key ID and secret access key after
creating the new user.

Note: if you are in the `brussel-sprouts` Github team, you should already have
AWS credentials. Just ask.

## 5: Set Up Config

Our repo already contains `sample-env`, the main environmental configuration
file for the entire app, as well as the `credentials/` directory, where you
will put credential files like the Github app private key. The file is split
into section. There is a general section (which should be the top bit), a
section on everything slack related, a section on Github and Github apps,
and a section on AWS. [Please read the section about the configuration
system.][config]

### 5.1: Set up Github App and organization

Register Rocket 2 as a Github App under an appropriate testing organization
(our team has one of these set up already). Make sure to install the Github App
to the organization in addition to registering it.

Under "Private keys", click "Generate a new private key". This will generate
and allow you to download a new secret key for Rocket 2. Save this to the
`credentials/` directory as `github_signing_key.pem` - it should already be in
the PEM file format, bracketed by:

```
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
```

Authenticating Rocket 2 as a Github App and obtaining an access token for the
Github API should be automated, once the signing key is available.

After doing this, remember to put your ngrok HTTPS URL with `/webhook` appended
at the end, into the "Webhook URL" box. After doing this, you must go to the
app's "Permissions & Events" tab and set the following as read-only:

- Organization hooks
- Organization members

After doing so, please check the checkboxes below:

- Membership
- Organization
- Team
- Team add

## 6: Build and Run Container

This section assumes you already have installed Docker. Assuming you are in the
directory containing the Dockerfile, all you need to do to build and run is the
following two commands:

```bash
docker build -t rocket2-dev-img .
docker run --rm -it -p 0.0.0.0:5000:5000 rocket2-dev-img
```

Note that the options passed to `-p` in `docker run` tell Docker what port
to run Rocket on. `0.0.0.0` is the IP address (in this case, localhost),
the first `5000` is the port exposed inside the container, and the second
`5000` is the port exposed outside the container. The port exposed outside
the container can be changed (for instance, if port 5000 is already
in use in your local development environment), but in that case ensure that
ngrok is running on the same port.

Also note that, for your convenience, we have provided two scripts,
`scripts/docker_build.sh` and `scripts/docker_run_local.sh`, that run these
exact commands.

### 6.1: [Optional] Running without Docker

We highly recommend building and running on Docker, but building every time
you make a tiny change can be inconvenient. If you would like to run without
building a new Docker image every time, you can do so with `pipenv run launch`.
This is in fact the same command Docker runs, but if you run outside Docker,
you may run into errors due to unexpected changes in your local development
environment.

## 7: Configure Slack App Features

In addition to a bot user, there are a couple other features that need to be
enabled in the Slack app once the local instance of Rocket is running.

### 7.1: Add Event Subscriptions

In "Add features and functionality", add event subscriptions. In particular, under
Request URL, submit the ngrok HTTPS URL with `/slack/events` appended to the end.
Note that ngrok will generate a new HTTPS URL every time it runs, so you will have
to repeat this step every time you launch ngrok. You will then have to enable
workspace and/or bot events that we want Rocket to listen for, like the `team_join`
workspace event - ask the team for the most up-to-date list of these.

### 7.2: Add Slash Command

In "Add features and functionality", add a slash command. In particular, under
Request URL, submit the ngrok HTTPS URL with `/slack/commands` appended to the
end. For the actual command, anything will work, though the final app will use
`/rocket`. Make sure you tick the box marked "Escape channels, users, and links
sent to your app", or else none of the @ signs will work properly!

## 8: Testing

This is the final and most important part: testing if it actually works or not.
Go to your Slack workspace and add Rocket (or whatever you named your Slack bot)
to the channel if you have yet to do so (just type `@<bot name>` and Slack will
ask if you want to invite the bot into the channel).

To test if Rocket is running, type the command:

```
/rocket user help
```

If you see a list of options, Rocket is working!

### 8.1: Setting Up Admin Permissions

We currently haven't finished the command to add a user to the database or
make them an admin, so we have to do it manually.

First, determine your Slack ID by reading the logs. The logs are formatted like so:

```
{slackid_making_the_command}:{command_itself}
```

The Slack IDs of other users will appear when you type `@` followed by whatever
the user's handle is. Slack automatically converts that handle into an ID.

Then, you have an option of either using the AWS command-line interface or
using the AWS web interface.

You should already have the command line interface installed via pipenv. If not,
run the command `pipenv install --dev`. Note that to run commands, you will
either have to go into the pipenv environment (with `pipenv shell`) or prefix
every command with `pipenv run`. Here is the command to create a user with a:

```bash
# The following command is split into multiple lines because it is long. Make
# sure that the actal command isn't split into multiple lines because it may
# complicate things.
aws dynamodb put-item --table-name USERS_TABLE\
                      --item '{"slack_id":{"S": "UE7PAG75L"},
                               "permission_level":{"S": "admin"}}'\
                      --endpoint-url http://localhost:8000
```

Replace `USERS_TABLE` with whatever name you set in `config.toml`.

Alternatively, you can directly edit the DynamoDB table via the AWS web
interface. Go to the DynamoDB service in the AWS web interface and open
the appropriate table. Click on the Items tab and then on "Create item".
Make sure there's a column for `slack_id` and `permission_level`,
where `slack_id` is a `String` with the appropriate value and
`permission_level` is a `String` with the value `admin`.

### 8.2: Viewing a User

```
/rocket user view
```

The output of this command should be a stylish table displaying your Slack id
and permissions level.

Now, you can continue with whatever testing you originally wanted to do.
Remember to rebulid your Docker image every time you make a change!

[config]: Config.html
[create-workspace]: https://slack.com/create
[make-slack-app]: https://api.slack.com/apps
[download-ngrok]: https://ngrok.com/
[github-token]: https://github.com/settings/tokens
