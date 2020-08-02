import requests

from utils import clean_and_short, print_title, print_cleaned


def main():
    r = requests.get('https://www.biobiochile.cl/lista/api/get-todo?limit=10')
    news = r.json()
    news.reverse()

    for new in news:
        print_title(new.get('post_hour', '') + ' ' + new.get('post_title', '-'))
        lines = clean_and_short(new.get('post_content', ''))
        for line in lines:
            print_cleaned(line)
        print()


if __name__ == "__main__":
    main()
