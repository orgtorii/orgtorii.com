# Django SaaS Starter Kit

An opinionated template to use Django for SaaS development.

It should be "good enough" with the aim of enabling rapid development of projects from MVP to early scale up.

## Setup Overview

This opinionated setup is designed to run on a single VPS (example Hetzner or Digital Ocean). It is not designed for 100% uptime (updates will require a restart).

However it should also have the core principals of a production setup. Namely backups, monitoring and some performance.

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

### Scaling

As this uses SQLite only Vertical scaling is supported. If you're using a cloud VPS, just make a larger VPS (more cores and memory). This will go quite far but if it looks like the project is becoming a success then a refactor to use a separate DB (e.g. PostgreSQL) and horizontal scaling will likely be in order.

## Configuration

[`django-environ`](https://django-environ.readthedocs.io/en/latest/) is used to manage configuration in the `settings.py` file. To use, copy the `.env.template` file to `.env` and update the values as needed. If local overrides are required, put them into `.env.local`.

## Security

### Object level permissions

[`django-guardian`](https://github.com/django-guardian/django-guardian) is used for object level permissions.

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

_todo(ewan)_

## Backups

[`borg`](https://github.com/borgbackup/borg) and [borgmatic](https://torsion.org/borgmatic/) are used for backups to [BorgBase](https://www.borgbase.com/).

### Database

_todo(ewan)_

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
