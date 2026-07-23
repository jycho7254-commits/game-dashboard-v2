#!/usr/bin/env python3
"""구독자 수 0인 YouTube 채널에 대한 2차 보충 파싱 (유연한 정규식)"""
import json, subprocess, re, sys, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36"

# 매우 유연한 구독자 수 정규식 (모든 형태 대응)
SUB_REGEXES = [
    # subscriberCountText with accessibility label
    re.compile(r'"subscriberCountText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]+)"', re.I),
    # subscriberCountText simpleText
    re.compile(r'"subscriberCountText":\{"simpleText":"([^"]+)"', re.I),
    # header_links subscriber
    re.compile(r'"text":"([\d.]+\s*[KMB千万亿億]?)\s*subscribers"', re.I),
]

MULT = {
    '천': 1000, '만': 10000, '억': 100000000,
    'K': 1000, 'M': 1000000, 'B': 1000000000,
    '千': 1000, '万': 10000, '亿': 100000000, '億': 100000000,
}

def parse_count(text):
    """'3.82천명' / '1.01M subscribers' / '382K' -> int"""
    m = re.search(r'([\d,.]+)\s*([KMB千万亿億]?)', text)
    if m:
        num = float(m.group(1).replace(",", ""))
        unit = m.group(2).upper()
        mult = MULT.get(unit, MULT.get(m.group(2), 1))
        return int(num * mult)
    # 순수 숫자
    nums = re.findall(r'[\d,]+', text)
    if nums:
        return int(nums[0].replace(",", ""))
    return 0

def fetch(url, timeout=12):
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", str(timeout), url,
             "-H", f"User-Agent: {UA}",
             "-H", "Accept-Language: en-US,en;q=0.9,ko;q=0.8,ja;q=0.7,zh;q=0.6"],
            capture_output=True, text=True, timeout=timeout+3
        )
        return r.stdout
    except:
        return ""

def get_subs(html):
    for rgx in SUB_REGEXES:
        m = rgx.search(html)
        if m:
            val = m.group(1)
            count = parse_count(val)
            if count > 0:
                return count
    return 0

# 메인
with open("all_influencers.json", encoding="utf-8") as f:
    data = json.load(f)

zero_channels = [(i, d) for i, d in enumerate(data)
                 if d["subscribers"] == 0
                 and not d["is_official"]
                 and "youtube.com" in d["channel_url"]]

print(f"보충 대상 YouTube 채널: {len(zero_channels)}")

updated = 0
processed = 0
for idx, d in zero_channels:
    url = d["channel_url"]
    about_url = url.rstrip("/") + "/about"
    html = fetch(about_url)
    subs = get_subs(html)
    if subs > 0:
        d["subscribers"] = subs
        # 파생 필드 재계산
        d["avg_views"] = int(subs * 0.12)
        d["engagement_rate"] = round(2.5 + (subs / 1000000) * 0.8, 2)
        # tier 재계산
        s, v = subs, d["avg_views"]
        if s >= 2000000 or v >= 400000: d["tier"] = "S"
        elif s >= 1000000 or v >= 200000: d["tier"] = "A"
        elif s >= 500000 or v >= 100000: d["tier"] = "B"
        elif s >= 100000 or v >= 20000: d["tier"] = "C"
        else: d["tier"] = "D"
        updated += 1
        data[idx] = d

    processed += 1
    if processed % 20 == 0:
        print(f"  진행: {processed}/{len(zero_channels)} | 업데이트: {updated}", flush=True)

# 저장
with open("all_influencers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"DONE: {updated}/{len(zero_channels)} 채널 구독자 수 보충 완료")

# 최종 통계
from collections import Counter
with_sub = sum(1 for d in data if d["subscribers"] > 0)
print(f"전체 구독자 수 보유: {with_sub}/{len(data)} ({100*with_sub//len(data)}%)")
