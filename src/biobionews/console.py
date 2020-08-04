import click

from . import __version__, biobio
from .utils import clean_and_short, get_cleaned


@click.command()
@click.option(
    "--limit",
    "-l",
    default=10,
    help="Limite de noticias",
    metavar="LIMIT",
    show_default=True
)
@click.version_option(version=__version__)
def main(limit):
    data = biobio.last_news(limit=limit)

    for new in data:
        title = f"{new.get('post_hour')} {get_cleaned(new.get('post_title', '-'))}"
        click.secho(title, fg='yellow')
        lines = clean_and_short(new.get('post_content', ''))
        for line in lines:
            click.echo(get_cleaned(line))
        click.echo("")
