"""Constantes de l'intégration Actualités Canada."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "news_ca"
VERSION: Final = "0.1.0b4"
NAME: Final = "Actualités Canada"

CONF_SOURCES: Final = "sources"
CONF_CUSTOM: Final = "custom_feeds"
CONF_ITEMS: Final = "items"
CONF_SCAN_MINUTES: Final = "scan_minutes"

DEFAULT_SOURCES: Final = ["radiocanada", "lapresse", "cbc", "globalnews"]
DEFAULT_ITEMS: Final = 20
MIN_ITEMS: Final = 5
MAX_ITEMS: Final = 50
DEFAULT_SCAN_MINUTES: Final = 15
MIN_SCAN_MINUTES: Final = 10

# Médias proposés : flux RSS publics (titres et résumés), l'article reste sur le site du média
SOURCES: Final[dict[str, dict[str, str]]] = {
    # Québec et médias francophones
    "radiocanada": {"name": "Radio-Canada", "url": "https://ici.radio-canada.ca/rss/4159", "site": "https://ici.radio-canada.ca/info"},
    "lapresse": {"name": "La Presse", "url": "https://www.lapresse.ca/actualites/rss", "site": "https://www.lapresse.ca"},
    "ledevoir": {"name": "Le Devoir", "url": "https://www.ledevoir.com/rss/manchettes.xml", "site": "https://www.ledevoir.com"},
    "tvanouvelles": {"name": "TVA Nouvelles", "url": "https://www.tvanouvelles.ca/rss.xml", "site": "https://www.tvanouvelles.ca"},
    "journaldemontreal": {"name": "Le Journal de Montréal", "url": "https://www.journaldemontreal.com/rss.xml", "site": "https://www.journaldemontreal.com"},
    # Médias anglophones
    "cbc": {"name": "CBC News", "url": "https://www.cbc.ca/webfeed/rss/rss-topstories", "site": "https://www.cbc.ca/news"},
    "globalnews": {"name": "Global News", "url": "https://globalnews.ca/feed/", "site": "https://globalnews.ca"},
    "globeandmail": {
        "name": "The Globe and Mail",
        "url": "https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/canada/",
        "site": "https://www.theglobeandmail.com",
    },
}

# Alerte AMBER : flux public En Alerte / NAAD (Pelmorex), deux serveurs (Québec, Toronto)
ALERT_FEEDS: Final = ("https://rss.naad-adna.pelmorex.com/", "https://rss1.naad-adna.pelmorex.com/")
ALERT_MINUTES: Final = 5

# Fichier de la carte, servi par Home Assistant et chargé dans l'interface
CARD_URL: Final = f"/{DOMAIN}/news-ca-card.js"
CARD_FILE: Final = "frontend/news-ca-card.js"
