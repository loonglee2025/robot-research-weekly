#!/usr/bin/env python3
"""Combine existing arXiv+RSS data with new Composio search results, deduplicate, and save."""
import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.expanduser("~/robot-research-weekly/data")
today = datetime.now(timezone.utc).date().isoformat()

# Load existing data
existing_path = os.path.join(DATA_DIR, f"{today}-raw-data.json")
with open(existing_path) as f:
    existing = json.load(f)

existing_items = existing.get("items", [])
existing_urls = {item["url"] for item in existing_items}

# New items from Composio searches
new_items = [
    # --- Boston Dynamics ---
    {"title": "Bridging the 'Porch Gap'", "url": "https://bostondynamics.com/blog/bridging-the-porch-gap/", "published_date": "2026-07-21T16:48:48+00:00", "entity": "Boston Dynamics", "category": "公司", "type": "产品发布", "summary": "Boston Dynamics is testing a last-mile delivery solution where Spot will help get packages from van to doorstep with less strain."},
    {"title": "Boston Dynamics plans $100M expansion expected to create 1,250 jobs", "url": "https://www.masslive.com/business/2026/07/boston-dynamics-plans-100m-expansion-expected-to-create-1250-jobs.html", "published_date": "2026-07-17T15:58:00+00:00", "entity": "Boston Dynamics", "category": "公司", "type": "其他", "summary": "Boston Dynamics plans approximately $100 million project that will transform operations and create 1,250 jobs."},
    {"title": "Hyundai Now Owns All of Boston Dynamics, and the Robots Still Can't Build a Car", "url": "https://finance.yahoo.com/technology/ai/articles/hyundai-now-owns-boston-dynamics-162055008.html", "published_date": "2026-07-17T16:20:55+00:00", "entity": "Boston Dynamics", "category": "公司", "type": "合作", "summary": "Hyundai Motor Group has acquired the remaining stake in Boston Dynamics from SoftBank, taking full ownership."},
    {"title": "Hyundai Motor Group to buy out Boston Dynamics", "url": "https://global.chinadaily.com.cn/a/202607/20/WS6a5d942ea310986e2b4662e4.html", "published_date": "2026-07-21T07:00:00+00:00", "entity": "Boston Dynamics", "category": "公司", "type": "合作", "summary": "Hyundai Motor Group to buy out Boston Dynamics, deal worth about 500 billion won ($335 million)."},
    {"title": "Building Robots for the Real World: Boston Dynamics on Atlas, Automation, and the Future of Human Work", "url": "https://innotechtoday.com/building-robots-for-the-real-world-boston-dynamics-on-atlas-automation-and-the-future-of-human-work/", "published_date": "2026-07-20T16:36:18+00:00", "entity": "Boston Dynamics", "category": "公司", "type": "观点", "summary": "Boston Dynamics discusses Atlas, automation, and the future of human work in an in-depth interview."},
    {"title": "Atlas' Journey to FIFA World Cup 2026™ | Boston Dynamics", "url": "https://www.hyundaimotorgroup.com/en/tv/atlas-journey-to-fifa-world-cup-2026-boston-dynamics", "published_date": "2026-07-22T06:13:51+00:00", "entity": "Boston Dynamics", "category": "公司", "type": "其他", "summary": "Explore Atlas' FIFA World Cup 2026 live performance story and discover how Boston Dynamics brought robotics to the pitch."},
    {"title": "Samsung's new robotics division appoints former Boston Dynamics lead", "url": "https://www.siliconrepublic.com/machines/samsungs-new-robotics-division-appoints-former-boston-dynamics-lead", "published_date": "2026-07-21T08:44:27+00:00", "entity": "Boston Dynamics", "category": "公司", "type": "其他", "summary": "Samsung Electronics is establishing a new robotics division overseen by a recently hired former Hyundai Motor Group robotics strategist."},
    
    # --- NVIDIA ---
    {"title": "NVIDIA Open Sources First GPU-Accelerated Medical Physics Simulation Framework", "url": "https://blogs.nvidia.com/blog/medical-physics-simulation-open-source/", "published_date": "2026-07-22T22:16:59+00:00", "entity": "NVIDIA", "category": "公司", "type": "产品发布", "summary": "NVIDIA open-sources a GPU-accelerated Medical Physics Simulation framework for surgical robot developers."},
    {"title": "Nvidia, Meet AMD, Your New Competition For Humanoid Robot Brains", "url": "https://www.forbes.com/sites/johnkoetsier/2026/07/23/nvidia-meet-amd-your-new-competition-for-humanoid-robot-brains/", "published_date": "2026-07-23T16:42:40+00:00", "entity": "NVIDIA", "category": "公司", "type": "观点", "summary": "Foundation's MK-2 Phantom humanoid robots will use AMD Ryzen chips, challenging Nvidia's dominance in AI chips for robotics."},
    {"title": "Nvidia Broadens Physical AI Push With Robotics, Edge AI Updates", "url": "https://aibusiness.com/robotics/nvidia-physical-ai-push-robotics-edge-ai-updates", "published_date": "2026-07-17T20:29:30+00:00", "entity": "NVIDIA", "category": "公司", "type": "产品发布", "summary": "Nvidia is expanding its physical AI and robotics portfolio with new edge AI hardware, robot foundation models, and developer software."},
    {"title": "Nvidia Teams Up With Google on Robot Venture", "url": "https://www.barrons.com/articles/nvidia-stock-price-google-robot-f13b135e", "published_date": "2026-07-22T13:57:00+00:00", "entity": "NVIDIA", "category": "公司", "type": "合作", "summary": "Nvidia and Google are partnering with a European data-robotics startup Microagi as Alphabet earnings loom."},
    {"title": "Jensen Huang Turns to Japan's Robots for Nvidia's Next Growth Engine", "url": "https://observer.com/2026/07/jensen-huang-nvidias-future-japan-physical-ai/", "published_date": "2026-07-23T12:34:56+00:00", "entity": "NVIDIA", "category": "公司", "type": "其他", "summary": "Nvidia CEO Jensen Huang is pitching Japan's robot makers, factories and government on physical A.I. as the company's next growth engine."},
    {"title": "Nvidia shrinks Blackwell for mass robotics", "url": "https://www.jonpeddie.com/news/nvidia-shrinks-blackwell-for-mass-robotics/", "published_date": "2026-07-20T16:14:48+00:00", "entity": "NVIDIA", "category": "公司", "type": "产品发布", "summary": "Nvidia introduced Jetson Thor T3000 and T2000 modules in Tokyo, bringing Blackwell architecture to mass robotics."},
    {"title": "Exclusive: Google, Nvidia deepen Europe robotics play with startup compute deal", "url": "https://www.semafor.com/article/07/21/2026/google-nvidia-deepen-europe-robotics-play-with-microagi-compute-deal", "published_date": "2026-07-22T08:00:00+00:00", "entity": "NVIDIA", "category": "公司", "type": "合作", "summary": "Google and Nvidia partner with German data-robotics startup Microagi to provide computing power for humanoid factory deployment."},
    {"title": "NVIDIA unveils open-source simulation framework for surgical robotics", "url": "https://www.massdevice.com/nvidia-unveils-simulation-framework-surgical-robotics/", "published_date": "2026-07-23T00:00:02+00:00", "entity": "NVIDIA", "category": "公司", "type": "产品发布", "summary": "Nvidia announced a new open-source, GPU-accelerated simulation capability to help surgical robot developers."},
    {"title": "NVIDIA Brings Robot AI On-Device as Japan's Top Manufacturers Join Cosmos Coalition", "url": "https://www.techtimes.com/articles/320801/20260717/nvidia-brings-robot-ai-device-japans-top-manufacturers-join-cosmos-coalition.htm", "published_date": "2026-07-17T11:59:12+00:00", "entity": "NVIDIA", "category": "公司", "type": "合作", "summary": "NVIDIA announced that more than 20 Japanese industrial firms including FANUC, Kawasaki Heavy Industries, and Yaskawa Electric joined the Cosmos Coalition."},
    
    # --- Tesla Optimus ---
    {"title": "Elon Musk Says This Will Be Tesla's 'Biggest Product Ever'—If It Can Solve the Supply Chain Issue", "url": "https://www.inc.com/georgia-fearn/elon-musk-says-this-will-be-teslas-biggest-product-ever-if-it-can-solve-the-supply-chain-issue/91378137", "published_date": "2026-07-23T00:58:24+00:00", "entity": "Tesla Optimus", "category": "公司", "type": "产品发布", "summary": "Elon Musk said Tesla's humanoid robot Optimus will be its 'biggest product ever,' but the company must build nearly the entire supply chain."},
    {"title": "Elon Musk spelled out how hard it will be to design Optimus, scale up manufacturing", "url": "https://www.businessinsider.com/elon-musk-optimus-tesla-humanoid-robot-design-scale-manufacturing-ai-2026-7", "published_date": "2026-07-23T16:22:00+00:00", "entity": "Tesla Optimus", "category": "公司", "type": "观点", "summary": "Elon Musk discussed the difficulty of designing Optimus and scaling up manufacturing during Tesla's earnings call."},
    {"title": "Tesla Says Optimus Is the First Robot That Learns by Watching", "url": "https://www.pymnts.com/earnings/2026/tesla-says-optimus-is-the-first-robot-that-learns-by-watching/", "published_date": "2026-07-23T17:30:15+00:00", "entity": "Tesla Optimus", "category": "公司", "type": "产品发布", "summary": "Tesla says Optimus, now in production at its Fremont factory, will be the first humanoid robot to learn to work without being programmed."},
    {"title": "Tesla Trains Optimus Robot With German Factory Data", "url": "https://fuelcellsworks.com/2026/07/22/electric/tesla-employees-in-germany-to-train-optimus-humanoid-robot-with-factory-movement-data", "published_date": "2026-07-23T12:49:00+00:00", "entity": "Tesla Optimus", "category": "公司", "type": "其他", "summary": "Tesla employees at Grünheide factory wear camera backpacks to collect movement data for training the Optimus humanoid robot."},
    {"title": "Tesla's push into AI and robotics is proving costly", "url": "https://www.axios.com/2026/07/22/tesla-earnings-ai-robotics-spending", "published_date": "2026-07-22T23:44:36+00:00", "entity": "Tesla Optimus", "category": "公司", "type": "其他", "summary": "Tesla revenue jumped on record vehicle deliveries in Q2, but operating profit dipped because of heavy spending on R&D including robotics."},
    {"title": "Tesla to Send First Optimus Builds to Academy, Says Production Begins This Year", "url": "https://eletric-vehicles.com/tesla/tesla-to-send-first-optimus-builds-to-academy-says-production-begins-this-year/", "published_date": "2026-07-22T21:28:19+00:00", "entity": "Tesla Optimus", "category": "公司", "type": "产品发布", "summary": "First Optimus robots off Tesla's Fremont line will go to an internal training programme rather than to factory work or customers."},
    {"title": "Humanoid Robots in 2026: What Is Actually Deployed", "url": "https://www.technology.org/2026/07/18/humanoid-robots-in-2026-what-is-actually-deployed/", "published_date": "2026-07-19T10:54:37+00:00", "entity": "Tesla Optimus", "category": "公司", "type": "观点", "summary": "Analysis of actual humanoid robot deployments in 2026; Tesla has never published an Optimus production count with cumulative builds in the low hundreds."},
    
    # --- Figure AI ---
    {"title": "BMW Group Plant Landshut develops software for humanoid robotics in component production", "url": "https://www.press.bmwgroup.com/global/article/detail/T0459467EN/bmw-group-plant-landshut-develops-software-for-humanoid-robotics-in-component-production?language=en", "published_date": "2026-07-21T07:00:00+00:00", "entity": "Figure AI", "category": "公司", "type": "合作", "summary": "BMW Group expands expertise in physical AI, with Plant Landshut taking on central software development tasks for humanoid robotics."},
    {"title": "U.K.-based Humanoid secures $152M in Series A funding", "url": "https://www.therobotreport.com/uk-based-humanoid-secures-152m-in-series-a-funding/", "published_date": "2026-07-21T23:46:54+00:00", "entity": "Figure AI", "category": "公司", "type": "融资", "summary": "Humanoid reached a $1.35 billion valuation as it scales its AI-driven industrial robots and expands commercial deployments."},
    
    # --- Agility Robotics ---
    {"title": "Agility Robotics plants its flag in Tesla's backyard", "url": "https://techcrunch.com/2026/07/17/agility-robotics-plants-its-flag-in-teslas-backyard/", "published_date": "2026-07-17T20:19:49+00:00", "entity": "Agility Robotics", "category": "公司", "type": "其他", "summary": "Agility Robotics is opening a 60,000-square-foot facility to train its humanoid robots in Fremont, California, near Tesla's factory."},
    {"title": "Oregon robotics company chooses California for its big expansion", "url": "https://www.oregonlive.com/silicon-forest/2026/07/oregon-robotics-company-chooses-california-for-its-big-expansion.html", "published_date": "2026-07-20T20:49:00+00:00", "entity": "Agility Robotics", "category": "公司", "type": "其他", "summary": "Agility Robotics plans a major expansion near Silicon Valley, opening a large software development office northeast of San Jose."},
    {"title": "Tech Moves: Agility Robotics gets CFO", "url": "https://www.geekwire.com/2026/tech-moves-agility-robotics-gets-cfo-microsoft-security-departure-zaps-legal-officer-new-kexp-cto/", "published_date": "2026-07-23T17:34:01+00:00", "entity": "Agility Robotics", "category": "公司", "type": "其他", "summary": "Agility Robotics names a CFO ahead of its plans to go public."},
    {"title": "Leading humanoid startup isn't interested in the 'bidding wars' for top AI and robotics talent", "url": "https://www.businessinsider.com/agility-robotics-humanoid-ai-talent-bidding-wars-salary-compensation-2026-7", "published_date": "2026-07-20T21:30:00+00:00", "entity": "Agility Robotics", "category": "公司", "type": "观点", "summary": "Agility Robotics has expanded with a new Silicon Valley hub, avoiding AI talent wars and focusing on culture over high salaries."},
    {"title": "Agility Robotics opens new Fremont facility to accelerate physical AI development", "url": "https://roboticsandautomationnews.com/2026/07/17/agility-robotics-opens-new-fremont-facility-to-accelerate-physical-ai-development/103426/", "published_date": "2026-07-17T18:56:09+00:00", "entity": "Agility Robotics", "category": "公司", "type": "其他", "summary": "Agility Robotics opened a new Fremont facility to accelerate physical AI development for its Digit humanoid robot."},
    
    # --- Intuitive Surgical ---
    {"title": "Intuitive Surgical falls as Obamacare concerns rekindle medtech demand debate", "url": "https://www.reuters.com/legal/litigation/intuitive-surgical-falls-obamacare-concerns-rekindle-medtech-demand-debate-2026-07-17/", "published_date": "2026-07-17T15:44:26+00:00", "entity": "Intuitive Surgical", "category": "公司", "type": "其他", "summary": "Intuitive Surgical shares slid about 13% after the surgical robot maker warned that changes to Obamacare subsidies could weigh on procedure growth."},
    {"title": "J&J Finally Has a Rival to da Vinci", "url": "https://finance.yahoo.com/healthcare/articles/j-j-finally-rival-da-191252711.html", "published_date": "2026-07-23T19:12:52+00:00", "entity": "Intuitive Surgical", "category": "公司", "type": "其他", "summary": "FDA granted De Novo authorization for Johnson & Johnson's Ottava Robotic Surgical System, creating a rival to Intuitive's da Vinci."},
    {"title": "Intuitive ties Q2 procedure softness to ACA subsidy expirations", "url": "https://www.medtechdive.com/news/intuitive-ties-q2-procedure-softness-to-aca-subsidy-expirations/825548/", "published_date": "2026-07-17T15:57:15+00:00", "entity": "Intuitive Surgical", "category": "公司", "type": "其他", "summary": "Despite an unexpected slowdown in U.S. procedure growth, system placements remained healthy, and Intuitive maintained its 2026 forecast."},
    {"title": "FDA clears Johnson & Johnson's surgical robot for 'the next era in surgery'", "url": "https://www.fiercebiotech.com/medtech/fda-clears-johnson-johnsons-surgical-robot-next-era-surgery", "published_date": "2026-07-23T12:27:04+00:00", "entity": "Intuitive Surgical", "category": "公司", "type": "产品发布", "summary": "The FDA has authorized Johnson & Johnson's Ottava Robotic Surgical System to compete with Intuitive Surgical and Medtronic."},
    
    # --- Amazon Robotics ---
    {"title": "Amazon Robotics planned for Austin Dog's Head development", "url": "https://cbsaustin.com/news/local/amazon-is-the-first-major-prospective-tenant-at-austins-dogs-head-development", "published_date": "2026-07-22T01:35:51+00:00", "entity": "Amazon Robotics", "category": "公司", "type": "其他", "summary": "Amazon Robotics was named the first major prospective tenant at Austin's Dog's Head development project."},
    {"title": "Amazon to lay off 494 workers at Florida warehouse as it adds advanced robotics", "url": "https://www.tcpalm.com/story/money/business/2026/07/20/why-amazon-laid-off-494-workers-at-florida-warehouse/90948858007/", "published_date": "2026-07-20T09:08:00+00:00", "entity": "Amazon Robotics", "category": "公司", "type": "其他", "summary": "Amazon will lay off 494 workers at its Port St. Lucie warehouse as it begins a major facility expansion that will add advanced robotics."},
    
    # --- FANUC (via NVIDIA Cosmos Coalition) ---
    {"title": "FANUC joins NVIDIA Cosmos Coalition with 20+ Japanese manufacturers", "url": "https://www.techtimes.com/articles/320801/20260717/nvidia-brings-robot-ai-device-japans-top-manufacturers-join-cosmos-coalition.htm", "published_date": "2026-07-17T11:59:12+00:00", "entity": "FANUC", "category": "公司", "type": "合作", "summary": "FANUC joined NVIDIA's Cosmos Coalition alongside Kawasaki Heavy Industries, Yaskawa Electric, and Fujitsu for physical AI development."},
    
    # --- Unitree (宇树科技) ---
    {"title": "宇树科技成功注册「UNITREE STORE」商标", "url": "https://www.google.com/goto?url=CAESXQHuR6pNLohVaQkinhQW9HDmlwPskrPJ9KxJuZkr0P-WUBVqu6ZtiywrRf-FzC6VfRYf5VI4bHj2wdT4vcDrs22B7O_2UqpU3Aa1dBo3TYiNZ6_wKefzs3_oG34vmw==", "published_date": "2026-07-20T06:09:29+00:00", "entity": "Unitree", "category": "公司", "type": "其他", "summary": "宇树科技注册「UNITREE STORE」商标，国际分类为9类科学仪器。"},
    {"title": "宇树科技王兴兴解读人形机器人，提出的'ChatGPT时刻'产业逻辑", "url": "https://www.google.com/goto?url=CAEScwHuR6pNCaahI4FZYTtIs59UJxkHiwxPb_A1RxJhHCBp6WBwiR1QmFYgTaXhif9gV5hIpvEOGTZoRatRhWfsOFGfuZRuyDUpWbmahOd2I1ot_X19Tog-6eWr_Mam9LMxFOmqWL_DougpWRi2rCFQQDEMNbg=", "published_date": "2026-07-23T04:16:00+00:00", "entity": "Unitree", "category": "公司", "type": "观点", "summary": "宇树科技创始人王兴兴在2026世界互联网大会数字丝路发展论坛解读人形机器人产业逻辑。"},
    {"title": "399万人民币！宇树3米载人变形机甲首亮相 「格斗机器人」秀拳脚", "url": "https://www.google.com/goto?url=CAESeAHuR6pNqbQcn4SqGHDIemb0jSw0d70TtIT1UJ80FEmxGWhejDhorlt1BhasqXCQeTG49z_GoLhN06949U8c9l-HOEnfxIQrxvrWV8itdRdgjHQYZjPtrh7XoTRDJcLeQBl33rHPMmeeofMnhmXe0gA3sf2m6I9Wog==", "published_date": "2026-07-22T02:58:00+00:00", "entity": "Unitree", "category": "公司", "type": "产品发布", "summary": "宇树科技在WAIC 2026上首次亮相3米载人变形机甲和格斗机器人，售价399万人民币。"},
    {"title": "The Robots Cometh — Unitree CEO Wang Xingxing's first international interview", "url": "https://time.com/article/2026/07/23/unitree-china-human-robotics/", "published_date": "2026-07-23T12:00:03+00:00", "entity": "Unitree", "category": "公司", "type": "观点", "summary": "Unitree CEO Wang Xingxing, in his first international interview with Time Magazine, explains the possibilities and promises of humanoid robots."},
    
    # --- AGIBOT (智元机器人) ---
    {"title": "AGIBOT在2026世界人工智能大会发布四款新机器人", "url": "https://www.zhiding.cn/physical-ai/2026/0721/3193951.shtml", "published_date": "2026-07-21T06:44:00+00:00", "entity": "AGIBOT", "category": "公司", "type": "产品发布", "summary": "智元机器人在WAIC 2026发布四款新品：A3 Ultra人形机器人、X2 EDU教育平台、G2 Max工业机器人及OmniHand 3 Ultra-M灵巧手。"},
    {"title": "全球首个！实现自主打乒乓球的全尺寸人形机器人智元远征A3亮相WAIC", "url": "https://www.jixin.tech/mobile/show.php?classid=1&id=7745&style=0&bclassid=1&cid=1&cpage=0", "published_date": "2026-07-19T23:42:46+00:00", "entity": "AGIBOT", "category": "公司", "type": "产品发布", "summary": "智元远征A3全尺寸人形机器人在WAIC 2026亮相，是全球首个全程自主决策完成乒乓球对抗的全尺寸双足人形机器人。"},
    {"title": "德银：中国人形机器人量产元年，关注零部件生态链", "url": "https://nai500.com/zh-hans/blog/2026/07/8-45/", "published_date": "2026-07-23T09:20:15+00:00", "entity": "AGIBOT", "category": "公司", "type": "观点", "summary": "德意志银行研报指出中国人形机器人产业正从概念走向规模化，2026年有望成为具身智能部署元年。"},
    
    # --- UBTECH (优必选) ---
    {"title": "优必选董事长'人类牛马'言论引争议，旗下人形机器人生意火爆", "url": "https://m.thepaper.cn/newsDetail_forward_33625898", "published_date": "2026-07-21T00:40:00+00:00", "entity": "UBTECH", "category": "公司", "type": "其他", "summary": "优必选创始人周剑因'人类牛马'相关言论引发争议，但旗下人形机器人生意火爆。"},
    {"title": "优必选CFO张钜：全世界没有比大湾区更适合的地方", "url": "https://finance.sina.com.cn/stock/relnews/hk/2026-07-22/doc-iniisxzu8630832.shtml", "published_date": "2026-07-22T13:39:00+00:00", "entity": "UBTECH", "category": "公司", "type": "其他", "summary": "优必选发布超仿生人形机器人U1，全渠道订单已突破1.3万台。"},
    {"title": "优必选在盐城成立智能机器人公司", "url": "https://www.caiwennews.com/article/1528352.shtml", "published_date": "2026-07-24T01:49:05+00:00", "entity": "UBTECH", "category": "公司", "type": "其他", "summary": "优必选在盐城成立智能机器人有限公司，经营范围包括AI理论与算法软件开发等。"},
    
    # --- Fourier Intelligence (傅利叶智能) ---
    {"title": "直击WAIC|傅利叶展出5台人形机器人，GR Nano桌面级新品力争年内上市", "url": "https://finance.sina.cn/2026-07-19/detail-iniiifmm0317116.d.html", "published_date": "2026-07-19T04:18:29+00:00", "entity": "Fourier Intelligence", "category": "公司", "type": "产品发布", "summary": "傅利叶在WAIC 2026展出5台人形机器人，GR Nano桌面级新品力争年内上市。"},
    {"title": "极佳视界与傅利叶达成战略合作'世界模型x人形本体'加速具身智能落地", "url": "https://www.ebrun.com/20260720/688555.shtml", "published_date": "2026-07-20T06:30:23+00:00", "entity": "Fourier Intelligence", "category": "公司", "type": "合作", "summary": "极佳视界与傅利叶达成战略合作，联手加速具身智能规模落地。"},
    {"title": "傅利叶×上海科技大学：共建联合实验室", "url": "https://www.163.com/dy/article/L2HA6B8O05568W0A.html", "published_date": "2026-07-23T05:05:10+00:00", "entity": "Fourier Intelligence", "category": "公司", "type": "合作", "summary": "傅利叶与上海科技大学在WAIC生命健康专区论坛上宣布共建联合实验室。"},
    
    # --- Google DeepMind ---
    {"title": "Exclusive: Google, Nvidia deepen Europe robotics play with startup compute deal", "url": "https://www.semafor.com/article/07/21/2026/google-nvidia-deepen-europe-robotics-play-with-microagi-compute-deal", "published_date": "2026-07-22T08:00:00+00:00", "entity": "Google DeepMind", "category": "公司", "type": "合作", "summary": "Google and Nvidia partner with German data-robotics startup Microagi to provide computing power for humanoid factory deployment."},
    {"title": "Google's Gemini delay exposes a deeper problem: employee frustration", "url": "https://www.axios.com/2026/07/23/googles-deep-mind-ai-model-race", "published_date": "2026-07-23T13:45:52+00:00", "entity": "Google DeepMind", "category": "公司", "type": "其他", "summary": "Poor morale among employees is contributing to delayed model releases from Google's DeepMind AI lab."},
    {"title": "I tried to stop Google DeepMind's Pentagon deal. Then I quit.", "url": "https://www.transformernews.ai/p/i-tried-to-stop-google-deepmind-pentagon-deal-then-quit", "published_date": "2026-07-21T14:02:23+00:00", "entity": "Google DeepMind", "category": "公司", "type": "其他", "summary": "Former Google DeepMind employee Alex Turner explains why he quit after the company reversed its AI weapons policy."},
    
    # --- CMU / MIT / Stanford ---
    {"title": "Stanford, MIT, Carnegie Mellon Lead First-Ever Benchmark of AI Production Capacity Across 50 Global Universities", "url": "https://www.prnewswire.com/news-releases/stanford-mit-carnegie-mellon-lead-first-ever-benchmark-of-ai-production-capacity-across-50-global-universities--new-5w-ai-communications-report-302832426.html", "published_date": "2026-07-22T17:31:00+00:00", "entity": "CMU", "category": "机构", "type": "其他", "summary": "5W AI Communications ranks Stanford, MIT, Carnegie Mellon, UC Berkeley, and Tsinghua in Tier I of AI production capacity across 50 global universities."},
    
    # --- US Humanoid Robot Policy ---
    {"title": "US eyes ban on Chinese humanoid robots as US-China tech rivalry intensifies", "url": "https://amp.scmp.com/tech/policy/article/3361622/us-eyes-ban-chinese-humanoid-robots-us-china-tech-rivalry-intensifies", "published_date": "2026-07-23T11:30:07+00:00", "entity": "其他", "category": "媒体", "type": "政策", "summary": "US House has passed a bill banning the military from using Chinese bots, as Washington ramps up restrictions on Chinese-made technology."},
    
    # --- Humanoid Robot Startup Funding ---
    {"title": "Top 10 humanoid robot startups to watch in 2026, ranked by total funding", "url": "https://techfundingnews.com/top-humanoid-robot-startups-2026-funding/", "published_date": "2026-07-24T10:05:20+00:00", "entity": "其他", "category": "媒体", "type": "其他", "summary": "Humanoid robot startups have raised $8.6B in 2026. From Figure AI and Apptronik to NEURA Robotics."},
    {"title": "人形机器人公司Humanoid融资1.52亿美元，估值达13.5亿美元", "url": "https://www.brandark.com/t/2nj7zzuF", "published_date": "2026-07-21T23:26:00+00:00", "entity": "其他", "category": "媒体", "type": "融资", "summary": "英国机器人初创公司Humanoid宣布完成1.52亿美元A轮融资，投后估值达到13.5亿美元。"},
]

# Deduplicate: keep existing items, add new ones not already in the set
added = 0
for item in new_items:
    if item["url"] not in existing_urls:
        existing_items.append(item)
        existing_urls.add(item["url"])
        added += 1

# Update the output
existing["items"] = existing_items
existing["total_items"] = len(existing_items)

with open(existing_path, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"Combined data saved to {existing_path}")
print(f"Existing items: {len(existing_items) - added}")
print(f"New items added: {added}")
print(f"Total items: {len(existing_items)}")

# Count by entity
from collections import Counter
ents = Counter(i['entity'] for i in existing_items)
print("\nEntity distribution:")
for e, c in ents.most_common(30):
    print(f"  {e}: {c}")

cats = Counter(i['category'] for i in existing_items)
print("\nCategory distribution:")
for c, n in cats.most_common():
    print(f"  {c}: {n}")

types = Counter(i['type'] for i in existing_items)
print("\nType distribution:")
for t, n in types.most_common():
    print(f"  {t}: {n}")
