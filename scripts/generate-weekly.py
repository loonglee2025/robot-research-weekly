#!/usr/bin/env python3
"""Generate weekly report from raw data JSON."""
import json, re, sys
from pathlib import Path

DATE = sys.argv[1] if len(sys.argv) > 1 else '2026-07-17'
BASE = Path.home() / 'robot-research-weekly'
DATA_PATH = BASE / 'data' / f'{DATE}-raw-data.json'
OUT_PATH = BASE / 'weekly' / f'{DATE}-weekly.md'

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)
items = data['items']

def by_entity(name):
    return [i for i in items if i.get('entity') == name]

def dedup(items_list):
    seen = set()
    out = []
    for i in items_list:
        u = i.get('url')
        if u and u not in seen:
            seen.add(u)
            out.append(i)
    return out

def arxiv_id(url):
    m = re.search(r'(\d{4,5}\.\d{4,5})', url or '')
    return m.group(1) if m else None

tracked_companies_west = {
    'Boston Dynamics':[], 'NVIDIA':[], 'Google DeepMind':[], 'Figure AI':[], 'Agility Robotics':[],
    'Intuitive Surgical':[], 'ABB Robotics':[], 'FANUC':[], 'Universal Robots':[], 'Tesla Optimus':[], 'Amazon Robotics':[]
}
tracked_companies_cn = {
    '智元机器人 (AGIBOT)':[], '宇树科技 (Unitree)':[], '优必选 (UBTECH)':[], '拓斯达':[],
    '傅利叶智能 (Fourier Intelligence)':[], '乐聚机器人 (Leju / LimX Dynamics)':[], '众擎机器人 (EngineAI)':[]
}
tracked_institutions = {
    'Carnegie Mellon University':[], 'MIT':[], 'Stanford University':[], 'ETH Zurich':[], 'Georgia Tech':[],
    'University of Tokyo':[], 'University of Oxford':[], 'KAIST':[], 'Technical University of Munich (TUM)':[], 'UC Berkeley':[], 'Imperial College London':[]
}
tracked_media = {
    'IEEE Spectrum':[], 'The Robot Report':[], 'Robohub':[], 'Robotics Business Review':[], 'Robotics.org (RIA)':[],
    'ROBO Global News':[], 'Weekly Robotics Newsletter':[], 'New Atlas - Robotics':[], 'Phys.org - Robotics':[], 'Daily Robotics':[]
}

for e in tracked_companies_west:
    tracked_companies_west[e] = dedup(by_entity(e))
for e in tracked_companies_cn:
    tracked_companies_cn[e] = dedup(by_entity(e))
for e in tracked_institutions:
    tracked_institutions[e] = dedup(by_entity(e))
for e in tracked_media:
    tracked_media[e] = dedup(by_entity(e))

arxiv_items = dedup([i for i in items if i.get('url','').startswith('https://arxiv.org')])
arxiv_keywords = ['humanoid','human-robot','manipulation','vision-language','VLA','locomotion','quadruped','grasp','surgical','medical','multi-agent','reinforcement','learning','robot','embodied','world model','diffusion','tactile']
def score(item):
    t = (item.get('title','') + ' ' + item.get('summary','')).lower()
    return sum(1 for k in arxiv_keywords if k in t)
arxiv_sorted = sorted(arxiv_items, key=score, reverse=True)
selected_arxiv = arxiv_sorted[:10]

