import click

from . import __version__, biobio
from .utils import get_cleaned, make_clickable, post_or_ia


@click.command()
@click.option(
    "--limit",
    "-l",
    default=10,
    help="Limite de noticias",
    metavar="LIMIT",
    show_default=True,
)
@click.option(
    "--width",
    "-w",
    default=180,
    help="Ancho del texto",
    metavar="WIDTH",
    show_default=True,
)
@click.option(
    "--lines",
    "-n",
    default=5,
    help="Cantidad de lineas por noticia",
    metavar="LINES",
    show_default=True,
)
@click.version_option(version=__version__)
def main(limit: int, width: int, lines: int) -> None:
    data = biobio.last_news(limit=limit)

    # Reverse the data to show the latest news first
    data = data[::-1]

    for new in data:
        title = f"{new.post_hour} {get_cleaned(new.post_title)}"
        clickable_title = make_clickable(new.post_URL, title)
        click.secho(clickable_title, fg="yellow")
        text_lines = post_or_ia(new.post_content, new.resumen_de_ia, lines, width)
        for line in text_lines:
            click.echo(get_cleaned(line))
        click.echo("")


if __name__ == "__main__":
    main()
