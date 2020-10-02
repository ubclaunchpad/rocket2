#!/usr/bin/env bash
# This script downloads the latest dynamodb archive for local use, sets up aws
# configurations with dummy values (to get it going), and starts the db daemon.
# Meant for use on automated builds only, and not for personal use.

# Download DynamoDB archive for local use (testing)
if [[ ! -d DynamoDB ]]; then
	printf "Setting up DynamoDB, locally...\n"
	wget https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz
	mkdir DynamoDB
	tar -xvf dynamodb_local_latest.tar.gz --directory DynamoDB
else
	printf "DynamoDB set up correctly\n"
fi

# Run DynamoDB through java
cd DynamoDB
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb &
cd ..

sleep 3
