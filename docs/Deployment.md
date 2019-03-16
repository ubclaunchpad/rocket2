# Deployment

## Deployment Process

### SSL

Before deploying for the first time, you must set up SSL and configuration for
Nginx, which we are using as a proxy server. This can be done by running the
`setup_deploy.sh` script. This runs the official
[Let's Encrypt](https://letsencrypt.org/) container to request SSL certificates,
sets up a cronjob to periodically revalidate them, and copies
`nginx.conf` to the correct location. Do note that the Let's
Encrypt container needs to use port 443, so if you have another process or
container using that port, you will need to kill it before running the
set up script.

### Inertia

For UBC Launch Pad, we continuously deploy off the master branch on Github
using UBC Launch Pad's [Inertia](https://github.com/ubclaunchpad/inertia).
This will pull the repo when changes are merged, rebuild the containers from
`docker-compose.yml`, and redeploy.

### Docker Compose

Our main deployment configuration is contained in
`docker-compose.yml`. We deploy an Nginx container
to serve as a proxy, as well as building and running a Rocket 2 container.
The Nginx proxy exposes ports 80 and 443, for HTTP/S, which must also be
accessible from the outside world. The Rocket 2 container exposes port 5000,
as Gunicorn is listening on this port; this should *not* be accessible to
the outside world.

Note that Docker Compose has a rather complex networking utility. In particular,
note that to access HTTP endpoints in other composed containers, you must
reference them by their service name in `docker-compose.yml`, *not* via
localhost. This is already handled in `nginx.conf`.

## Other Build Tools

### Travis CI

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

### Docker

[Docker](https://docs.docker.com/get-started/) is a program that run software
packages called containers. Every container is isolated from each other and is
a bundle (also known as image) of their own tools, applications, libraries and
configuration files. However, containers are able to also communicate with each
other through channels, and all containers are run by a single OS kernel.
We use Docker in Rocket2 to make deployment to the server easier.

Docker is composed of 3 parts: Container, Services, and Stack.
`Dockerfile` defines the container. Inside `Dockerfile` is the environment that
would be set up. Inside the container for Rocket2, we have a copy of our app,
and all the dependencies and the virtual environment installed.

`docker-compose.yml` defines the services that allow multiple containers to run together.

Docker is different than virtual machines because it can run multiple containers
using only one kernel which makes it more lightweight.

### Code Coverage

Code coverage measures the lines that were executed by the test suite.
[CodeCov](https://docs.codecov.io/docs/about-code-coverage) is used in Rocket2.

Two common code coverages are Statement Coverage and Branch Coverage. Statement
coverage counts the number of executable lines of code that has been tested,
whereas branch coverage requires all code blocks and execution paths to
be completed tested. For example, in an `if` statement, both the `true` and
`false` outcome should be covered. If only one path is covered, then it is a
called a partial coverage.

CodeCov coverage is computed using `hits/(sum of hit + partial + miss)` where
`hit` is the statement coverage and `partial` is for partial branch coverage and
`miss` is for not tested code.
