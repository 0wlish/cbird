import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('-n', '--name', type=str, help='Name to greet', default='world')
def hello(name):
    click.echo(f'Hello {name}')