import re
import textwrap
from typing import List

from bs4 import BeautifulSoup


def get_cleaned(value: str) -> str:
    return str(BeautifulSoup(value, features="html.parser"))


def make_clickable(url: str, text: str) -> str:
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def clean_and_short(html: str, lines: int = 5, width: int = 180) -> List[str]:
    return short_string(cleanhtml(html), lines, width)


def post_or_ia(post: str, ia: str, lines: int = 5, width: int = 180) -> List[str]:
    if ia:
        return clean_and_short(ia, lines, width)
    return clean_and_short(post, lines, width)


def cleanhtml(raw_html: str) -> str:
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext.strip()


def short_string(str: str, lines: int, width: int) -> List[str]:
    wrapper = textwrap.TextWrapper(width=width)
    return wrapper.wrap(text=str)[:lines]
