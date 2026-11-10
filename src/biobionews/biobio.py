from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import click
import desert
import marshmallow
import requests

API_URL = "https://www.biobiochile.cl/lista/api/get-todo?limit={limit}"

# Category slugs (primary, secondary or any in post_categories) to hide
EXCLUDED_CATEGORIES = frozenset(
    {
        # Futbol nacional
        "futbol",
        "futbol-nacional",
        "colo-colo",
        "universidad-catolica",
        "universidad-de-chile",
        "la-roja",
        # Futbol internacional
        "futbol-internacional",
        "notas-futbol-internacional",
        "chilenos-en-el-exterior",
        # Espectaculos y farandula
        "espectaculos-y-tv",
        "notas-espectaculos-tv",
        "celebridades",
        "tv",
        "cine-y-series",
        "notas-cortas",
        "dopamina",
    }
)

# URL path prefixes to hide, catches subcategories missing from the list above
EXCLUDED_PATHS = (
    "/noticias/deportes/futbol/",
    "/noticias/deportes/futbol-internacional/",
    "/noticias/espectaculos-y-tv/",
    "/noticias/dopamina/",
)


@dataclass
class New:
    post_hour: str
    post_title: str
    post_content: str
    resumen_de_ia: str
    post_URL: str
    en_desarrollo: Optional[bool] = False
    nota_en_vivo: Optional[bool] = False

    @property
    def live_label(self) -> Optional[str]:
        """Badge for live or developing news, None for regular news."""
        if self.nota_en_vivo:
            return "EN VIVO"
        if self.en_desarrollo:
            return "EN DESARROLLO"
        return None


schema = desert.schema(New, meta={"unknown": marshmallow.EXCLUDE}, many=True)


def is_live(item: Dict[str, Any]) -> bool:
    return bool(item.get("en_desarrollo") or item.get("nota_en_vivo"))


def is_excluded(item: Dict[str, Any]) -> bool:
    slugs = {item.get("primary"), item.get("secondary")}
    slugs.update(category.get("slug") for category in item.get("post_categories") or [])
    if slugs & EXCLUDED_CATEGORIES:
        return True
    url = item.get("post_URL") or ""
    return any(path in url for path in EXCLUDED_PATHS)


def select_news(data: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    """Drop excluded news and keep the newest `limit` regular ones.

    Live news are kept even beyond `limit`, since they stay pinned while they last.
    """
    selected = []
    regular = 0
    for item in data:
        if is_excluded(item):
            continue
        if is_live(item):
            selected.append(item)
        elif regular < limit:
            selected.append(item)
            regular += 1
    return selected


def last_news(limit: int = 10) -> List[New]:
    # Ask for extra news so there are still `limit` left after filtering
    url = API_URL.format(limit=limit * 2 + 10)

    try:
        with requests.get(url) as response:
            response.raise_for_status()
            data = response.json()
            data = select_news(data, limit)
            data.reverse()
            return schema.load(data)
    except (requests.RequestException, marshmallow.ValidationError) as error:
        message = str(error)
        raise click.ClickException(message)