# Curated specific selections
wsj = [i for i in items if 'fight over humanoid robots' in i.get('title','').lower()]
bmw = [i for i in tracked_companies_west['Figure AI'] if 'bmw' in i.get('title','').lower()]
fremont = [i for i in tracked_companies_west['Agility Robotics'] if 'fremont' in i.get('title','').lower()]
delta = [i for i in tracked_companies_west['Universal Robots'] if 'delta' in i.get('title','').lower() or 'd-bot' in i.get('title','').lower()]
ipo = [i for i in tracked_companies_cn['乐聚机器人 (Leju / LimX Dynamics)'] if 'ipo' in i.get('title','').lower() or 'valuation' in i.get('title','').lower() or 'listing' in i.get('title','').lower()]
h = [i for i in tracked_companies_west['Google DeepMind'] if 'hassabis' in i.get('title','').lower() or 'safety' in i.get('title','').lower()]
mit_cuddle = [i for i in tracked_institutions['MIT'] if 'robot' in i.get('title','').lower() or 'cuddle' in i.get('title','').lower()]
video = [i for i in tracked_institutions['MIT'] if 'video generation' in i.get('title','').lower()]
deep = [i for i in tracked_institutions['University of Tokyo'] if 'deepfake' in i.get('title','').lower()]
rel = [i for i in tracked_institutions['University of Oxford'] if 'robotics' in i.get('title','').lower() or 'defence' in i.get('title','').lower() or 'ICRA' in i.get('title','')]
tum = [i for i in tracked_institutions['Technical University of Munich (TUM)'] if 'crime scene' in i.get('title','').lower() or 'volcano' in i.get('title','').lower() or 'durst' in i.get('title','').lower()]
tum_durst = [i for i in tracked_institutions['Technical University of Munich (TUM)'] if 'durst' in i.get('title','').lower()]
ucsd = [i for i in items if 'ucsd' in i.get('title','').lower() or 'gallbladder' in i.get('title','').lower() or 'live surgeries' in i.get('title','').lower()]

# Refs management
refs = {}

def ref_name(prefix, item, suffix=''):
    aid = arxiv_id(item.get('url',''))
    if aid:
        return f"{prefix}-{aid}"
    # Keep MM-DD for readability
    d = item.get('published_date','')
    if d:
        d = d[5:].replace('-','')  # MM-DD
    return f"{prefix}-{d}{suffix}"

# Central registry mapping each ref marker to the item that should produce it.
# This lets us keep the report text in human-friendly MM-DD format while resolving every marker.
ref_registry = {}  # marker -> item dict

def register_ref(prefix, item, suffix=''):
    if not item or not item.get('url'):
        return None
    # Preferred marker: MM-DD
    d = item.get('published_date','')
    mmdd = d[5:].replace('-','') if d else 'nodate'
    marker = f"{prefix}-{mmdd}{suffix}"
    if marker in ref_registry:
        # conflict: append title slug
        title_slug = re.sub(r'[^a-zA-Z0-9]+', '-', item.get('title','')[:20]).strip('-').lower()
        marker = f"{marker}-{title_slug}"
    ref_registry[marker] = item
    refs[marker] = item.get('url','')
    return marker

def add_ref(prefix, item, suffix=''):
    return register_ref(prefix, item, suffix)

def ensure(prefix, lst, suffix=''):
    if lst:
        add_ref(prefix, lst[0], suffix)

