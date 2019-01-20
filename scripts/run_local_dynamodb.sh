#!/usr/bin/env bash

# Run DynamoDB through java
cd DynamoDB
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb &
cd ..

sleep 3
