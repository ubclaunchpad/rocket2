Deployment
==========

Deployment Process
------------------

The following should be read as more of a reference than a guide. To
deploy Rocket 2, you must follow the steps as if you were building it
for local use, except some tweaks in regards to where it goes and more
tooling-specific details mentioned below.

Hosting
~~~~~~~

Rocket 2 is currently hosted by an AWS EC2 t2.micro instance. Since this
is a single-threaded application with a single worker thread, there is
not much of a reason to go for anything more. **Note: Adding more worker
threads may cause "minor" issues such as the scheduler running more than
once, weird exceptions, and may prevent the server from running in some
cases, which is why increasing the number of worker threads beyond 1 is
not recommended.**

If need-be, Inertia can `help provision an instance for
you <https://inertia.ubclaunchpad.com/#provisioning-a-remote>`__.

Should you wish to set up your own Rocket 2 instance for deployment, you
should first be able to set up a Rocket 2 instance for testing on a
local computer with ``ngrok`` forwarding. If you have successfully set
up an instance on a remote computer, you may still want to have a look.

For those of you who don't want too much of a hassle, hosting via Heroku
is also a valid option, as Heroku does continuous deployment without the
need of setting up Inertia, and also has built-in SSL so you don't need
to set anything up. Be wary, however, that Heroku is almost twice as
expensive as an AWS EC2 t2.micro instance.

Do note that you must set the environmental variables in the provided
settings page if you are to host via Heroku. For details regarding how
you would input the ``GITHUB_KEY``, please see `below <#github-key>`__.

SSL
~~~

Before deploying for the first time, you must set up SSL and
configuration for Nginx, which we are using as a proxy server. This can
be done by running the ``scripts/setup_deploy.sh`` script. This runs the
official `Let's Encrypt <https://letsencrypt.org/>`__ container to
request SSL certificates, sets up a cronjob to periodically re-validate
them, and copies ``nginx.conf`` to the correct location. Do note that
the Let's Encrypt container needs to use port 443, so if you have
another process or container using that port, you will need to kill it
before running the set up script.

Inertia
~~~~~~~

For UBC Launch Pad, we continuously deploy off the ``ec2-release``
branch on Github using UBC Launch Pad's
`Inertia <https://github.com/ubclaunchpad/inertia>`__. This will pull
the repo when changes are merged, rebuild the containers from
``docker-compose.yml``, and redeploy.

When deploying with Inertia, make sure that you are using a stable
version of Inertia.

Since we have changed from using ``.toml`` configuration files to using
environmental variables for configuration, you must inject them using
``inertia {some name} env set AWS_LOCAL False`` and the like. If you
already have all your environmental variables set up in your ``.env``
file, you can send the entire file over with
``inertia {some name} send .env``.

GITHUB_KEY
^^^^^^^^^^

The ``GITHUB_KEY`` is merely the GPG private key used to sign Github API
requests. We simply shove the entire file into a string and use it in
the environmental variable. Do note that doing this on the command line
is somewhat difficult because ``inertia`` would treat the dashes ``--``
in the string as flags and get confused. Another thing to watch out for
is that the command line ignores the new lines in the string. The
current working method of doing this is to pass in the entire string
with a single quote (which means that every symbol is taken literally),
then for every dash in the string, we add a forward slash ``\`` in
front. We then replace all new lines with the literal ``\n``.

Our configuration code replaces these instances of ``\-`` and ``\n``
with actual dashes and new lines.

Note that these replacements are not necessary on Heroku and you can
simply copy and paste the contents of the key file directly into the box
provided.

If you are using the ``.env`` file approach, you only need to replace
the new lines and not the dashes.

Docker Compose
~~~~~~~~~~~~~~

Our main deployment configuration is contained in
``docker-compose.yml``. We deploy an Nginx container to serve as a
proxy, as well as building and running a Rocket 2 container. The Nginx
proxy exposes ports 80 and 443, for HTTP/S, which must also be
accessible from the outside world. The Rocket 2 container exposes port
5000, as Gunicorn is listening on this port; this should *not* be
accessible to the outside world. We use `certbot` for periodic certificate
renewals.

Note that Docker Compose has a rather complex networking utility. In
particular, note that to access HTTP endpoints in other composed
containers, you must reference them by their service name in
``docker-compose.yml``, *not* via localhost. This is already handled in
``nginx.conf``.

Pure Docker
~~~~~~~~~~~

One deployment option is to use the standalone Docker image:

.. code-block:: bash

    docker pull ghcr.io/ubclaunchpad/rocket2:latest
    docker run --rm -it -p 0.0.0.0:5000:5000 --env-file .env ghcr.io/ubclaunchpad/rocket2

Other Build Tools
-----------------

Github Actions CI
~~~~~~~~~~~~~~~~~

`Github Actions CI <https://github.com/features/actions>`__ is a
continuous integration service that is used to build and test software
projects hosted on Github. To configure Github CI, a file
``pythonpackage.yml`` needs to be added to ``.github/workflows/``. This
YAML file will contain the commands for the automated tests that needs
to run.

Every time a branch gets pushed into github, Github CI starts a job. A
job is where Github clones the GitHub repository into a new virtual
environment to test the code.

Docker
~~~~~~

`Docker <https://docs.docker.com/get-started/>`__ is a program that run
software packages called containers. Every container is isolated from
each other and is a bundle (also known as image) of their own tools,
applications, libraries and configuration files. However, containers are
able to also communicate with each other through channels, and all
containers are run by a single OS kernel. We use Docker in Rocket2 to
make deployment to the server easier.

Docker is composed of 3 parts: Container, Services, and Stack.
``Dockerfile`` defines the container. Inside ``Dockerfile`` is the
environment that would be set up. Inside the container for Rocket2, we
have a copy of our app, and all the dependencies and the virtual
environment installed.

``docker-compose.yml`` defines the services that allow multiple
containers to run together.

Docker is different than virtual machines because it can run multiple
containers using only one kernel which makes it more lightweight.
