#!/usr/bin/env python3
import json
data = json.load(open('/home/hermes/robot-research-weekly/data/2026-08-07-raw-data.json'))
# Show non-arXiv, non-其他 type items sample for quality check
types = ["融资", "产品发布", "合作", "政策", "观点"]
for t in types:
    items = [i for i in data["items"] if i["type"] == t and i["entity"] != "arXiv cs.RO"]
    print(f"=== {t} ({len(items)}) ===")
    for i in items[:20]:
        print(f"  [{i['entity']}] {i['title'][:90]}")
    print()