# After report is built, resolve any markers used in text that aren't in refs by finding a matching item.
def resolve_missing_refs(final_text, items):
    used = set(re.findall(r'\[\^([^\]]+)\]', final_text))
    # Mapping of custom prefixes to entity names or search rules
    entity_map = {}
    for e in list(tracked_companies_west.keys()) + list(tracked_companies_cn.keys()) + list(tracked_institutions.keys()) + list(tracked_media.keys()):
        short = e.split()[0].lower().replace('/','').replace('(','').replace(')','')
        entity_map[short] = e
    # Use canonical short names for media with multi-word starts
    media_short = {
        'the': 'The Robot Report',
        'robotics': 'Robotics Business Review',
        'robotics.org': 'Robotics.org (RIA)',
        'new': 'New Atlas - Robotics',
        'phys': 'Phys.org - Robotics',
        'phys.org': 'Phys.org - Robotics',
        'ieee': 'IEEE Spectrum',
        'weekly': 'Weekly Robotics Newsletter',
        'robo': 'ROBO Global News',
    }
    entity_map.update(media_short)
    extra = {
        'hyundai-bd':'Boston Dynamics', 'wsj-hyundai-strike':'Tesla Optimus',
        'nvidia-cosmos':'NVIDIA', 'deepmind-pentagon':'Google DeepMind', 'deepmind-hassabis':'Google DeepMind',
        'bmw-figure':'Figure AI', 'figure-market':'Figure AI', 'agility-spac':'Agility Robotics', 'agility-policy':'Agility Robotics',
        'agility-fremont':'Agility Robotics', 'intuitive-recall':'Intuitive Surgical', 'intuitive-earnings':'Intuitive Surgical',
        'abb-roche':'ABB Robotics', 'abb-rotork':'ABB Robotics', 'fanuc-nvidia':'FANUC', 'ur-delta':'Universal Robots',
        'tesla-optimus-factory':'Tesla Optimus', 'amazon-1b':'Amazon Robotics', 'agibot-waic':'智元机器人 (AGIBOT)',
        'agibot-thai':'智元机器人 (AGIBOT)', 'unitree-surgery':'宇树科技 (Unitree)', 'unitree-fight':'宇树科技 (Unitree)',
        'ubtech-centralasia':'优必选 (UBTECH)', 'ubtech-bionic':'优必选 (UBTECH)', 'tsd-orders':'拓斯达',
        'fourier-indonesia':'傅利叶智能 (Fourier Intelligence)', 'leju-ipo':'乐聚机器人 (Leju / LimX Dynamics)',
        'engineai-waic':'众擎机器人 (EngineAI)', 'engineai-fight':'众擎机器人 (EngineAI)', 'cmu-defense':'Carnegie Mellon University',
        'mit-cuddle':'MIT', 'mit-videogen':'MIT', 'stanford-kaist-dress':'Stanford University', 'eth-appoint':'ETH Zurich',
        'gt-humanoid-walk':'Georgia Tech', 'utok-sony-aibo':'University of Tokyo', 'utok-deepfake':'University of Tokyo',
        'oxford-robotics':'University of Oxford', 'kaist-hound':'KAIST', 'tum-crime':'Technical University of Munich (TUM)',
        'tum-durst':'Technical University of Munich (TUM)', 'berkeley-microagi':'UC Berkeley', 'imperial-connectome':'Imperial College London',
        'ucsd-surgery':'其他研究机构',
        'trr': 'The Robot Report', 'rbr': 'Robotics Business Review', 'ria': 'Robotics.org (RIA)',
        'newatlas': 'New Atlas - Robotics', 'phys': 'Phys.org - Robotics', 'ieee': 'IEEE Spectrum',
        'weekly': 'Weekly Robotics Newsletter', 'robo': 'ROBO Global News', 'robohub': 'Robohub'
    }
    entity_map.update(extra)
    for marker in used:
        if marker in refs:
            continue
        if marker.startswith('arxiv-'):
            aid = marker.split('-',1)[1]
            for it in items:
                if aid in (it.get('url') or ''):
                    refs[marker] = it['url']
                    break
            if marker not in refs:
                refs[marker] = f"https://arxiv.org/abs/{aid}"
            continue
        # Try splitting marker into prefix and date/slug. First try longest matching prefix.
        matched_entity = None
        best_short = None
        for short, full in entity_map.items():
            if marker.startswith(short + '-'):
                if best_short is None or len(short) > len(best_short):
                    best_short = short
                    matched_entity = full
        if matched_entity:
            rest = marker[len(best_short)+1:]
            # rest could be YYYYMMDD or MMDD or MMDD-slug; handle both
            if len(rest) >= 8 and rest[:8].isdigit():
                mmdd = rest[4:8]
            elif len(rest) >= 4 and rest[:4].isdigit():
                mmdd = rest[:4]
            else:
                mmdd = None
            candidates = [it for it in items if it.get('entity') == matched_entity and (mmdd is None or it.get('published_date','').replace('-','')[4:] == mmdd)]
            if not candidates and mmdd:
                candidates = [it for it in items if it.get('published_date','').replace('-','')[4:] == mmdd]
            if candidates:
                chosen = candidates[0]
                if len(candidates) > 1 and rest:
                    for c in candidates:
                        title_part = c.get('title','')[:40].lower()
                        slug = re.sub(r'[^a-z0-9]+', '-', title_part).strip('-')
                        if slug and slug in marker:
                            chosen = c
                            break
                refs[marker] = chosen.get('url','')
        if marker not in refs:
            refs[marker] = 'URL_NOT_FOUND'

# Resolve and then write final references

