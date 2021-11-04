import asyncio
import shlex
import subprocess
from datetime import datetime

import click
import uvicorn

ROOT_PATH = "src/saleor_algolia"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("saleor-domain")
def add_domain(saleor_domain):
    from saleor_algolia.configuration.models import Configuration
    from saleor_algolia.db import DBSession

    with DBSession() as db:
        config = Configuration(saleor_domain=saleor_domain, is_active=True)
        db.add(config)
        db.commit()


@cli.command()
@click.argument("saleor-domain", type=str)
@click.option("--product-id", type=str)
@click.option("--after", type=str)
def index(saleor_domain, product_id=None, after=None):
    from saleor_algolia.initial_upload import run_index_products_task

    if product_id:
        product_ids = [product_id]
    else:
        click.confirm("This will reindex all products, are you sure?", abort=True)
        product_ids = []

    start_datetime = datetime.now()

    click.secho(f"started at {start_datetime.isoformat()}")
    asyncio.run(
        run_index_products_task(saleor_domain, product_ids=product_ids, after=after)
    )
    end_datetime = datetime.now()
    datetime_delta = end_datetime - start_datetime
    click.secho(f"finished at {end_datetime.isoformat()}, took: {datetime_delta}")


@cli.command()
@click.option("--debug", type=bool, default=False, is_flag=True)
def run(debug):
    from saleor_algolia.settings import LOGGING

    uvicorn.run(
        "saleor_algolia.app:app",
        host="0.0.0.0",
        port=8080,
        debug=debug,
        reload=debug,
        log_config=LOGGING,
    )


@cli.group()
def develop():
    pass


def run_command(name, command):
    click.secho(f"{name}: ", nl=False)
    proc = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode == 0:
        click.secho("done.", fg="green")
    else:
        click.secho("failed.", fg="red")
    return proc.returncode, stdout, stderr


@develop.command()
def lint():
    click.echo("Running linters:")
    black = run_command("black", f"black --check {ROOT_PATH}")
    isort = run_command("isort", f"isort --check {ROOT_PATH}")
    flake8 = run_command("flake8", f"flake8 {ROOT_PATH}")

    if black[0] != 0:
        click.secho("Errors for black", fg="red")
        click.echo(black[1])
        click.echo(black[2])
    if isort[0] != 0:
        click.secho("Errors for isort", fg="red")
        click.echo(isort[1])
        click.echo(isort[2])
    if flake8[0] != 0:
        click.secho("Errors for flake8", fg="red")
        click.echo(flake8[1])
        click.echo(flake8[2])


@develop.command()
def reformat():
    run_command("black", f"black {ROOT_PATH}")
    run_command("isort", f"isort {ROOT_PATH}")


@develop.command()
@click.argument("docker-image", type=str)
def build(docker_image):
    subprocess.Popen(
        shlex.split(f"docker build -t {docker_image} --build-arg INSTALL_DEV=false .")
    ).communicate()


@develop.command()
@click.argument("docker-image", type=str)
def push(docker_image):
    subprocess.Popen(shlex.split(f"docker push {docker_image}")).communicate()
