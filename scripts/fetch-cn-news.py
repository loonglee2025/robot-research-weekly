#!/usr/bin/env python3
"""Supplementary Google News fetch with zh-CN locale for Chinese entities."""
import json, os, re, time
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from html import unescape
from urllib.parse import quote

ROOT = os.path.expanduser("~/robot-research-weekly")
today = datetime.now(timezone.utc).date()
last_friday = today - timedelta(days=7)
OUTPUT = os.path.join(ROOT, "data", f"{today}-raw-data.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ResearchBot/1.0)"}

QUERIES = [
    ("乐聚机器人", "LimX Dynamics/Leju"),
    ("众擎机器人", "众擎机器人"),
    ("拓斯达", "拓斯达"),
    ("智元机器人", "AGIBOT"),
    ("宇树科技", "Unitree"),
    ("优必选机器人", "UBTECH"),
    ("傅利叶智能", "Fourier Intelligence"),
]

def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
    norm = s.strip()
    for tz, off in (("GMT","+0000"),("UTC","+0000"),("EST","-0500"),("EDT","-0400"),("CST","+0800")):
        if norm.endswith(tz):
            norm = norm[: -len(tz)].rstrip() + " " + off
            break
    try:
        return datetime.strptime(norm, "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        return None

def clean(s):
    return re.sub(r"<[^>]+>", "", unescape(s or "")).replace("\n", " ").strip()

def type_from_title(title):
    t = title.lower()
    if any(x in t for x in ["融资", "raises", "funding", "million", "亿元", "投资"]): return "融资"
    if any(x in t for x in ["发布", "launch", "unveils", "announces", "新品", "推出", "上市"]): return "产品发布"
    if any(x in t for x in ["合作", "partnership", "签约", "联手", "collaborat"]): return "合作"
    if any(x in t for x in ["论文", "paper", "research", "arxiv", "开源"]): return "论文"
    if any(x in t for x in ["政策", "policy", "regulation", "政府"]): return "政策"
    if any(x in t for x in ["表示", "采访", "观点", "says", "interview"]): return "观点"
    return "其他"

def main():
    data = json.load(open(OUTPUT, encoding="utf-8"))
    existing = {it["url"] for it in data["items"]}
    new_items = []
    for q, entity in QUERIES:
        url = f"https://news.google.com/rss/search?q={quote(q)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        try:
            r = requests.get(url, timeout=20, headers=HEADERS)
            feed = feedparser.parse(r.text)
            n = 0
            for e in feed.entries:
                dt = parse_date(e.get("published", ""))
                if dt and last_friday <= dt.date() <= today:
                    link = (e.get("link", "") or "").strip()
                    if link and link not in existing and link not in {i["url"] for i in new_items}:
                        new_items.append({
                            "title": clean(e.get("title", "")),
                            "url": link,
                            "published_date": dt.isoformat(),
                            "entity": entity,
                            "category": "公司",
                            "type": type_from_title(e.get("title", "")),
                            "summary": clean(e.get("summary", ""))[:400],
                        })
                        n += 1
            print(f"{entity}: {n} new")
        except Exception as ex:
            print(f"ERROR {entity}: {ex}")
        time.sleep(0.5)
    data["items"].extend(new_items)
    seen, uniq = set(), []
    for it in data["items"]:
        if it["url"] not in seen:
            seen.add(it["url"]); uniq.append(it)
    data["items"] = uniq
    data["total_items"] = len(uniq)
    json.dump(data, open(OUTPUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Added {len(new_items)} items. Total: {len(uniq)}")

if __name__ == "__main__":
    main()
