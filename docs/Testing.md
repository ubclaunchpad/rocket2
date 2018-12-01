# Testing

## Running Pytest Efficiently

Test Driven Development... we hear professors preach about it during lectures
but we never got an opportunity to put it to good use until Rocket2 came along.
Unfortunately we got over excited and wrote A LOT of tests. Running them all
every time is a bit painful, that's where `@pytest.mark` comes in. `pytest.mark`
allows you to label your tests to run them in groups.

### Run all tests

`pytest`

### Run only db tests

`pytest -m db`

### Run all tests except db tests

`pytest -m "not db"`

## Using Environment Variables to Test the Database

What are environment variables? Variables for the environment of course! These
variables set up the environment for testing. Rocket2 uses them because we have
both a local and a sever DynamoDB database and each require an extra variable to
get everything working.

### Run local DynamoDB

We need to set the `TESTING` to indicate which DynamoDB (local or server) is
ran. `TESTING` is default to false. When `TESTING=true`, we indicate we want to
run the local DynamoDB.

`TESTING=true pytest`

### Run server DynamoDB

To run the server DynamoDB we need to set the `REGION`. The `REGION` is default
to `us-east-1`, however you can change it to [any of the regions
here](https://docs.aws.amazon.com/general/latest/gr/rande.html).

To set a new region for DynamoDB:
`REGION=us-east-2 pytest`