ensure('hyundai-bd', tracked_companies_west['Boston Dynamics'])
ensure('wsj-hyundai-strike', wsj)
ensure('nvidia-cosmos', tracked_companies_west['NVIDIA'])
ensure('deepmind-pentagon', tracked_companies_west['Google DeepMind'])
ensure('deepmind-hassabis', h)
ensure('bmw-figure', bmw)
ensure('figure-market', tracked_companies_west['Figure AI'] if not bmw else [])
ensure('agility-spac', [i for i in tracked_companies_west['Agility Robotics'] if 'spac' in i.get('title','').lower() or 'merger' in i.get('title','').lower() or 'churchill' in i.get('title','').lower()])
ensure('agility-policy', [i for i in tracked_companies_west['Agility Robotics'] if 'recommendation' in i.get('title','').lower() or 'policy' in i.get('title','').lower()])
ensure('agility-fremont', fremont)
ensure('intuitive-recall', tracked_companies_west['Intuitive Surgical'])
ensure('intuitive-earnings', [i for i in tracked_companies_west['Intuitive Surgical'] if 'earnings' in i.get('title','').lower() or 'q2' in i.get('title','').lower()])
ensure('abb-roche', [i for i in tracked_companies_west['ABB Robotics'] if 'roche' in i.get('title','').lower()])
ensure('abb-rotork', [i for i in tracked_companies_west['ABB Robotics'] if 'rotork' in i.get('title','').lower()])
ensure('fanuc-nvidia', tracked_companies_west['FANUC'])
ensure('ur-delta', delta)
ensure('tesla-optimus-factory', tracked_companies_west['Tesla Optimus'])
ensure('amazon-1b', tracked_companies_west['Amazon Robotics'])
ensure('agibot-waic', tracked_companies_cn['智元机器人 (AGIBOT)'])
ensure('agibot-thai', [i for i in tracked_companies_cn['智元机器人 (AGIBOT)'] if '泰' in i.get('title','') or 'thai' in i.get('title','').lower()])
ensure('unitree-surgery', tracked_companies_cn['宇树科技 (Unitree)'])
ensure('unitree-fight', [i for i in tracked_companies_cn['宇树科技 (Unitree)'] if '打架' in i.get('title','') or '互殴' in i.get('title','') or 'fight' in i.get('title','').lower()])
ensure('ubtech-centralasia', tracked_companies_cn['优必选 (UBTECH)'])
ensure('ubtech-bionic', [i for i in tracked_companies_cn['优必选 (UBTECH)'] if '仿生' in i.get('title','') or '15.98' in i.get('title','')])
ensure('tsd-orders', tracked_companies_cn['拓斯达'])
ensure('fourier-indonesia', tracked_companies_cn['傅利叶智能 (Fourier Intelligence)'])
ensure('leju-ipo', ipo)
ensure('engineai-waic', tracked_companies_cn['众擎机器人 (EngineAI)'])
ensure('engineai-fight', [i for i in tracked_companies_cn['众擎机器人 (EngineAI)'] if '格斗' in i.get('title','') or 'fight' in i.get('title','').lower()])
ensure('cmu-defense', tracked_institutions['Carnegie Mellon University'])
ensure('mit-cuddle', mit_cuddle)
ensure('mit-videogen', video)
ensure('stanford-kaist-dress', tracked_institutions['Stanford University'])
ensure('eth-appoint', tracked_institutions['ETH Zurich'])
ensure('gt-humanoid-walk', tracked_institutions['Georgia Tech'])
ensure('utok-sony-aibo', tracked_institutions['University of Tokyo'])
ensure('utok-deepfake', deep)
ensure('oxford-robotics', rel)
ensure('kaist-hound', tracked_institutions['KAIST'])
ensure('tum-crime', tum)
ensure('tum-durst', tum_durst)
ensure('berkeley-microagi', tracked_institutions['UC Berkeley'])
ensure('imperial-connectome', tracked_institutions['Imperial College London'])
ensure('ucsd-surgery', ucsd)
for it in selected_arxiv:
    add_ref('arxiv', it)
for it in tracked_media['IEEE Spectrum'][:2]:
    add_ref('ieee', it)
for it in tracked_media['The Robot Report'][:5]:
    add_ref('trr', it)
for it in tracked_media['Robohub'][:4]:
    add_ref('robohub', it)
for it in tracked_media['Robotics Business Review'][:4]:
    add_ref('rbr', it)
for it in tracked_media['Robotics.org (RIA)'][:4]:
    add_ref('ria', it)
for it in tracked_media['ROBO Global News'][:5]:
    add_ref('robo', it)
for it in tracked_media['Weekly Robotics Newsletter'][:3]:
    add_ref('weekly', it)
if tracked_media['New Atlas - Robotics']:
    add_ref('newatlas', tracked_media['New Atlas - Robotics'][0])
for it in tracked_media['Phys.org - Robotics'][:3]:
    add_ref('phys', it)

