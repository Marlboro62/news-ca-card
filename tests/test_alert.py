"""Alerte AMBER : lecture du flux En Alerte (NAAD) et état de l'alerte."""
from datetime import UTC, datetime, timedelta

from custom_components.news_ca.alert import detect, parse_alerts

NOW = datetime(2026, 11, 12, 12, 0, tzinfo=UTC)


def entry(event, title, minutes, msg="Alert", status="Actual", lang="fr-CA", expires_h=6, oid="1"):
    upd = (NOW - timedelta(minutes=minutes)).isoformat()
    exp = (NOW - timedelta(minutes=minutes) + timedelta(hours=expires_h)).isoformat()
    summary = (f"Description: Enfant de 7 ans vu pour la dernière fois à Laval.&lt;br&gt;&lt;br&gt;###&lt;br&gt;"
               f"Expires: {exp}&lt;br&gt;Originated from CAP Alert: x&lt;br&gt;Area: Laval")
    return f"""<entry><id>tag:rss.naad-adna.pelmorex.com,2026-11-12:feed.atom/urn:oid:{oid}</id><title>{title}</title>
<updated>{upd}</updated><author><name>Sûreté du Québec</name></author>
<link href="http://capcp2.naad-adna.pelmorex.com/2026-11-12/{oid}.xml" rel="alternate"/>
<summary type="html">{summary}</summary>
<category term="status={status}"/><category term="msgType={msg}"/><category term="language={lang}"/><category term="event={event}"/></entry>"""


def feed(*entries):
    return ('<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>NAAD</title>' + "".join(entries) + "</feed>").encode()


def test_alerte_amber_en_cours():
    data = feed(
        entry("rainfall", "avertissement jaune - pluie - en vigueur", 5),
        entry("amber", "Alerte AMBER - en vigueur", 30, oid="a1"),
        entry("amber", "AMBER Alert - in effect", 30, lang="en-CA", oid="a1en"),
    )
    entries = parse_alerts(data)
    assert len(entries) == 2  # la pluie est ignorée
    r = detect(entries, NOW)
    assert r["active"] and r["title"] == "Alerte AMBER - en vigueur" and r["area"] == "Laval"
    assert "Laval" in r["summary"] and r["source"] == "Sûreté du Québec" and r["id"]


def test_alerte_annulee_test_ou_expiree():
    assert not detect(parse_alerts(feed(
        entry("amber", "Alerte AMBER - en vigueur", 60),
        entry("amber", "Alerte AMBER - terminée", 5, msg="Cancel"),
    )), NOW)["active"]
    assert not detect(parse_alerts(feed(entry("amber", "Alerte AMBER - test", 5, status="Test"))), NOW)["active"]
    assert not detect(parse_alerts(feed(entry("amber", "Alerte AMBER", 8 * 60, expires_h=2))), NOW)["active"]


def test_flux_illisible():
    import pytest

    with pytest.raises(ValueError):
        parse_alerts(b"<html>")
