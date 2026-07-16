#!/usr/bin/env python3
"""채널 about 페이지에서 구독자 수/총조회수 파싱 (빠른 curl 기반)"""
import json, subprocess, re, sys, time

cc = sys.argv[1]
with open(f"{cc}_search_results.json", encoding="utf-8") as f:
    channels = json.load(f)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# 구독자 수 파싱 (다국어)
SUB_PATTERNS = [
    # 한국어: 구독자 3.82천명 / 1.01만명 / 393명
    re.compile(r'"label":"구독자\s*([\d.]+)\s*([천만억]*)\s*명"'),
    # 영어: 3.82K subscribers / 1.01M subscribers
    re.compile(r'"label":"([\d.]+)\s*([KMB]?)\s*subscribers"', re.I),
    # 일본어: 登録者 3.82千人 / 1.01万人
    re.compile(r'"label":"登録者\s*([\d.]+)\s*([千万億]*)\s*人"'),
    # 중국어: 3.82千位订阅者 / 1.01万位订阅者 / 393位订阅者
    re.compile(r'"label":"([\d.]+)\s*([千万亿]?)\s*位订阅者"'),
    # fallback: subscriberCountText simpleText
    re.compile(r'"subscriberCountText":\{"simpleText":"([^"]+)"'),
]

MULTIPLIERS = {
    '천': 1000, '만': 10000, '억': 100000000,
    'K': 1000, 'M': 1000000, 'B': 1000000000,
    '千': 1000, '万': 10000, '億': 100000000, '亿': 100000000,
}

def parse_sub_from_label(label):
    """'구독자 3.82천명' -> 3820"""
    for pat in SUB_PATTERNS:
        m = pat.search(label)
        if m:
            if pat == SUB_PATTERNS[-1]:
                # simpleText 형식: "3.82K subscribers" 등
                txt = m.group(1)
                return parse_simpletext(txt)
            num_str, unit = m.group(1), m.group(2)
            try:
                num = float(num_str)
                mult = MULTIPLIERS.get(unit, 1)
                return int(num * mult)
            except:
                continue
    return 0

def parse_simpletext(txt):
    """'3.82K subscribers' / '382K subscribers' / '1.01M subscribers' -> int"""
    m = re.match(r'([\d.]+)\s*([KMB]?)', txt, re.I)
    if m:
        num = float(m.group(1))
        unit = m.group(2).upper()
        mult = {'K':1000,'M':1000000,'B':1000000000,'':1}.get(unit,1)
        return int(num*mult)
    return 0

def fetch_about(url):
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "12", url,
             "-H", f"User-Agent: {UA}",
             "-H", "Accept-Language: ko-KR,ko;q=0.9,en;q=0.8"],
            capture_output=True, text=True, timeout=15
        )
        return r.stdout
    except:
        return ""

def get_subscribers(html):
    """HTML에서 첫번째(=메인 채널) 구독자 수 추출"""
    # accessibility label에서 추출
    for pat in SUB_PATTERNS:
        m = pat.search(html)
        if m:
            if pat == SUB_PATTERNS[-1]:
                return parse_simpletext(m.group(1))
            num_str, unit = m.group(1), m.group(2)
            try:
                num = float(num_str)
                mult = MULTIPLIERS.get(unit, 1)
                return int(num * mult)
            except:
                continue
    return 0

def get_total_views(html):
    """총 조회수 추출 (가능한 경우)"""
    # 한국어: 조회수 1,234,567회 / 영어: 1,234,567 views
    m = re.search(r'"viewCountText":\{"simpleText":"([\d,]+)\s*회views?"', html)
    if not m:
        m = re.search(r'"viewCountText":\{"simpleText":"([\d,]+)\s*views"', html, re.I)
    if m:
        return int(m.group(1).replace(",", ""))
    return 0

results = []
total = len(channels)
for i, ch in enumerate(channels):
    url = ch["url"]
    # /about URL로 변환
    if url.endswith("/videos") or "/videos" in url:
        about_url = url.split("/videos")[0] + "/about"
    elif "/channel/" in url:
        about_url = url.rstrip("/") + "/about"
    elif "/@" in url or "/user/" in url or "/c/" in url:
        about_url = url.rstrip("/") + "/about"
    else:
        about_url = url.rstrip("/") + "/about"

    html = fetch_about(about_url)
    subs = get_subscribers(html) if html else 0
    views = get_total_views(html) if html else 0

    results.append({
        "name": ch["name"],
        "url": url,
        "subscribers": subs,
        "total_views": views,
        "queries": ch.get("queries", [])
    })

    if (i + 1) % 15 == 0:
        with_subs = sum(1 for r in results if r["subscribers"] > 0)
        print(f"[{cc}] {i+1}/{total} | subs_found={with_subs}", flush=True)

results.sort(key=lambda x: x["subscribers"], reverse=True)

with open(f"{cc}_with_subs.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with_subs = sum(1 for r in results if r["subscribers"] > 0)
print(f"[{cc}] DONE: {len(results)} channels, {with_subs} with subscriber data")
print(f"[{cc}] Top 5:")
for r in results[:5]:
    print(f"    {r['name']}: {r['subscribers']:,} subs")