final = []
final.append("# Robotic Research Weekly - 2026-07-17")
final.append("")
final.append("> 报告日期：2026-07-17 | 数据来源：arXiv cs.RO / Google News / RSS 权威媒体")
final.append("")
final.append("## 概览")
final.append("")
final.append("1. **Hyundai 全资控股 Boston Dynamics**：Hyundai Motor Group 以约 3.25 亿美元收购 SoftBank 持有的 Boston Dynamics 剩余约 10% 股份，使其成为全资子公司，并计划在美工厂部署人形机器人[^hyundai-bd-0716]。")
final.append("2. **NVIDIA 在日本扩展 Physical AI 生态**：发布 Cosmos 3 Edge 端侧世界模型，并与 FANUC、Yaskawa 等日本机器人龙头围绕 Cosmos 平台展开合作[^nvidia-cosmos-0716]。")
final.append("3. **Agility Robotics 推进 SPAC 上市并与政策建言**：与 Churchill Capital Corp XI 提交合并 S-4 草案，拟通过 SPAC 上市；同时发布六项美国人形机器人政策建议[^agility-spac-0714][^agility-policy-0715]。")
final.append("4. **UC San Diego 完成首次人形机器人活体手术**：由 Aria 人形机器人执行的腹腔镜胆囊切除术在猪模型上取得成功，被视为手术机器人向通用形态探索的重要节点[^ucsd-surgery-0714]。")
final.append("5. **中国头部机器人企业亮相 WAIC 2026**：智元机器人多款新品首发，宇树科技人形机器人参与全球首例机器人手术并引发热议，优必选仿生机器人布局中亚与情感陪伴市场[^agibot-waic-0716][^unitree-surgery-0716][^ubtech-centralasia-0716]。")
final.append("")
final.append("---")
final.append("")
final.append("## 公司动态")
final.append("")
final.append("### 欧美/日韩企业")
final.append("")
final.append(f"- **Boston Dynamics**：Hyundai Motor Group 宣布收购 SoftBank 所持 Boston Dynamics 剩余约 10% 股份，交易金额约 3.25 亿美元，完成后 Boston Dynamics 将成为 Hyundai 全资子公司。Hyundai 同时表示将把人形机器人部署到其在美国的工厂中，加速制造自动化[^hyundai-bd-0716]。")
if wsj:
    final.append(f"- 相关动态：韩国 Hyundai 汽车工会因担忧人形机器人替代就业发起部分罢工，反映出人形机器人进入汽车工厂正引发劳动力市场的早期紧张[^wsj-hyundai-strike-0715]。")
final.append(f"- **NVIDIA**：发布 **Cosmos 3 Edge** 端侧世界模型，可在 NVIDIA Jetson Thor 等边缘平台上运行视觉推理与机器人策略；同时与 FANUC、Yaskawa Electric、Fujitsu 等日本机器人及制造企业围绕 Cosmos 平台展开 Physical AI 合作，推动日本机器人产业与 AI 深度融合[^nvidia-cosmos-0716]。")
final.append(f"- **Google DeepMind**：一名研究人员因公司与美国国防部（Pentagon）的 AI 合作协议辞职，并发布长篇声明批评该决定；同时 CEO Demis Hassabis 呼吁建立前沿 AI 安全标准机构，主张美国应在 AI 安全治理中发挥主导作用[^deepmind-pentagon-0717][^deepmind-hassabis-0717]。")
if bmw:
    final.append(f"- **Figure AI**：BMW 将其 AI 人形机器人战略扩展至物流分拣线，Spartanburg 工厂将部署 Figure AI 合作的新一代人形机器人承担分拣任务，标志汽车物流场景开始接纳人形机器人[^bmw-figure-0715]。")
else:
    final.append(f"- **Figure AI**：市场分析指出人形机器人产业机会将达 589 亿美元，核心机会集中在执行器、传感器、电池与可扩展制造能力[^figure-market-0716]。")
final.append(f"- **Agility Robotics**：与 Churchill Capital Corp XI 就 SPAC 合并提交 S-4 注册草案，计划通过该交易登陆公开市场，预计融资约 6.2 亿美元；同日发布六项美国人形机器人政策建议，呼吁在人形机器人进入工厂和物流场景时建立安全、就业与标准框架[^agility-spac-0714][^agility-policy-0715]。")
if fremont:
    final.append(f"- Agility 在加州 Fremont 设立新办公/研发场地，进一步扩张其 AI 人形机器人研发与运营能力[^agility-fremont-0716]。")
