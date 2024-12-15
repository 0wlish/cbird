#note: virtualenv testing environment is cbirdtest
#enter virtualenv with "source cbirdtest/bin/activate"

import click

@click.group()
def cli():
    pass

@cli.command()
def hello():
    click.echo("Hello World")