FROM node:14 AS frontend
WORKDIR /app

COPY package.json yarn.lock vite.config.js  ./
RUN yarn install

COPY src/saleor-algolia-ui/ ./src/saleor-algolia-ui/
RUN yarn run build

FROM python:3.9 AS backend
RUN apt-get -y update \
    && apt-get install -y gettext \
    # Cleanup apt cache
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LOs https://github.com/segmentio/chamber/releases/download/v2.10.1/chamber-v2.10.1-linux-amd64 && mv chamber-v2.10.1-linux-amd64 /bin/chamber && chmod +x /bin/chamber

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY src/saleor_algolia /app/src/saleor_algolia
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install ; else poetry install --no-dev ; fi"

COPY --from=frontend /app/src/saleor_algolia/static/ /app/src/saleor_algolia/static/
COPY .flake8 alembic.ini docker-entrypoint.sh /app/

EXPOSE 8080
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]

CMD gunicorn --config src/saleor_algolia/gunicorn.conf.py saleor_algolia.app:app