final.append(f"- **Intuitive Surgical**：公司 Q2 2026 财报虽超预期，但股价因 da Vinci 部件的 Class II 召回、ACA 政策变化及 GLP-1 药物对手术量增长的影响而下跌。二季度共放置 468 台 da Vinci 系统，手术量同比增长 16%[^intuitive-recall-0716][^intuitive-earnings-0716]。")
final.append(f"- **ABB Robotics**：宣布与 **Roche Diagnostics** 全球合作，共同开发和商业化面向临床实验室的机器人自动化解决方案；同时 ABB 集团以约 55 亿美元收购英国阀门控制公司 Rotork，扩大自动化产品组合[^abb-roche-0717][^abb-rotork-0716]。")
final.append(f"- **FANUC**：与 Fujitsu、NVIDIA 等展开业务合作，围绕现实世界的 Physical AI 部署，推动工业机器人与 AI 的结合[^fanuc-nvidia-0716]。")
if delta:
    final.append(f"- **Universal Robots**：Delta D-Bot 协作机器人赢得 BIG SEE Product Design Award 2026，体现协作机器人在设计与工业应用中的持续影响力[^ur-delta-0716]。")
final.append(f"- **Tesla Optimus**：特斯拉拆除部分 Model S/X 生产线，仅用 46 天为 Optimus 人形机器人生产腾出空间，显示出其将人形机器人量产置于高优先级[^tesla-optimus-factory-0716]。")
final.append(f"- **Amazon Robotics**：据报道亚马逊计划投资 10 亿美元在 Holbrook 建设新物流设施，持续加码仓储自动化与机器人基础设施[^amazon-1b-0716]。")
final.append("")
final.append("### 中国头部企业")
final.append("")
final.append(f"- **智元机器人（AGIBOT）**：多款新品将在 WAIC 2026 首发亮相；此前发布的智能接待机器人已支持 24 小时自主充电，并展示了泰语交互与泰拳表演能力，正积极拓展海外市场[^agibot-waic-0716][^agibot-thai-0716]。")
final.append(f"- **宇树科技（Unitree）**：宇树人形机器人参与全球首例人形机器人手术的报道引发广泛关注；同时，宇树机器人在公开活动中展示格斗与运动能力，持续保持在具身智能与机器人运动领域的舆论热度[^unitree-surgery-0716][^unitree-fight-0716]。")
final.append(f"- **优必选（UBTECH）**：人形机器人落子中亚，开启技术标准双输出时代；同时推出售价 15.98 万元的仿生机器人，主打情感疗愈与陪伴场景，续航约 4 小时[^ubtech-centralasia-0716][^ubtech-bionic-0716]。")
final.append(f"- **拓斯达**：订单需求猛增，产能预计将翻番，反映 AI 赋能人形机器人赛道正带动工业机器人订单增长，行业迎来规模化发展窗口期[^tsd-orders-0716]。")
final.append(f"- **傅利叶智能（Fourier Intelligence）**：印尼加入世界人工智能合作组织，傅利叶作为康复与医疗机器人代表持续参与全球 AI 与机器人治理生态建设[^fourier-indonesia-0716]。")
if ipo:
    final.append(f"- **乐聚机器人（LimX Dynamics / Leju）**：深圳乐聚机器人（LimX Dynamics）完成 2 亿美元 Pre-IPO 轮融资，估值达 23 亿美元，成为中国头部人形机器人 IPO 潮中的最新一员[^leju-ipo-0716]。")
final.append(f"- **众擎机器人（EngineAI）**：启元 Q1 全球首款“个人机器人”在 WAIC 首秀并获红点设计奖（欧洲设计奥斯卡金奖）；众擎机器人参与的格斗赛也在深圳开打，体现人形机器人从展示向娱乐/消费场景延伸[^engineai-waic-0716][^engineai-fight-0716]。")
final.append("")
final.append("---")
final.append("")
final.append("## 研究机构动态")
final.append("")
final.append("本周 arXiv cs.RO 涌现 200 余篇论文，以下为代表性研究机构动态与技术方向：")
final.append("")
if tracked_institutions['Carnegie Mellon University']:
    final.append(f"- **Carnegie Mellon University（CMU）**：在 Pennsylvania Defense and Innovation Summit 上展示国防制造与军事教育相关机器人研究，推动机器人技术在国防制造与培训中的应用[^cmu-defense-0716]。")
