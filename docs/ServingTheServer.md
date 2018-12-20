# Linking Your Dev Server to Slack

So, you want to see some progress, preferably on slack, and not just in the
forms of unit testing? At this point, fear is actually a reasonable response.
With this guide, you can be talking to your locally-hosted slack bot in no time!

> **Warning**: This only works smoothly with a unix machine (macOS or some linux
> variant. Windows users may be in for more pain than expected.

## 1: Registering Your Slack Bot

First things first, you must first create a slack workspace (an existing one
would do, as long as you can install things onto it).

After that, you must create a new slack app. Follow the link
[here][make-slack-app] to create a new slack app. Make sure to have it installed
onto your slack workspace of choice.

Now, you need to create a bot user. [Create it here][make-bot].

## 2: Download and Start Up DynamoDB

Since we are developing locally, we must use the local version of DynamoDB.
Download the `jar` from [here][dynamodb-download]. Follow the instructions from
another tab to have it up and running properly.

## 3: Download and Install (and run) ngrok

Slack does not run locally. To force/trick it to run locally (method recommended
by slack), you must forward your 5000 port to a public domain name. Luckily for
us, `ngrok` can do such things. Sign up and download and run `ngrok`
[here][download-ngrok].

Our app runs on port 5000. Run `ngrok http 5000` and copy the forwarding URL.

## 4: Configure Your Environment

We use environment variables to make everything go smoothly. Therefore, you must
as well. Create a file `.env` in the base directory (where the `README.md` is),
with the following:

```bash
SLACK_SIGNING_SECRET=""
SLACK_API_TOKEN=""
REGION="us-east-1"
TESTING="True"
```

Your `SLACK_SIGNING_SECRET` can be found [here][creds-general]. Scroll down
until you get to the section "App Credentials" and the credentials will be
directly below the "Signing Secret".

Your `SLACK_API_TOKEN` can be found [here][creds-api]. Be sure to copy the
access token under "Bot User OAuth Access Token".

## 5: Running the App

You are now ready to start the app! To start it, run `pipenv run launch`. This
will automatically include your `.env` file. Be sure to already have DynamoDB up
and running as well.

## 6: Configure Slack

Back to slack. Go [here][slack-events] and click "Enable Events". You will be
asked to submit a request URL. Remember that URL that you memorized? Paste the
URL. It should look like this:

```
https://46c81c5b.ngrok.io/slack/events
```

Notice that I have added `/slack/events` to the end of the URL. You should do
that too.

> **Important**: Please use `https` and refrain from placing an extra `/` at the
> end of the URL. It messed me up.

## 7: Actually Testing it

This is the final and most important part: finally testing if it works or not.
Go to your slack workspace and add your slack bot to the channel if you have yet
to do so (just type `@<bot name>` and slack will ask if you want to invite the
bot into the channel. say yes).

To test, type the command:

```
@<slackbot name> user help
```

If you see a list of options, the slack bot works!

There currently is no existing command to add an admin into the database, which
is perhaps what you'd want to be, so our next task is to add ourselves to the
database and using the `user view` command.

### Adding Self to Database

Since we are using Amazon DynamoDB, we have access to AWS commandline tools. You
should have AWS CLI installed. If not, run `pipenv install --dev`.

Here is the command to create a user:

```bash
# The following command is split into multiple lines because it is long. Make
# sure that the actal command isn't split into multiple lines because it may
# complicate things.
aws dynamodb put-item --table-name users\
                      --item '{"slack_id":{"S": "UE7PAG75L"},
                               "permission_level":{"S": "admin"}}'\
                      --endpoint-url http://localhost:8000
```

You can find your own slack ID by viewing the logs. The logs are formatted in
this way:

```
{slackid_making_the_command}:{command_itself}
```

The slack IDs of other users will appear when you type `@` followed by whatever
the user's handle is. Slack automatically converts that handle into an ID.

### Viewing the User

```
@<slackbot name> user view
```

The output of this command should be a nice ASCII table(ish) looking thing that
displays what you already know: your own slack id and permissions level, along
with a few missing fields.

[make-slack-app]: https://api.slack.com/apps
[make-bot]: https://api.slack.com/apps/AEGCC4G4Q/bots?
[dynamodb-download]: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html
[download-ngrok]: https://ngrok.com/
[creds-general]: https://api.slack.com/apps/AEGCC4G4Q/general?
[creds-api]: https://api.slack.com/apps/AEGCC4G4Q/oauth?
[slack-events]: https://api.slack.com/apps/AEGCC4G4Q/event-subscriptions?
