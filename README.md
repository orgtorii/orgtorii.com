# Org Torii ⛩️ - The open source alternative to Glassdoor

## What are we trying to achieve?

Our aim is to bring transparency to companies world wide, peeking behind the marketing and opening up the internal culture.

We provide a safe space for current and ex-employees to leave reviews and share salary information & working conditions.

Employers are not left out - they can brand their profiles, collect and analyze reviews and compare their salaries information to others in similar locations & industries and post jobs to attract future employees.

We believe this transparency will benefit and improve the working conditions of everyone.

### Why not Glassdoor?

[Glassdoor](https://glassdoor.com/) has taken over $200 million in funding and was acquired in 2018 for $1.2 billion. However we believe that as a website, it is filled with dark UX patterns, paywalls and locked information - it can be done better, fairer and with more transparency.

### Monetization

A business won't get far without covering it's own costs. In the beginning, as we develop the paid features, we will work on a model similar to Wikipedia. Our data will be open and not require a login or a paid subscription etc. Instead we ask for user donations to cover the running and development costs.

In the future we will offer paid features to companies who wish to use the platform to mine data or promote their excellent results and their open job positions.

## Developing on this project

We have chosen to make our project open source so if you want a feature or are simply looking to contribute to an open source project we welcome your involvement.

> **Please note** you do not have to be a developer to contribute. If you wish to help this project succeed you can achieve a lot by promoting Org Torii to your friends and family. Encourage them to write a review and anonymously share their salary information. Advocate and raise awareness to your employer to take Org Torii seriously and engage with the feedback here.

### Installing requirements

#### Python backend

> **Note**: We recommend `Python3.12`

```
$ make install
```

This creates a virtual environment, installs the dependencies and installs `pre-commit`.

### Setting environment variables

Environment variables are loaded from a `.env` file.

We provide a pre-configured environment file for local development (this should **never be used in production**). We can copy the local `.env.template` file with the defaults and this can be modified by developers for their own needs.

```shell
$ # Copy local environment defaults
$ cp .env.template .env
```

When deploying to production, the `.env.dist` file can be used as a base however as this file is committed as-is to version control, all sensitive settings should be modified for use on the production environment.

```shell
$ # Collect static files for serving via Whitenoise
$ make collectstatic

$ # Run the local django development server
$ make runserver
```

If also developing on the frontend, make sure to run the frontend pipeline with npm. In a separate terminal:

```shell
$ # Run tailwind in `watch` mode to automatically build and purge
$ npm run tailwindcss:watch
```

### Keeping to the style guide

Code styling is enforced by [Ruff]() (run as part of pre-commit and the CI/CD pipeline).

We choose to follow the [HackSoftware Django guide](https://github.com/HackSoftware/Django-Styleguide) wherever we can for the layout and structure of our code.

## Deployment to production

At this stage, production uses containers and persistent volumes to store data.

```shell
$ # Build the static assets
$ npm run tailwindcss:build

$ # Collect the newly compiled static assets
$ make collectstatic
```

## Continuously integrating and deploying

As our code is hosted on Github, we leverage [Github Actions](https://github.com/features/actions).

The CI/CD pipeline performs the following actions:

### For all pushes

- checks our code for linting and formatting errors (all pushes);
- unit tests the code (all pushes);

### For pushes to `main` branch

- builds new container image for deployment
- versions container image (semantic version tags on `main` branch);
- pushes new container image to repository
- runs integration tests on new container image
- migrates database
- updates running container image

## Production architecture

### Configuration

To make it easy to setup a server (e.g. for disaster recovery, fail-overs, future scaling etc.), we use [Ansible](https://docs.ansible.com/ansible/latest/index.html) to install OS dependencies and manage our configuration as code.

### Backend

Org Torii is a Python + [Django](https://www.djangoproject.com/) application with a [Caddy](https://caddyserver.com/) web server in front to take care of HTTPS, reverse proxying and static file serving.

### Database

We have chosen to use SQLite as our production data store. While this may seem counterintuitive to some, SQLite can act valiantly as a production level database, especially in read-heavy applications like ours.

#### Extensions

To support some fields we need to install some SQLite extensions:

- [JSON1 Extension](https://code.djangoproject.com/wiki/JSON1Extension) for the [`models.JSONField`](https://docs.djangoproject.com/en/4.1/ref/models/fields/#jsonfield);
  - Used for storing the pros/cons of a `Review`.
- [SpatiaLite](https://www.gaia-gis.it/fossil/libspatialite/index) for the [`django.contrib.gis.db.models.PointField`](https://docs.djangoproject.com/en/4.1/ref/contrib/gis/model-api/#pointfield);
  - Used for storing the location of an organization and a reviewer location.

#### Migrations

Migrations are run as part of the automated CI/CD pipeline and thus must never be "breaking" migrations to minimize service disruption.

By this we mean we prefer to make two migrations (and releases) which may affect running code.

For example, given that we must rename a column in our database. If we simply rename the column the old code will break. If there is a delay in deploying the newer version, or we need to roll back then the old code will not be compatible with the new column name. In this case we would add a second column with the new name (copying the values from the original column). Then, in a second release we would delete the old column. Should we have to roll back our code would still function (although may be out of date - this could be rectified by copying the values from the new column to the old).

Database migrations should be repeatable (e.g. use `IF NOT EXISTS` etc.)

### Search

To make it fast and easy to find organizations we integrate with [Meilisearch](https://github.com/meilisearch/meilisearch) which indexes and searches all of our results as fast as possible.

### Caching

Due to the read-heavy nature of the product we heavy use of caching throughout the stack.

[Redis](https://redis.io/) is used for caching database calls and template renders.

[Cloudflare](https://www.cloudflare.com/) is used as a CDN for compressed & versioned static assets.

### Backups

We use a combination of [LiteStream](https://litestream.io/) for SQLite and [Borg](https://www.borgbackup.org/) to backup our database and static assets.

### Monitoring

To catch application errors and monitor system usage we use [NewRelic](https://newrelic.com/) and their alerting capabilities.

### Containers

[Docker Hub](https://hub.docker.com/) hosts our containers and scans them for vulnerabilities.

### Server

Org Torii is hosted on a single, dedicated [Hetzner](https://www.hetzner.com/) server with 6 cores, 64GB of ECC memory and 512GB of NVMe storage.

## Security and privacy are top priorities

Org Torii is focused on keeping users anonymous while preventing fraud, maintaining privacy and offering accurate insights into life at an organization. We take your privacy very seriously and for this reason we do not store your name, email address, telephone number etc.

To offer "verified" organization reviews we ask for your email address to prove that you work there and send you a verification code. Your email address is never stored.

So we can enable you to edit your review in the future we store a hash of your combined email and password - this makes it impossible for us to work out what your contact details are while allowing you to use your email and password to change your review in the future.

### Password hashing

Passwords are stored and hashed using Argon2di.

### Vulnerabilities

If you discover a security vulnerability we encourage you to please disclose this responsibly to [security@orgtorii.com](mailto:security@orgtorii.com). We will endeavour to act quickly and reward if we can.

## Data dumps

It is the plan to offer downloads of the Org Torii database at future dates. This will **not include any user data** however will include the database of organizations, reviews, salary ranges and job positions. We hope this can help others explore this data in their own time and encourage

In case you were not aware [Wikipedia](https://en.wikipedia.org/wiki/Wikipedia:Database_download) offers the same possibility and this is where we got our inspiration from.

## Setup Overview

- Django
- Django rest framework for APIs (when required)
- SQLite database
- Redis for queues
- [DiskCache](https://github.com/grantjenks/python-diskcache) for Django caching
- Gunicorn with 4 workers per core
- Caddy as an HTTPS web server for static files and proxy to Gunicorn
- Docker + Docker Compose to run and orchestrate the application
- Github Actions for CI/CD
- [Django newsletter](https://github.com/jazzband/django-newsletter) to capture email addresses

## Configuration

[`django-environ`](https://django-environ.readthedocs.io/en/latest/) is used to manage configuration in the `settings.py` file. To use, copy the `.env.template` file to `.env` and update the values as needed. If local overrides are required, put them into `.env.local`.

## Security

### Object level permissions

[`django-guardian`](https://github.com/django-guardian/django-guardian) is used for granular permissions.

### Authentication

[`django-allauth`](https://docs.allauth.org/en/latest/introduction/index.html) is configured for regular accounts with the following setup:

- Local accounts (no external social accounts). Chosen for speed and don't have to register any additional social accounts.
- Email addresses as username
- Login via code is enabled
- Multi-factor authentication via TOTP or Passkey

## Development

- [Pipenv](https://pipenv.pypa.io/en/latest/) for dependency management
- [Playwright](https://playwright.dev/) for end-to-end user tests

### Prerequisites

- [`pipenv`](https://pipenv.pypa.io/en/latest/) for python dependency management
- [`entr`](https://github.com/eradman/entr) for hot reloading tests (`make test-watch`)
- [`rg`](https://github.com/BurntSushi/ripgrep) for finding the python and html files suitable for hot reloading

### Setup

1. Clone repo
1. `make install` (this will setup a virtual environment and install dependencies)

### Debugging

- [`debug-toolbar`](https://github.com/jazzband/django-debug-toolbar) for SQL query analysis

### Linting & Formatting

[`ruff`](https://docs.astral.sh/ruff/) is used to format (drop in replacement for `black`) and lint code (run as part of a `pre-commit` hook).

### Test Driven Development (TDD)

To practice TDD with this, the best way is:

1. Write a behaviour test that uses Playwright to simulate user behaviour
1. [optional] Debug Playwright tests by appending `PWDEBUG=1` to command to run tests

#### Models

Use [factory boy](https://github.com/FactoryBoy/factory_boy) to make it easier to test models.

#### Testing Best Practices

_todo(kisamoto)_

## Backups

[`borg`](https://github.com/borgbackup/borg) and [borgmatic](https://torsion.org/borgmatic/) are used for backups to [BorgBase](https://www.borgbase.com/).

### Database

_todo(kisamoto)_

## Monitoring and alerting

Both server & application monitoring and alerting are handled by [Grafana Cloud](https://grafana.com/).

## Recommendations & best practices

Follow the [Hack Django Style guide](https://github.com/HackSoftware/Django-Styleguide).

### Sanitise user input

Use [`nh3`](https://github.com/messense/nh3) to sanitise user input as soon as it is received.

### Use the debug toolbar (only in development)

---

If in doubt, check [awesome django](https://github.com/wsvincent/awesome-django) for libraries.

## Todo

Additional things to do

- [ ] Development in a dev container that's suitable for Mac and Linux
- [ ] Finish implementing [logging and metrics capturing](https://rafed.github.io/devra/posts/cloud/django-mlt-observability-with-opentelemetry/) to Grafana

---

## What's with the name "Org Torii"?

A ["torii"](https://en.wikipedia.org/wiki/Torii) is a traditional Japanese gate which symbolically marks the transition from the mundane to the sacred. We thought this was a relevant analogy for opening today's company cultures.⛩️