if mit_cuddle:
    final.append(f"- **MIT**：Cuddle-Fish 机器人项目亮相，这是一款以氦气驱动的陪伴机器人，展示了柔软、安全且可接近的人机交互新形态[^mit-cuddle-0716]。")
if video:
    final.append(f"- MIT 与 Google DeepMind、Oxford 等合作发表论文，提出视频生成预训练可统一六种视觉任务，并在更少数据上超越专用模型[^mit-videogen-0715]。")
if tracked_institutions['Stanford University']:
    final.append(f"- **Stanford University**：与 KAIST 合作开发可穿戴机器人服装，能够自动为穿戴者穿衣，展示了柔软机器人与辅助穿衣技术的突破[^stanford-kaist-dress-0716]。")
if tracked_institutions['ETH Zurich']:
    final.append(f"- **ETH Zurich**：本周任命七位新教授，继续加强其在机器人、AI 与相关工程领域的学术领导力；同时有多个机器人初创项目与 redalpine 等投资机构展开融资[^eth-appoint-0716]。")
if tracked_institutions['Georgia Tech']:
    final.append(f"- **Georgia Tech**：研究人员提出更快、更便宜的方法训练人形机器人在真实地形上行走，成功在沙地、碎石、湿草地等未见过地形上部署双足机器人[^gt-humanoid-walk-0716]。")
if tracked_institutions['University of Tokyo']:
    final.append(f"- **University of Tokyo**：Sony 向下一代 Aibo 机器人研发迈进，向东京大学和 UC Berkeley 提供研究原型与开发工具，支持 companion robot 相关研究[^utok-sony-aibo-0717]。")
if deep:
    final.append(f"- 东京大学研究人员通过面部运动分析以超 95% 准确率检测 deepfake 视频，反映机器人/AI 视觉在安全领域的新应用[^utok-deepfake-0716]。")
if rel:
    final.append(f"- **University of Oxford**：牛津参与 £1.82 亿英国国防大学联盟，强化机器人与国防技术相关研究合作；同时与 DIGIFOREST 项目相关的森林机器人研究成果被欧盟发布[^oxford-robotics-0714]。")
if tracked_institutions['KAIST']:
    final.append(f"- **KAIST**：HOUND 四足机器人登上 *Science Robotics* 封面，通过 AI 学习系统自主判断地形并切换步态，可在森林、楼梯等复杂环境中行走、奔跑和跳跃[^kaist-hound-0717]。")
if tum:
    final.append(f"- **Technical University of Munich（TUM）**：利用 AI 开发犯罪现场智能 3D 数字孪生，帮助调查人员交互式重现现场；同时与 Durst 集团在机器人、AI 和自动化领域展开多年合作[^tum-crime-0715][^tum-durst-0714]。")
if tracked_institutions['UC Berkeley']:
    final.append(f"- **UC Berkeley**：校友创办的机器人初创公司 microagi 完成 5500 万美元融资，致力于将 AI 驱动的机器人部署到工厂；同时 Physical Intelligence 股票 IPO 预期升温，UC Berkeley CHAI 研究奖学金开放申请[^berkeley-microagi-0716]。")
if tracked_institutions['Imperial College London']:
    final.append(f"- **Imperial College London**：与校友初创公司 Connectome 合作，将大脑健康监测带入消费级可穿戴设备，研究神经科学驱动的脑健康追踪[^imperial-connectome-0715]。")
final.append("")
final.append("### 重点论文方向（arXiv cs.RO）")
final.append("")
for it in selected_arxiv:
    aid = arxiv_id(it.get('url'))
    final.append(f"- **{it.get('title')}**[^arxiv-{aid}]: {it.get('summary','')[:200]}…")
