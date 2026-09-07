#!/usr/bin/env python3
import json
from collections import Counter

with open('/home/hermes/robot-research-weekly/data/2026-07-24-raw-data.json') as f:
    data = json.load(f)

print(f'Total: {data["total_items"]}')
ents = Counter(i['entity'] for i in data['items'])
print('Entities:')
for e, c in ents.most_common(30):
    print(f'  {e}: {c}')

print()
types = Counter(i['type'] for i in data['items'])
print('Types:')
for t, c in types.most_common():
    print(f'  {t}: {c}')

print()
companies = [i for i in data['items'] if i['category'] == '公司']
print(f'Company items: {len(companies)}')
for c in companies[:30]:
    print(f'  [{c["entity"]}] {c["title"][:100]}')

print()
institutions = [i for i in data['items'] if i['category'] == '机构']
print(f'Institution items: {len(institutions)}')
for inst in institutions[:10]:
    print(f'  [{inst["entity"]}] {inst["title"][:100]}')
