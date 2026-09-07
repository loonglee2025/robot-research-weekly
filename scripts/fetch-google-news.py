#!/usr/bin/env python3
"""Fetch past-week Google News RSS for tracked entities and append to raw-data JSON."""
import json
import os
import re
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from html import unescape
import time
from urllib.parse import quote

ROOT = os.path.expanduser("~/robot-research-weekly")
DATA_DIR = os.path.join(ROOT, "data")
today = datetime.now(timezone.utc).date()
last_friday = today - timedelta(days=7)
OUTPUT = os.path.join(DATA_DIR, f"{today}-raw-data.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
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


# Entity query definitions (search_term, entity_name, category)
ENTITIES = [
    # Western companies
    ("Boston Dynamics", "Boston Dynamics", "公司"),
    ("NVIDIA robotics", "NVIDIA", "公司"),
    ("Google DeepMind robotics", "Google DeepMind", "公司"),
    ("Figure AI", "Figure AI", "公司"),
    ("Agility Robotics", "Agility Robotics", "公司"),
    ("Tesla Optimus robot", "Tesla Optimus", "公司"),
    ("Intuitive Surgical", "Intuitive Surgical", "公司"),
    ("ABB Robotics", "ABB Robotics", "公司"),
    ("FANUC robot", "FANUC", "公司"),
    ("Universal Robots", "Universal Robots", "公司"),
    ("Amazon Robotics", "Amazon Robotics", "公司"),
    # Chinese companies
    ("Unitree robot", "Unitree", "公司"),
    ("UBTECH robot", "UBTECH", "公司"),
    ("智元机器人", "AGIBOT", "公司"),
    ("傅利叶智能 robot", "Fourier Intelligence", "公司"),
    ("乐聚机器人", "LimX Dynamics", "公司"),
    ("众擎机器人", "众擎机器人", "公司"),
    ("拓斯达 robot", "拓斯达", "公司"),
    # Institutions
    ("Carnegie Mellon robotics", "Carnegie Mellon University", "机构"),
    ("MIT robotics", "MIT", "机构"),
    ("Stanford robotics", "Stanford University", "机构"),
    ("ETH Zurich robotics", "ETH Zurich", "机构"),
    ("Georgia Tech robotics", "Georgia Tech", "机构"),
    ("UC Berkeley robotics", "UC Berkeley", "机构"),
    ("KAIST robotics", "KAIST", "机构"),
    ("University of Tokyo robotics", "University of Tokyo", "机构"),
    ("University of Oxford robotics", "University of Oxford", "机构"),
    ("Technical University of Munich robotics", "Technical University of Munich", "机构"),
    ("Imperial College London robotics", "Imperial College London", "机构"),
    # Media (handled separately already via RSS but add as bonus)
    ("IEEE Spectrum robotics", "IEEE Spectrum", "媒体"),
    ("The Robot Report", "The Robot Report", "媒体"),
    ("Robohub", "Robohub", "媒体"),
    ("New Atlas robotics", "New Atlas", "媒体"),
    ("Phys.org robotics", "Phys.org", "媒体"),
]


def type_from_title(title):
    t = title.lower()
    if any(x in t for x in ["raises", "series", "funding", "million", "investment"]):
        return "融资"
    if any(x in t for x in ["launch", "releases", "unveils", "announces", "new", "product", "introduces"]):
        return "产品发布"
    if any(x in t for x in ["partnership", "collaborates", "team up", "joins", "signs"]):
        return "合作"
    if any(x in t for x in ["paper", "study", "research", "arxiv", "algorithm"]):
        return "论文"
    if any(x in t for x in ["policy", "regulation", "fcc", "ban", "law", "government"]):
        return "政策"
    if any(x in t for x in ["says", "ceo", "interview", "opinion", "view", "predicts"]):
        return "观点"
    return "其他"


def fetch_for_entity(q, entity, category):
    found = []
    try:
        url = (
            f"https://news.google.com/rss/search?"
            f"q={quote(q)}&hl=en-US&gl=US&ceid=US:en"
        )
        r = requests.get(url, timeout=20, headers=HEADERS)
        feed = feedparser.parse(r.text)
        for entry in feed.entries:
            dt = parse_date(entry.get("published", ""))
            if dt and is_within_week(dt):
                found.append({
                    "title": clean_title(entry.get("title", "")),
                    "url": (entry.get("link", "") or "").strip(),
                    "published_date": dt.isoformat(),
                    "entity": entity,
                    "category": category,
                    "type": type_from_title(entry.get("title", "")),
                    "summary": clean_summary(entry.get("summary", "")),
                })
        if found:
            print(f"  {entity}: {len(found)} items")
        else:
            # show most recent date found
            recent = None
            for entry in feed.entries[:3]:
                dt = parse_date(entry.get("published", ""))
                if dt and (recent is None or dt > recent):
                    recent = dt
            print(f"  {entity}: 0 items (recent: {recent.date() if recent else 'none'})")
    except Exception as e:
        print(f"  ERROR {entity}: {e}")
    return found


def main():
    # Load existing raw data
    with open(OUTPUT, "r", encoding="utf-8") as f:
        data = json.load(f)
    existing_urls = {it["url"] for it in data["items"]}
    new_items = []

    for q, entity, category in ENTITIES:
        for item in fetch_for_entity(q, entity, category):
            if item["url"] not in existing_urls and item["url"] not in {i["url"] for i in new_items}:
                new_items.append(item)
        time.sleep(0.5)

    print(f"\nTotal new items from Google News: {len(new_items)}")
    data["items"].extend(new_items)
    # Deduplicate
    seen = set()
    uniq = []
    for it in data["items"]:
        if it["url"] not in seen:
            seen.add(it["url"])
            uniq.append(it)
    data["items"] = uniq
    data["total_items"] = len(uniq)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(uniq)} items to {OUTPUT}")


if __name__ == "__main__":
    main()
