
# Twooter!

## Step 1

I chose to use the following technologies to build the API:

- Python

  Great for prototyping, very readable, terse and elegant code, tons of libraries available.

- FastAPI

  An async web framework for Python, specifically designed for writing APIs. It leverages Pydantic for input validation
  and automatically generates an OpenAPI spec and docs based on the route definitions (see `/docs`).

- Tortoise ORM

  An async ORM for Python. This makes it easy to generate a database schema from Python classes and gives a convenient
  interface for manipulating data in the database.

I also used ChatGPT to generate a few hundred mock messages, so the various endpoints can be tested more easily.

### Hosted solution

I've hosted the finished application using Railway for easy verification:

https://twooter-production.up.railway.app

See the generated OpenAPI documentation here:
https://twooter-production.up.railway.app/docs

For the database, I used a free [PlanetScale] instance. ([PlanetScale] is a SaaS that provides a massively scalable
MySQL-compatible database backed by [Vitess].)

[PlanetScale]: https://twooter-production.up.railway.app/docs
[Vitess]: https://vitess.io

Each endpoint can be tested by expanding the documentation section for that endpoint and clicking "Try it out".

### Spin it up locally

Spinning up Twooter locally requires Docker and Python 3.11.

Run MySQL:

```
$ docker run -d \
    --name twooter-mysql \
    -e MYSQL_USER=twooter \
    -e MYSQL_PASSWORD=password \
    -e MYSQL_DATABASE=twooter \
    -p 127.0.0.1:3306:3306 \
    mysql:8-debian
```

Install Poetry, then install Python dependencies:

```
$ pip install -y poetry
$ poetry install
```

Spin up the server:

```
$ poetry run uvicorn twooter.app:app --reload
```

The API is now reachable at http://127.0.0.1:8000 and automatically reloads on code changes. You can read the generated
docs at `/docs`.

Optionally, insert the ChatGPT generated messages for testing:

```
$ poetry run python3 ./scripts/add_test_data.py
```

## Step 2

### Scalability

To make a sure an application can scale easily, a few core principles should be followed:

- Make the application stateless

  Don't save anything to disk, don't hold anything in memory between requests, only store state in the backing database
  or in shared key/value stores like memcached or Redis. Never assume that 2 consecutive user requests will hit the same
  application instance. This makes it trivial to spin up extra application instances to handle increased traffic.

- Accept configuration from environment variables

  This makes it very easy to manage the configuration of your application instances through Kubernetes manifests, Docker
  Compose configs etc.

- Make the application disposable

  The application should start up quickly and exit quickly and cleanly. This makes it trivial to spin up extra instances
  to handle traffic spikes and tear down instances to save on resources.

If these principles are followed, it should be fairly trivial to deploy the application to any serverless infrastructure
provider (such as Railway, Heroku etc.) or Kubernetes cluster and scale it horizontally by increasing the number of
instances.

I have currently deployed Twooter to Railway, which doesn't support horizontal scaling (but it's on the roadmap for
2023). If I wanted to scale Twooter to millions of users today, I could deploy the application on Heroku instead, which
supports virtually limitless horizontal scaling by upping the number of "dynos". However, my understanding is that
Heroku is fairly pricy, so it might be a better option to look for a hosted Kubernetes option instead, for example on
Linode.

The entire idea of PlanetScale is scalability, so that part is already all set. Scaling databases is hard, so it's
something I'd prefer leaving to the professionals.

### Maintainability and extendability

My next steps for supporting a large scale Twooter in production would be:

- Set up the infrastructure for static code analysis (linting, type checking), unit testing (pytest), E2E testing (maybe
  Robot Framework?) and vulnerability scanning (e.g. [Grype])
  - **Important**: These steps should all be trivial to run locally on development machines, so I would set up scripts
    to assist with that. Relying on the CI/CD pipeline for troubleshooting test issues is extremely slow and kills
    productivity.
- Set up a CI/CD pipeline that runs the aforementioned steps on every PR and deploys the main branch to production on
  success
- Set up log aggregation with alerts on errors
- Set up monitoring of service endpoints with alerting
- Set up data aggregation for analytics (twoot count, request processing time, query times etc.)

[Grype]: https://github.com/anchore/grype
