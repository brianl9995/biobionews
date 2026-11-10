from typing import Any, Dict, List
from unittest.mock import Mock

import pytest

from biobionews import biobio


def make_item(title: str, primary: str = "nacional", **extra: Any) -> Dict[str, Any]:
    item = {
        "post_title": title,
        "post_hour": "10:20",
        "post_content": "bar",
        "post_URL": f"https://www.biobiochile.cl/noticias/{primary}/x/{title}.shtml",
        "resumen_de_ia": "",
        "primary": primary,
        "secondary": "",
        "post_categories": [],
    }
    item.update(extra)
    return item


def set_response(mock: Mock, items: List[Dict[str, Any]]) -> None:
    mock.return_value.__enter__.return_value.json.return_value = items


def test_last_news_requests_more_than_limit(mock_requests_get: Mock) -> None:
    biobio.last_news(limit=15)
    args, _ = mock_requests_get.call_args
    assert "limit=40" in args[0]


def test_last_news_trims_to_limit_keeping_newest(mock_requests_get: Mock) -> None:
    # API returns newest first; result is oldest first
    set_response(mock_requests_get, [make_item(str(n)) for n in range(5)])
    news = biobio.last_news(limit=3)
    assert [new.post_title for new in news] == ["2", "1", "0"]


@pytest.mark.parametrize(
    "item",
    [
        make_item("a", primary="futbol", secondary="colo-colo"),
        make_item("b", primary="futbol-internacional"),
        make_item("c", primary="espectaculos-y-tv", secondary="celebridades"),
        make_item("d", primary="notas-cortas", secondary="dopamina"),
        make_item("e", primary="servicios", post_categories=[{"slug": "la-roja"}]),
        make_item(
            "f",
            primary="otra",
            post_URL="https://www.biobiochile.cl/noticias/deportes/futbol/audax/x.shtml",
        ),
    ],
)
def test_last_news_excludes_football_and_shows(
    mock_requests_get: Mock, item: Dict[str, Any]
) -> None:
    set_response(mock_requests_get, [item, make_item("ok")])
    news = biobio.last_news(limit=10)
    assert [new.post_title for new in news] == ["ok"]


def test_last_news_keeps_other_sports(mock_requests_get: Mock) -> None:
    set_response(
        mock_requests_get, [make_item("tenis", primary="deportes", secondary="tenis")]
    )
    assert len(biobio.last_news(limit=10)) == 1


def test_last_news_keeps_live_news_beyond_limit(mock_requests_get: Mock) -> None:
    items = [make_item(str(n)) for n in range(3)]
    items.append(make_item("live", en_desarrollo=True))
    set_response(mock_requests_get, items)
    news = biobio.last_news(limit=2)
    assert [new.post_title for new in news] == ["live", "1", "0"]
    assert news[0].live_label == "EN DESARROLLO"
    assert news[1].live_label is None


def test_live_label_prefers_en_vivo(mock_requests_get: Mock) -> None:
    set_response(
        mock_requests_get, [make_item("a", en_desarrollo=True, nota_en_vivo=True)]
    )
    assert biobio.last_news()[0].live_label == "EN VIVO"
