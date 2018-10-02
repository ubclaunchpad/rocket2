# Requirements

## MVP

Our MVP is essentially feature-parity with the original Rocket.
In particular, we should have:

* An extensible Unix-style command system
* `user` command (member info)
* `team` command (team management)
* `help` command
* Permissions system

All of these should be connected to a database, likely a cloud
database like DynamoDb or Firebase.

We have decided *not* to pursue a full plugin-oriented architecture,
as this would severely complicate our work and most likely would not be used.

## Stretch Goals

* Currently Rocket does most of the work of managing the Launch Pad
  Github organization. Replicating and extending this behaviour would
  be our first priority after completing the MVP.
* More ways to access Rocket-the-service would be nice. In particular,
  a command-line interface should be relatively easy to build. A
  web-based dashboard would be useful, but likely too far outside scope.
* A reminders command has been specifically requested by the co-presidents.
* The co-presidents also have other feature requests that will be added
  as Github issues.

## Non-functional & Other Requirements

* Rocket 2.0 will be containerized via [Docker](https://www.docker.com).
* All code will follow the [PEP8 style guide](http://pep8.org);
  this will be automated with [pycodestyle](https://github.com/pycqa/pycodestyle).
* There should be automated tests for most behaviour, run with a CI system,
  and code coverage should be collected and uploaded to [Codecov.io](https://codecov.io).
* The command system should be reasonably extensible.
