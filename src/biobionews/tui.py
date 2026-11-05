import webbrowser
from datetime import datetime
from typing import List, Optional

import click
from rich.style import Style
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Static

from . import biobio
from .utils import get_cleaned, post_or_ia

MIN_WIDTH = 20
CHROME = 16  # scrollbar, padding, item border/padding and hour gutter
REFRESH_SECONDS = 60


class NewsList(VerticalScroll):
    """Scroll container that never takes focus, so up/down move the selection."""

    can_focus = False


class NewsItem(Horizontal):
    def __init__(self, url: str, hour: str, title: str, body: str) -> None:
        super().__init__()
        self.url = url
        self.hour = hour
        self.title_text = title
        self.body_text = body

    def compose(self) -> ComposeResult:
        yield Static(self.hour, classes="hour")
        with Vertical(classes="text"):
            yield Static(
                Text(self.title_text, style=Style(link=self.url)), classes="title"
            )
            yield Static(Text(self.body_text), classes="body")


class NewsApp(App[None]):
    TITLE = "BioBioNews"
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen { align-horizontal: center; }
    #news { width: 100%; padding: 0 1; }
    NewsItem { height: auto; padding: 0 1; margin-top: 1; border: round transparent; }
    NewsItem.-selected { border: round $warning; background: $boost; }
    NewsItem .hour { width: 7; color: $warning; text-style: bold; }
    NewsItem .text { height: auto; width: 1fr; }
    NewsItem .title { text-style: bold; }
    NewsItem .body { color: $text-muted; }
    NewsItem.-selected .body { color: $text; }
    .status { color: $text-muted; }
    """
    BINDINGS = [
        ("r", "refresh", "Actualizar"),
        ("q", "quit", "Salir"),
        ("up", "move(-1)", "Anterior"),
        ("down", "move(1)", "Siguiente"),
        ("enter", "open", "Abrir"),
    ]

    def __init__(
        self, limit: int = 10, lines: int = 5, width: Optional[int] = None
    ) -> None:
        super().__init__()
        # None: use the full terminal width
        self.max_width = max(width, MIN_WIDTH) if width else None
        self.news: List[biobio.New] = []
        self.limit = limit
        self.lines = lines
        self.selected = -1  # -1: not chosen yet, start on the newest (last)

    def compose(self) -> ComposeResult:
        yield Header()
        yield NewsList(Static("Cargando...", classes="status"), id="news")
        yield Footer()

    def on_mount(self) -> None:
        if self.max_width:
            for selector in ("Header", "#news", "Footer"):
                self.query_one(selector).styles.max_width = self.max_width
        self.action_refresh()
        self.set_interval(REFRESH_SECONDS, self.action_refresh)

    @property
    def text_width(self) -> int:
        width = self.max_width or self.size.width
        return max(min(width, self.size.width) - CHROME, MIN_WIDTH)

    def on_resize(self) -> None:
        if self.news:
            self.call_later(self.render_news)

    def action_refresh(self) -> None:
        self.sub_title = "Actualizando..."
        self.fetch()

    def items(self) -> List[NewsItem]:
        return list(self.query(NewsItem))

    def select(self, index: int) -> None:
        items = self.items()
        if not items:
            return
        self.selected = len(items) - 1 if index < 0 else min(index, len(items) - 1)
        for position, item in enumerate(items):
            item.set_class(position == self.selected, "-selected")
        container = self.query_one("#news", NewsList)
        if self.selected == 0:
            container.scroll_home(animate=False)
        elif self.selected == len(items) - 1:
            container.scroll_end(animate=False)
        else:
            items[self.selected].scroll_visible(animate=False)

    def action_move(self, delta: int) -> None:
        self.select(self.selected + delta)

    def action_open(self) -> None:
        items = self.items()
        if items:
            webbrowser.open(items[self.selected].url)

    @work(thread=True, exclusive=True)
    def fetch(self) -> None:
        try:
            news = biobio.last_news(limit=self.limit)
        except (click.ClickException, Exception) as error:
            message = getattr(error, "message", None) or str(error)
            self.call_from_thread(self.show_error, message)
            return
        self.call_from_thread(self.show_news, news)

    def show_error(self, message: str) -> None:
        self.sub_title = f"Error al actualizar ({datetime.now():%H:%M:%S})"
        self.notify(message, severity="error")

    async def show_news(self, news: List[biobio.New]) -> None:
        self.news = news
        await self.render_news()
        self.sub_title = f"Actualizado {datetime.now():%H:%M:%S}"

    async def render_news(self) -> None:
        container = self.query_one("#news", NewsList)
        items: List[NewsItem] = []
        for new in self.news:
            title = get_cleaned(new.post_title)
            text = post_or_ia(
                new.post_content, new.resumen_de_ia, self.lines, self.text_width
            )
            body = "\n".join(get_cleaned(line) for line in text)
            items.append(NewsItem(new.post_URL, new.post_hour, title, body))
        await container.remove_children()
        await container.mount_all(items)
        self.select(self.selected)
