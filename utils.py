import re
import textwrap
from bs4 import BeautifulSoup


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_cleaned(str):
    print(BeautifulSoup(str, features="html.parser"))


def print_title(str):
    title = BeautifulSoup(str, features="html.parser")
    print(f"{bcolors.WARNING}{title}{bcolors.ENDC}")


def clean_and_short(html, lines=5):
    return short_string(cleanhtml(html), lines)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()


def short_string(str, lines):
    wrapper = textwrap.TextWrapper(width=90)
    return wrapper.wrap(text=str)[:lines]
