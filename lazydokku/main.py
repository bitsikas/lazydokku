import click

from . import core
from . import widgets


@click.command()
@click.argument("dokku-command", nargs=-1)
def main(dokku_command):
    if not dokku_command:
        dokku_command = ["dokku"]
    command_executor = core.DokkuCommandExecutor(dokku_command)
    dokku_provider = core.DokkuProvider(command_executor)

    widgets.run(dokku_provider=dokku_provider)


main()
