import click
import requests

API_URL = "https://www.biobiochile.cl/lista/api/get-todo?limit={limit}"


def last_news(limit=10):
    url = API_URL.format(limit=limit)

    try:
        with requests.get(url) as response:
            response.raise_for_status()
            data = response.json()
            data.reverse()
            return data
    except requests.RequestException as error:
        message = str(error)
        raise click.ClickException(message)
