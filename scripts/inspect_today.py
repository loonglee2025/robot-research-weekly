import json, sys
from collections import Counter
p = sys.argv[1] if len(sys.argv)>1 else 'data/2026-08-14-raw-data.json'
d = json.load(open(p))
print('fetch_date:', d.get('fetch_date'))
print('total_items:', d.get('total_items'), 'len:', len(d['items']))
print('--- entities ---')
for e,c in Counter(i['entity'] for i in d['items']).most_common():
    print(c, e)
print('--- categories ---')
for e,c in Counter(i['category'] for i in d['items']).most_common():
    print(c, e)
print('--- types ---')
for e,c in Counter(i['type'] for i in d['items']).most_common():
    print(c, e)
