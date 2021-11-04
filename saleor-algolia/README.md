## An Algolia integration for Saleor

### About

This app provides a connection between [Saleor](https://saleor.io/) and [Algolia](https://www.algolia.com/).

### Development Shortcuts

#### Local deployment

##### Prerequisities

You will need a small set of tools to contribute to this service, namely:

- Python Poetry
- Docker with Docker Compose

(You can get away with using only Docker but that can sometimes be troublesome)

Create a Docker network for development purposes:

```
$ docker network create saleor
```

##### Running the service

You can run every command locally or in a Docker container. I.e. to run the service you can either:

```
$ saleor-algolia run --debug
```

or

```
docker-compose run --rm --service-ports saleor_algolia saleor-algolia run --debug
```

The same can be done with other commands like: `alembic revision --autogenerate -m "migration_name"`, `saleor-algolia add-domain 127.0.0.1:8000` or `pytest src/saleor_algolia`

#### App Installation

TBD
