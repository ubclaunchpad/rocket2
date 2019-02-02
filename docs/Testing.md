# Testing

## Running Pytest Efficiently

Test Driven Development... we hear professors preach about it during lectures
but we never got an opportunity to put it to good use until Rocket2 came along.
Unfortunately we got over excited and wrote A LOT of tests. Running them all
every time is a bit painful, that's where `@pytest.mark` comes in. `pytest.mark`
allows you to label your tests to run them in groups.

We only have tests that test the functions by themselves. Features that involve
multiple parts (such as a new command involving Slack, Github, and the database)
should be tested manually as well.

### Run all the tests

`pytest`

### Run only db tests

`pytest -m db`

### Run all tests except database tests

`pytest -m "not db"`

## Testing the Database

What are environment variables? Variables for the environment of course! These
variables set up the environment for testing. Rocket2 uses them because we have
both a local and a sever DynamoDB database and each require an extra variable to
get everything working.

### Run local DynamoDB

We use `testing` in the `config.toml` to indicate if we want to run DynamoDB
locally or on a server. Change `testing = true` to use local DynamoDB.

If `testing == true` but you did not start an instance of local DynamoDB,
`scripts/build_check.sh` will automatically skip all database tests.

This is the recommended way for unit testing.

### Run server DynamoDB

To run the server DynamoDB we need to set the `region` and obtain both the
AWS `access_key_id` and `secret_access_key`.

This is the recommended way for testing everything (not unit testing, but
testing the slack commands themselves). Click [here][full-testing] to learn how
to set up a full development environment (including the testing part).

[full-testing]: LocalDevelopmentGuide.html
