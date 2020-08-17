# RediSolar Python

This is the sample application codebase for the Redis University course [RU102PY, Redis for Python Developers](https://university.redislabs.com/courses/ru102py/).

## Setup

### Prerequisites

To start and run this application, you will need:

* [Python 3.8](https://www.python.org/downloads/) (**Note**: It must be version 3.8)
* Access to a local or remote installation of [Redis](https://redis.io/download) version 5 or newer
* Your Redis installation should have the RedisTimeSeries module installed. You can find the installation instructions at: https://oss.redislabs.com/redistimeseries/#setup

**Note**: If you don't have Redis installed but do have Docker and want to get start quickly,
run `make timeseries-docker`. This starts a Redis container with RedisTimeSeries installed.

### Setting up Python dependencies with make

This project automates setting up its Python dependencies with `make`.

To get started, run `make env`. This command creates a virtual environment
and installs the project and its dependencies into the environment.

### Setting up dependencies manually

Follow the steps in this section if you want to manually set up the project.

Note that the Makefile provides targets (e.g. `make all`, `make backend_dev`,
and `make frontend_dev`) that automate everything you should need to do, so
manually setting up the project is not necessary.

#### Virtualenv

If you want to create a virtualenv manually instead of using `make env`, run the
following command from the base directory of the project:

    python3.8 -m venv env

#### Dependencies

Before installing dependencies, activate the virtualenv:

    source env/bin/activate

Install the app and its dependencies by running the following command from the
base directory of the project:

    pip install -e .

### Redis

This project requires a connection to Redis. The default settings expect Redis
to run on localhost at port 6379 without password protection.

#### RedisTimeSeries

This project uses the RedisTimeSeries module. You can either install it manually
or run Redis with the module enabled using Docker.

Check the project's web site for installation instructions: https://oss.redislabs.com/redistimeseries/

**Note**: As mentioned earlier in this document, if you have Docker installed and want to get started quickly, run
`make timeseries-docker`, which starts a Docker container running Redis with the
RedisTimeSeries module enabled.

#### Username and password protection

If you use Redis with a username (via the new ACL system in Redis 6) and/or a
password, make sure to set the `REDISOLAR_REDIS_USERNAME` and/or
`REDISOLAR_REDIS_PASSWORD` environment variables before running project-related
`make` commands or manual commands.

You can set these on the command line like so:

    $ REDISOLAR_REDIS_USERNAME=your-username make load

However, doing so keeps a record of these variables around in your shell history.

The example project is configured to read environment variables from a `.env` file,
so if you do need to use environment variables, we recommend adding them to this file.

*Note*: The `.env` file is ignored by git because we added it to the `.gitignore`
file. If you use a `.env` file, you should avoid adding it to git, so your
credentials don't end up in git's history.

Finally, credential management is a big topic. This is just a demo project --
make sure you follow your company's guidelines for credentials management.

#### Using a different hostname and/or port for Redis

**Important note**: If you are not using Redis on localhost at port 6379, you
need to update the following files:

- `redisolar/instance/dev.cfg`
- `redisolar/instance/testing.cfg`

In the referenced files, change the values of `REDIS_HOST` and `REDIS_PORT` to
the correct values for your Redis instance.

#### Key prefixes

This project prefixes all keys with a string. By default, the dev server and
sample data loader use the prefix "ru102py-app:", while the test suite uses "ru102py-test:".

When you run the tests, they add keys to the same Redis database that the
running Flask application uses, but with the prefix "test:". Then when the
tests finish, the test runner deletes all the keys prefixed with "test:".

You can change the prefix used for keys by changing the `REDIS_KEY_PREFIX`
option in the following files:

- `redisolar/instance/dev.cfg`
- `redisolar/instance/testing.cfg`

## Loading sample data

Before the example app will do anything interesting, it needs data.

### With make

If you're running Redis locally, you can use the command `make load` to load
sample data. `make load` loads data into a Redis running on localhost at port
6379.

### Manually

If Redis is running on a different host than localhost, or on a different port, use the `load_redisolar` command to load data.

Once you've installed the project's Python dependencies, the `load_redisolar`
command should be available on your command line.

**Tip:**: If the `load_redisolar` command is not available, make sure that you installed the project dependencies (done with `make env`), there were no errors in the `make env` output), and you've activated the project's virtualenv by running `source env/bin/activate` from the project root.

`load_redisolar` takes options for host and port, so you can import into a specific host or port by passing those options:

    load_redisolar --host 192.168.1.9 --port 16379

The command will populate solar sites and generate example readings.

### Password protection

If your Redis instance is password-protected, pass the `-w/--request-password` option to
make `load_redisolar` ask you interactively for the password.

To send the password to `load_redisolar` non-interactively, set the
`REDISOLAR_REDIS_PASSWORD` environment variable.

In most Unix shells, you can set an env var using `export`:

    export REDISOLAR_REDIS_PASSWORD=password

Or supply it on the command line:

    REDISOLAR_REDIS_PASSWORD=password load_redisolar --host 192.168.1.9

## Running the dev server

### With make

Run the development server with `make dev`.

**Note:** By default, the server runs with geographic features disabled. To run
with geo features enabled, set the option `USE_GEO_SITE_API` in
`redisolar/instance/dev.cfg` to `True`.

After running `make dev` access https://localhost:8001 to see the app.

**Don't see any data?**
The first time you run `make dev`, you may see a map with nothing on it. In order to see
sites on the map, you'll need to do two things:

1. Follow the instructions in this README to load data
2. Complete Challenge #1 in the course

### Manually Running the Dev Server

You can use the `flask` command to run the dev server manually, like so:

    FLASK_APP=redisolar flask run --port=8001

### Password protection

If your Redis instance requires a password, set it using the
`REDISOLAR_REDIS_PASSWORD` environment variable.

See instructions in the "Password protection" section of the previous
instructions on loading sample data for more information on setting environment
variables.

## Running tests

You can run `make test` to run the unit tests. Doing so will build
a virtualenv automatically if you have not already done so.

## FAQ

## Why do I get a ConnectionError when I run the tests or dev server?

You might see an error like this (or many of them) when you try to run the tests:

    ERROR tests/scripts/test_update_if_lowest.py::test_update_if_lowest_unchanged - redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379. Connection refused.
   
The error is telling you that Redis is not running on port 6379. Make sure you've started Redis -- exactly how to do so depends
on your operation system and the way you installed Redis. For example, if you installed via Homebrew on a Mac, the command is:

    brew services start redis 
   
## Why do I get an "Authentication required" error when I try to run the tests/dev server?

Your Redis instance requires a username and/or password to connect. First, find out what those are. Then follow the "Username and password protection" section of this README to configure the project to connect with those credentials.

## Why do I get an "unknown command `TS.ADD`" when I try to run the tests?

Your Redis instance does not have the RedisTimeSeries module installed. See the section "RedisTimeSeries" in this README for instructions.
