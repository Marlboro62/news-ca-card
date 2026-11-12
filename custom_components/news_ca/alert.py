"""Alerte AMBER : lue dans le flux public du système national En Alerte (NAAD, Pelmorex).

Le flux Atom liste toutes les alertes diffusées au Canada (météo, urgences civiles, AMBER…) en français et en anglais.
Une Alerte AMBER est en cours tant qu'une entrée « event=amber », réelle (status=Actual), n'est ni expirée ni annulée.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import html
import re
from typing import Any
import xml.etree.ElementTree as ET

_ATOM = "{http://www.w3.org/2005/Atom}"
_TAGS = re.compile(r"<[^>]+>")
_SPACES = re.compile(r"\s+")
_EXPIRES = re.compile(r"Expires:\s*([0-9T:\-+.Z]+)", re.I)
_AREA = re.compile(r"Area:\s*(.+?)(?:<br|$)", re.I | re.S)
_DESC = re.compile(r"Description:\s*(.+?)(?:###|Expires:)", re.I | re.S)
_ENDED = re.compile(r"\b(ended|terminée?|annulée?|cancelled|canceled|levée)\b", re.I)
# sans date d'expiration lisible, une alerte reste affichée au plus 24 heures
MAX_AGE = timedelta(hours=24)


def _text(value: str | None) -> str:
    return _SPACES.sub(" ", html.unescape(_TAGS.sub(" ", value or ""))).strip()


def _date(value: str | None) -> datetime | None:
    try:
        when = datetime.fromisoformat((value or "").strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return when if when.tzinfo else when.replace(tzinfo=UTC)


def parse_alerts(data: bytes) -> list[dict[str, Any]]:
    """Entrées AMBER du flux NAAD. ValueError si le flux est illisible."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as err:
        raise ValueError(f"flux illisible ({err})") from err
    out: list[dict[str, Any]] = []
    for entry in root.iter(f"{_ATOM}entry"):
        terms = dict(
            (t.split("=", 1) + [""])[:2] for t in (c.get("term") or "" for c in entry.iter(f"{_ATOM}category")) if "=" in t
        )
        if terms.get("event", "").lower() != "amber":
            continue
        raw = entry.findtext(f"{_ATOM}summary") or ""
        summary = html.unescape(raw)
        link = next((ln.get("href") for ln in entry.iter(f"{_ATOM}link") if ln.get("rel", "alternate") == "alternate"), None)
        desc = _DESC.search(summary)
        area = _AREA.search(summary)
        expires = _EXPIRES.search(summary)
        out.append({
            "id": (entry.findtext(f"{_ATOM}id") or "").strip(),
            "title": _text(entry.findtext(f"{_ATOM}title")),
            "summary": _text(desc.group(1) if desc else summary)[:1200],
            "area": _text(area.group(1)) if area else "",
            "updated": _date(entry.findtext(f"{_ATOM}updated")),
            "expires": _date(expires.group(1)) if expires else None,
            "status": terms.get("status", ""),
            "msg_type": terms.get("msgType", ""),
            "language": terms.get("language", ""),
            "author": _text(entry.findtext(f"{_ATOM}author/{_ATOM}name")),
            "url": link if link and link.startswith(("https://", "http://")) else None,
        })
    return out


def detect(entries: list[dict[str, Any]], now: datetime | None = None) -> dict[str, Any]:
    """État de l'Alerte AMBER : {"active": bool, ...détails, en français de préférence}."""
    now = now or datetime.now(UTC)
    real = [e for e in entries if e["status"] == "Actual" and e["updated"]]
    ends = [e["updated"] for e in real if e["msg_type"] == "Cancel" or _ENDED.search(e["title"])]
    live = [
        e for e in real
        if e["msg_type"] in ("Alert", "Update") and not _ENDED.search(e["title"])
        and (e["expires"] or e["updated"] + MAX_AGE) > now and e["updated"] > now - MAX_AGE
    ]
    if not live:
        return {"active": False, "ended": max(ends).isoformat() if ends else None}
    start = min(e["updated"] for e in live)
    if ends and max(ends) >= max(e["updated"] for e in live):
        return {"active": False, "ended": max(ends).isoformat()}
    # dernière version de l'alerte, en français si elle existe
    latest = max(e["updated"] for e in live)
    recent = [e for e in live if e["updated"] >= latest - timedelta(minutes=10)]
    best = next((e for e in recent if e["language"].startswith("fr")), recent[0])
    expires = [e["expires"] for e in live if e["expires"]]
    return {
        "active": True,
        # identifiant stable de l'alerte : sa première diffusion (les mises à jour en changent l'identifiant)
        "id": (min(live, key=lambda e: e["updated"])["id"].rsplit("/", 1)[-1] or best["title"])[:80],
        "since": start.isoformat(),
        "expires": max(expires).isoformat() if expires else None,
        "title": best["title"],
        "summary": best["summary"],
        "area": best["area"],
        "image": None,
        "url": best["url"],
        "source": best["author"] or "En Alerte",
        "sources": sorted({e["author"] for e in live if e["author"]}) or ["En Alerte"],
    }
