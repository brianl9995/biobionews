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
    def __init__(
        self,
        url: str,
        hour: str,
        title: str,
        body: str,
        live_label: Optional[str] = None,
    ) -> None:
        super().__init__(classes="-live" if live_label else "")
        self.url = url
        self.hour = hour
        self.title_text = title
        self.body_text = body
        self.live_label = live_label

    def compose(self) -> ComposeResult:
        yield Static(self.hour, classes="hour")
        with Vertical(classes="text"):
            title = Text()
            if self.live_label:
                title.append(f" ● {self.live_label} ", style="bold white on red")
                title.append(" ")
            title.append(self.title_text, style=Style(link=self.url))
            yield Static(title, classes="title")
            yield Static(Text(self.body_text), classes="body")


class NewsApp(App[None]):
    TITLE = "BioBioNews"
    ENABLE_COMMAND_PALETTE = False
    CSS = """
    Screen { align-horizontal: center; }
    #news { width: 100%; padding: 0 1; }
    #pinned {
        width: 100%; height: auto; max-height: 50%; padding: 0 1 1 1;
        border-bottom: heavy $error;
    }
    #pinned.-empty { display: none; }
    NewsItem { height: auto; padding: 0 1; margin-top: 1; border: round transparent; }
    NewsItem.-selected { border: round $warning; background: $boost; }
    NewsItem .hour { width: 7; color: $warning; text-style: bold; }
    NewsItem .text { height: auto; width: 1fr; }
    NewsItem .title { text-style: bold; }
    NewsItem .body { color: $text-muted; }
    NewsItem.-selected .body { color: $text; }
    NewsItem.-live { border: heavy $error; background: $error 15%; }
    NewsItem.-live .hour { color: $error; }
    NewsItem.-live .body { color: $text; }
    NewsItem.-live.-selected { border: heavy $warning; }
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
        yield NewsList(id="pinned", classes="-empty")
        yield NewsList(Static("Cargando...", classes="status"), id="news")
        yield Footer()

    def on_mount(self) -> None:
        if self.max_width:
            for selector in ("Header", "#pinned", "#news", "Footer"):
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
        item = items[self.selected]
        container = item.parent
        regular = list(container.query_children(NewsItem))
        if item is regular[0]:
            container.scroll_home(animate=False)
        elif item is regular[-1]:
            container.scroll_end(animate=False)
        else:
            item.scroll_visible(animate=False)

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
        pinned = self.query_one("#pinned", NewsList)
        container = self.query_one("#news", NewsList)
        live: List[NewsItem] = []
        items: List[NewsItem] = []
        for new in self.news:
            title = get_cleaned(new.post_title)
            text = post_or_ia(
                new.post_content, new.resumen_de_ia, self.lines, self.text_width
            )
            body = "\n".join(get_cleaned(line) for line in text)
            item = NewsItem(new.post_URL, new.post_hour, title, body, new.live_label)
            (live if new.live_label else items).append(item)
        # Newest live news first, pinned above the scrolling list
        live.reverse()
        await pinned.remove_children()
        await pinned.mount_all(live)
        pinned.set_class(not live, "-empty")
        await container.remove_children()
        await container.mount_all(items)
        self.select(self.selected)
