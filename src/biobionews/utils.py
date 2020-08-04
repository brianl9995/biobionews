import re
import textwrap
from bs4 import BeautifulSoup


def get_cleaned(str):
    print(BeautifulSoup(str, features="html.parser"))


def clean_and_short(html, lines=5):
    return short_string(cleanhtml(html), lines)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()


def short_string(str, lines):
    wrapper = textwrap.TextWrapper(width=90)
    return wrapper.wrap(text=str)[:lines]
