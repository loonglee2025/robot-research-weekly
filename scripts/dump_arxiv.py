import json, sys
d = json.load(open(sys.argv[1]))
for it in d['items']:
    if it.get('entity')=='arXiv cs.RO' or it.get('category')=='机构' and it.get('type')=='论文':
        print(f"{it.get('published_date','')} | {it.get('title')} | {it.get('url')}")
