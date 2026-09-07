#!/usr/bin/env python3
"""Fetch raw robotics intelligence for the Robotic Research Weekly project.

Sources: arXiv cs.RO, Google News RSS, authoritative RSS feeds, and Composio news
search as a fallback. Saves structured JSON to data/YYYY-MM-DD-raw-data.json.
"""
import json
import os
import re
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from html import unescape

ROOT = os.path.expanduser("~/robot-research-weekly")
DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Use UTC date for the fetch_date and rolling window.
today = datetime.now(timezone.utc).date()
last_friday = today - timedelta(days=7)

OUTPUT = os.path.join(DATA_DIR, f"{today}-raw-data.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}


def parse_date(s):
    """Parse ISO-8601 or RSS date strings into a timezone-aware datetime."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
    # Handle RSS dates that use a named timezone abbreviation like GMT/UTC
    norm = s.strip()
    for tz_name, offset in (("GMT", "+0000"), ("UTC", "+0000"), ("EST", "-0500"), ("EDT", "-0400")):
        if norm.endswith(tz_name):
            norm = norm[: -len(tz_name)].rstrip() + " " + offset
            break
    try:
        return datetime.strptime(norm, "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        return None


def is_within_week(dt):
    if not dt:
        return False
    return last_friday <= dt.date() <= today


def clean_title(t):
    return unescape(t or "").replace("\n", " ").strip()


def clean_summary(s):
    return re.sub(r"<[^>]+>", "", unescape(s or "")).replace("\n", " ").strip()[:400]


items = []


def add_item(title, url, published, entity, category, typ, summary):
    if not title or not url:
        return
    published_str = ""
    if isinstance(published, str) and published:
        published_str = published
    else:
        dt = parse_date(published) if published else None
        if dt:
            published_str = dt.isoformat()
    items.append({
        "title": clean_title(title),
        "url": url.strip(),
        "published_date": published_str,
        "entity": entity.strip(),
        "category": category,
        "type": typ,
        "summary": clean_summary(summary),
    })


def fetch_arxiv():
    print("Fetching arXiv cs.RO...")
    url = (
        "https://export.arxiv.org/api/query?search_query=cat:cs.RO"
        "&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending"
    )
    try:
        r = requests.get(url, timeout=45, headers=HEADERS)
        feed = feedparser.parse(r.text)
        count = 0
        for entry in feed.entries:
            dt = parse_date(entry.get("published", "")) or parse_date(entry.get("updated", ""))
            if dt and is_within_week(dt):
                add_item(
                    entry.get("title", ""),
                    entry.get("link", ""),
                    dt.isoformat(),
                    "arXiv cs.RO",
                    "机构",
                    "论文",
                    entry.get("summary", ""),
                )
                count += 1
        print(f"  -> {count} arXiv papers this week")
    except Exception as e:
        print(f"arXiv error: {e}")


# Google News queries mapped to the primary entity they represent.
GOOGLE_NEWS_QUERIES = {
    "Boston Dynamics": ["Boston Dynamics"],
    "NVIDIA": ["NVIDIA robotics"],
    "Google DeepMind": ["Google DeepMind robotics"],
    "Figure AI": ["Figure AI"],
    "Agility Robotics": ["Agility Robotics"],
    "Tesla Optimus": ["Tesla Optimus robot"],
    "Intuitive Surgical": ["Intuitive Surgical"],
    "ABB Robotics": ["ABB Robotics"],
    "FANUC": ["FANUC robot"],
    "Universal Robots": ["Universal Robots"],
    "Amazon Robotics": ["Amazon Robotics"],
    "Unitree": ["Unitree robot"],
    "UBTECH": ["UBTECH robot"],
    "AGIBOT": ["智元机器人"],
    "Fourier Intelligence": ["Fourier Intelligence robot"],
    "CMU": ["Carnegie Mellon robotics"],
    "MIT": ["MIT robotics"],
    "Stanford": ["Stanford robotics"],
    "ETH Zurich": ["ETH Zurich robotics"],
    "Georgia Tech": ["Georgia Tech robotics"],
    "UC Berkeley": ["UC Berkeley robotics"],
    "KAIST": ["KAIST robotics"],
    "IEEE Spectrum": ["IEEE Spectrum robotics"],
    "The Robot Report": ["The Robot Report"],
    "Robohub": ["Robohub"],
    "New Atlas Robotics": ["New Atlas robotics"],
    "Phys.org Robotics": ["Phys.org robotics"],
}


def fetch_google_news():
    from urllib.parse import quote
    for entity, qlist in GOOGLE_NEWS_QUERIES.items():
        q = qlist[0]
        try:
            url = (
                f"https://news.google.com/rss/search?"
                f"q={quote(q)}&hl=en-US&gl=US&ceid=US:en"
            )
            r = requests.get(url, timeout=15, headers=HEADERS)
            feed = feedparser.parse(r.text)
            count = 0
            for entry in feed.entries:
                dt = parse_date(entry.get("published", ""))
                if dt and is_within_week(dt):
                    category = "公司"
                    if entity in {"CMU", "MIT", "Stanford", "ETH Zurich", "Georgia Tech", "UC Berkeley", "KAIST"}:
                        category = "机构"
                    if entity in {"IEEE Spectrum", "The Robot Report", "Robohub", "New Atlas Robotics", "Phys.org Robotics"}:
                        category = "媒体"
                    add_item(
                        entry.get("title", ""),
                        entry.get("link", ""),
                        dt.isoformat(),
                        entity,
                        category,
                        "其他",
                        entry.get("summary", ""),
                    )
                    count += 1
            print(f"  Google News {entity}: {count} items")
        except Exception as e:
            print(f"Google News error {entity}: {e}")


RSS_SOURCES = {
    "IEEE Spectrum": "https://spectrum.ieee.org/rss/topic/robotics",
    "The Robot Report": "https://www.therobotreport.com/feed",
    "Robohub": "https://robohub.org/feed/",
    "Robotics Business Review": "https://www.roboticsbusinessreview.com/feed/",
    "Phys.org - Robotics": "https://phys.org/rss/technology/robotics/",
    "New Atlas - Robotics": "https://newatlas.com/robotics/feed/",
    "ROBO Global": "https://roboglobal.com/feed/",
}


def fetch_rss():
    for source, url in RSS_SOURCES.items():
        try:
            r = requests.get(url, timeout=20, headers=HEADERS)
            feed = feedparser.parse(r.text)
            count = 0
            for entry in feed.entries:
                dt = parse_date(entry.get("published", ""))
                if dt and is_within_week(dt):
                    add_item(
                        entry.get("title", ""),
                        entry.get("link", ""),
                        dt.isoformat(),
                        source,
                        "媒体",
                        "其他",
                        entry.get("summary", ""),
                    )
                    count += 1
            print(f"  RSS {source}: {count} items")
        except Exception as e:
            print(f"RSS error {source}: {e}")


def deduplicate():
    seen = set()
    uniq = []
    for it in items:
        if it["url"] not in seen:
            seen.add(it["url"])
            uniq.append(it)
    return uniq


def main():
    fetch_arxiv()
    fetch_google_news()
    fetch_rss()
    uniq = deduplicate()
    out = {"fetch_date": today.isoformat(), "total_items": len(uniq), "items": uniq}
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(uniq)} items to {OUTPUT}")


if __name__ == "__main__":
    main()