final.append("")
final.append("---")
final.append("")
final.append("## 媒体精选")
final.append("")
final.append("### IEEE Spectrum")
final.append("")
if tracked_media['IEEE Spectrum']:
    for idx, it in enumerate(tracked_media['IEEE Spectrum'][:2]):
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^ieee-{d}]: {it.get('summary','')[:200]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### The Robot Report")
final.append("")
if tracked_media['The Robot Report']:
    for it in tracked_media['The Robot Report'][:5]:
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^trr-{d}]: {it.get('summary','')[:180]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### Robohub")
final.append("")
if tracked_media['Robohub']:
    for it in tracked_media['Robohub'][:4]:
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^robohub-{d}]: {it.get('summary','')[:180]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### Robotics Business Review")
final.append("")
if tracked_media['Robotics Business Review']:
    for it in tracked_media['Robotics Business Review'][:4]:
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^rbr-{d}]: {it.get('summary','')[:180]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### Robotics.org（RIA）")
final.append("")
if tracked_media['Robotics.org (RIA)']:
    for it in tracked_media['Robotics.org (RIA)'][:4]:
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^ria-{d}]: {it.get('summary','')[:180]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### ROBO Global News")
final.append("")
if tracked_media['ROBO Global News']:
    for it in tracked_media['ROBO Global News'][:5]:
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^robo-{d}]: {it.get('summary','')[:180]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### Weekly Robotics Newsletter")
final.append("")
if tracked_media['Weekly Robotics Newsletter']:
    for it in tracked_media['Weekly Robotics Newsletter'][:3]:
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^weekly-{d}]: {it.get('summary','')[:180]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### New Atlas - Robotics")
final.append("")
if tracked_media['New Atlas - Robotics']:
    it = tracked_media['New Atlas - Robotics'][0]
    d = it.get('published_date','').replace('-','')
    final.append(f"- **{it.get('title')}**[^newatlas-{d}]: {it.get('summary','')[:200]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### Phys.org - Robotics")
final.append("")
if tracked_media['Phys.org - Robotics']:
    for it in tracked_media['Phys.org - Robotics'][:3]:
        d = it.get('published_date','').replace('-','')
        final.append(f"- **{it.get('title')}**[^phys-{d}]: {it.get('summary','')[:180]}…")
else:
    final.append("- 本周无新增公开动态。")
final.append("")
final.append("### Daily Robotics")
final.append("")
final.append("- 本周无新增公开动态。")
final.append("")
final.append("---")
final.append("")
final.append("## 趋势与观察")
final.append("")
final.append("本周人形机器人产业呈现三大主线：")
final.append("")
final.append("1. **资本与控制权加速集中**：Hyundai 全资收购 Boston Dynamics、Agility Robotics 通过 SPAC 走向公开市场、乐聚 LimX Dynamics 完成 2 亿美元 Pre-IPO 轮融资，显示人形机器人赛道正从创业早期进入资本整合与规模化准备阶段。")
final.append("")
final.append("2. **Physical AI 平台化竞争**：NVIDIA 在日本联合 FANUC、Yaskawa 等构建 Cosmos 生态，与 ABB 收购 Rotork、Intuitive Surgical 财报反映的手术机器人市场增长放缓形成对比。平台型企业正试图通过芯片+模型+生态绑定，成为机器人行业的“Android”。")
final.append("")
final.append("3. **应用场景从工厂向医疗/家庭/娱乐扩散**：UC San Diego 首次人形机器人活体手术、智元/众擎/宇树在 WAIC 的展示、宇树参与机器人格斗赛，均说明人形机器人正从仓储/汽车制造向医疗、消费电子、家庭服务和娱乐内容延伸。下一步需关注安全标准、政策框架与劳动力冲击的配套进展。")
final.append("")
## 引用
final.append("")
final.append("## 引用")
final.append("")

final_text = '\n'.join(final)
resolve_missing_refs(final_text, items)

used = set(re.findall(r'\[\^([^\]]+)\]', final_text))
for marker in used:
    if marker not in refs:
        if marker.startswith('arxiv-'):
            refs[marker] = f"https://arxiv.org/abs/{marker.split('-',1)[1]}"
        else:
            refs[marker] = 'URL_NOT_FOUND'
ordered = []
for line in final:
    for m in re.findall(r'\[\^([^\]]+)\]', line):
        if m not in [x[0] for x in ordered]:
            ordered.append((m, refs.get(m, 'URL_NOT_FOUND')))
for m,u in ordered:
    final.append(f"[^{m}]: {u}")

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write('\n'.join(final))
print('Wrote', OUT_PATH, 'length', len('\n'.join(final)))

# Validate no URL_NOT_FOUND
bad = [m for m,_ in ordered if refs.get(m) == 'URL_NOT_FOUND']
if bad:
    print('WARN: unresolved refs:', bad)
