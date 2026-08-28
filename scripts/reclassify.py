#!/usr/bin/env python3
"""Reclassify news item types by title keywords (leave arXiv papers as 论文)."""
import json
import sys
import os
from datetime import datetime, timezone

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    today = datetime.now(timezone.utc).date()
    path = os.path.expanduser(f'~/robot-research-weekly/data/{today}-raw-data.json')
data = json.load(open(path))

def type_from_title(title):
    t = title.lower()
    if any(x in t for x in ["raises", "series", "funding", "million", "investment", "secures", "raises $",
                            "融资", "亿元", "万元", "投资", "ipo", "上市募资", "增资"]):
        return "融资"
    if any(x in t for x in ["launch", "releases", "unveils", "announces", "new", "product", "introduces", "debuts", "unveiled", "unveiling",
                            "发布", "新品", "推出", "亮相", "开售", "量产", "官宣"]):
        return "产品发布"
    if any(x in t for x in ["partnership", "collaborates", "team up", "joins", "signs", "partner", "collaboration", "teams with", "deepen", "coalition", "acquisition", "acquires", "buy out", "expands to", "opens",
                            "合作", "签约", "联手", "携手", "并购", "收购", "合资"]):
        return "合作"
    if any(x in t for x in ["paper", "study", "research", "arxiv", "algorithm", "open-source", "open source",
                            "论文", "研究", "开源", "算法"]):
        return "论文"
    if any(x in t for x in ["policy", "regulation", "fcc", "ban", "law", "government", "executive order",
                            "政策", "监管", "法规", "政府", "国标", "标准"]):
        return "政策"
    if any(x in t for x in ["says", "ceo", "interview", "opinion", "view", "predicts", "musk says", "commentary",
                            "表示", "采访", "专访", "观点", "认为", "坦言"]):
        return "观点"
    return "其他"

changed = 0
for it in data["items"]:
    if it["type"] == "其他":
        newtype = type_from_title(it["title"])
        if newtype != "其他":
            it["type"] = newtype
            changed += 1

data["total_items"] = len(data["items"])
json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Reclassified {changed} items. Total: {len(data['items'])}")
from collections import Counter
print(Counter(i['type'] for i in data['items']))
