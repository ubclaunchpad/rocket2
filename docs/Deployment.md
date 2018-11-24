# Deployment Process

## Travis CI

[Travis CI](https://docs.travis-ci.com/user/tutorial/) is a continuous integration
service that is used to build and test software projects hosted on Github.
To configure Travis CI, a file  `.travis.yml` needs to be added to the
root directory of the directory. This YAML file will contain the commands for
the automated tests that needs to run.

Every time a branch gets pushed into github, Travis CI starts a job. A job is
where Travis clones the GitHub repository into a new virtual environment to
test the code.

Travis CI can also be integrated with slack channels to notify developers
when its processes have completed.

## Docker

[Docker](https://docs.docker.com/get-started/) is a program that run software
packages called containers. Every container is isolated from each other and is
a bundle (also known as image) of their own tools, applications, libraries and
configuration files. However, containers are able to also communicate with each
other through channels, and all containers are run by a single OS kernel.
We use Docker in Rocket2 to make deployment to the server easier.

Docker is composed of 3 parts: Container, Services, and Stack.
`Dockerfile` defines the container. Inside `Dockerfile` is the environment that
would be set up. Inside the container for Rocker2, we have a copy of our app,
and all the dependencies and the virtual enviroment installed.

`docker-compose.yml` defines the services which describe how Docker containers
should behave in production.

Docker is different than virtual machines because it can run multiple containers
using only one kernel which makes it more lightweight.

## Code Coverage

Code coverage measures the lines that were executed by the test suite.
[CodeCov](https://docs.codecov.io/docs/about-code-coverage) is used in Rocket2.

Two common code coverages are Statement Coverage and Branch Coverage.
Statement coverage counts the number of executable lines of code that has been
tested, whereas branch coverage requires all code blocks and execution paths to
be completed tested.
For example, in an `if` statement, both the `true` and `false` outcome should be
covered.If only one path is covered, then it is a called a partial coverage.

CodeCov coverage is computed using `hits/(sum of hit + partial + miss)` where
`hit` is the statement coverage and `partial` is for partial branch coverage and
`miss` is for not tested code.

