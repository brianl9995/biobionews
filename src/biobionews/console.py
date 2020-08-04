import click
import requests

from . import __version__
from .utils import clean_and_short, get_cleaned

API_URL = "https://www.biobiochile.cl/lista/api/get-todo?limit=10"


@click.command()
@click.version_option(version=__version__)
def main():
    with requests.get(API_URL) as response:
        response.raise_for_status()
        data = response.json()
        data.reverse()

    for new in data:
        click.secho(new.get('post_hour', '') + ' ' + new.get('post_title', '-'), fg='yellow')
        lines = clean_and_short(new.get('post_content', ''))
        for line in lines:
            click.echo(get_cleaned(line), nl=False)
        click.echo("")
