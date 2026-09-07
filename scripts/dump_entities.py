import json, sys
p = sys.argv[1]
d = json.load(open(p))
items = d['items']

tracked = {
 'companies_western': ['Boston Dynamics','NVIDIA','Google DeepMind','Figure AI','Agility Robotics','Intuitive Surgical','ABB Robotics','FANUC','Universal Robots','Tesla Optimus','Amazon Robotics'],
 'companies_china': ['AGIBOT','智元机器人','Unitree','宇树科技','UBTECH','优必选','拓斯达','Fourier Intelligence','傅利叶智能','Leju Robotics','乐聚机器人','众擎机器人'],
 'institutions': ['CMU','Carnegie Mellon','MIT','Stanford','ETH Zurich','Georgia Tech','University of Tokyo','University of Oxford','Oxford','KAIST','TUM','UC Berkeley','Imperial College London'],
 'media': ['IEEE Spectrum','The Robot Report','Robohub','New Atlas','Robotics Business Review','Phys.org','Daily Robotics'],
}

for group, names in tracked.items():
    print('='*30, group, '='*30)
    seen=set()
    for it in items:
        ent = it.get('entity','')
        for n in names:
            if n.lower() in ent.lower():
                key = it.get('url')
                if key in seen: break
                seen.add(key)
                print(f"[{it.get('type')}] ({it.get('published_date','')}) {it.get('entity')}")
                print(f"   TITLE: {it.get('title')}")
                print(f"   URL: {it.get('url')}")
                s=(it.get('summary') or '').strip()
                if s:
                    print(f"   SUMMARY: {s[:400]}")
                break
