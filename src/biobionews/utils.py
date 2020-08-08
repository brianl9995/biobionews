import re
import textwrap
from typing import List

from bs4 import BeautifulSoup


def get_cleaned(value: str) -> str:
    return str(BeautifulSoup(value, features="html.parser"))


def clean_and_short(html: str, lines: int = 5) -> List[str]:
    return short_string(cleanhtml(html), lines)


def cleanhtml(raw_html: str) -> str:
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext.strip()


def short_string(str: str, lines: int) -> List[str]:
    wrapper = textwrap.TextWrapper(width=90)
    return wrapper.wrap(text=str)[:lines]
