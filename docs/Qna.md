# Questions and Answers

**What is the `db` module?**
The database `db` module consists of the `facade` and the `dynamodb` database
we are using.

**What is the `command` module?**
The `command` module is where the slack commands get parsed and passed on to the
backend so models can be created and the database can be populated.

**What is the `model` module?**
The `model` module is where models are constructed.
Currently we have `Team` and `User` models.

**How do `db`, `command`, `model` modules interact with each other?**
First a command is input through slack. Then, the input will be parsed so a
model can be populated. After the model gets populated, the model can then be
added into the db. The db contains a separate
table for each type of model.
