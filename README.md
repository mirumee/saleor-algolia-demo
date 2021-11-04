# saleor-algolia-demo
All Saleor services started from a single repository

*Keep in mind this repository is for local development only and is not meant to be deployed on any production environment! If you're not a developer and just want to try out Saleor you can check our [live demo](https://demo.saleor.io/).*

## Requirements
1. [Docker](https://docs.docker.com/install/)
2. [Docker Compose](https://docs.docker.com/compose/install/)


## How to run it?

1. Clone the repository:

```
$ git clone https://github.com/mirumee/saleor-algolia-demo.git --recursive --jobs 3
```

2. Go to the cloned directory:
```
$ cd saleor-algolia-demo
```

3. Build the application:
```
$ docker-compose build
```

4. Apply Django migrations:
```
$ docker-compose run --rm api python3 manage.py migrate
```

5. Collect static files:
```
$ docker-compose run --rm api python3 manage.py collectstatic --noinput
```

6. Populate the database with example data and create the admin user:
```
$ docker-compose run --rm api python3 manage.py populatedb --createsuperuser
```
*Note that `--createsuperuser` argument creates an admin account for `admin@example.com` with the password set to `admin`.*

7. Run the application:
```
$ docker-compose up
```
*Both storefront and dashboard are quite big frontend projects and it might take up to few minutes for them to compile depending on your CPU. If nothing shows up on port 3000 or 9000 wait until `Compiled successfully` shows in the console output.*

8. Go to [Saleor-Algolia installation](INSTALL_SALEOR_ALGOLIA.md) for further steps

## Where is the application running?
- Saleor Core (API) - http://localhost:8000
- Saleor Storefront - http://localhost:3000
- Saleor Dashboard - http://localhost:9000
- Jaeger UI (APM) - http://localhost:16686
- Mailhog (Test email interface) - http://localhost:8025 


If you have any questions or feedback, do not hesitate to contact us via Spectrum or Gitter:

- https://spectrum.chat/saleor
- https://gitter.im/mirumee/saleor


Some situations do call for extra code; we can cover exotic use cases or build you a custom e-commerce appliance.

#### Crafted with ❤️ by [Mirumee Software](http://mirumee.com)

hello@mirumee.com
