import re
import requests
import textwrap


def main():
    r = requests.get('https://www.biobiochile.cl/lista/api/get-todo?limit=10')
    news = r.json()
    news.reverse()

    for new in news:
        print(new.get('post_hour', ''), new.get('post_title', '-'))
        lines = clean_and_short(new.get('post_content', ''))
        for line in lines:
            print(line)
        print()


def clean_and_short(html, lines=4):
    return short_string(cleanhtml(html), lines)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()


def short_string(str, lines):
    wrapper = textwrap.TextWrapper(width=80)
    return wrapper.wrap(text=str)[:lines]


if __name__ == "__main__":
    main()
