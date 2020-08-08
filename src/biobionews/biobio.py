from dataclasses import dataclass
from typing import List

import click
import desert
import marshmallow
import requests

API_URL = "https://www.biobiochile.cl/lista/api/get-todo?limit={limit}"


@dataclass
class New:
    post_hour: str
    post_title: str
    post_content: str


schema = desert.schema(New, meta={"unknown": marshmallow.EXCLUDE}, many=True)


def last_news(limit: int = 10) -> List[New]:
    url = API_URL.format(limit=limit)

    try:
        with requests.get(url) as response:
            response.raise_for_status()
            data = response.json()
            data.reverse()
            return schema.load(data)
    except (requests.RequestException, marshmallow.ValidationError) as error:
        message = str(error)
        raise click.ClickException(message)
