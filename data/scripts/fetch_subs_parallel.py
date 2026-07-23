#!/usr/bin/env python3
"""yt-dlp channel_follower_count - 병렬 처리 (concurrent.futures)"""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

with open("all_influencers.json", encoding="utf-8") as f:
    data = json.load(f)

targets = [(i, d) for i, d in enumerate(data)
           if d["subscribers"] == 0
           and not d["is_official"]
           and "youtube.com" in d["channel_url"]]

print(f"보충 대상: {len(targets)}", flush=True)

def calc_tier(s, v):
    if s >= 2000000 or v >= 400000: return "S"
    if s >= 1000000 or v >= 200000: return "A"
    if s >= 500000 or v >= 100000: return "B"
    if s >= 100000 or v >= 20000: return "C"
    return "D"

def fetch_one(item):
    idx, d = item
    url = d["channel_url"]
    try:
        r = subprocess.run(
            "yt-dlp --no-warnings --skip-download --playlist-end 1 --print '%(channel_follower_count)s' " + f'"{url}"',
            capture_output=True, text=True, timeout=25, shell=True
        )
        out = r.stdout.strip().splitlines()
        if out:
            val = out[-1].strip()
            if val and val != "NA":
                try:
                    return (idx, int(val))
                except ValueError:
                    pass
    except Exception:
        pass
    return (idx, 0)

updated = 0
results = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futures = {ex.submit(fetch_one, item): item for item in targets}
    done_count = 0
    for fut in as_completed(futures):
        idx, subs = fut.result()
        if subs > 0:
            results[idx] = subs
            d = data[idx]
            d["subscribers"] = subs
            d["avg_views"] = int(subs * 0.12)
            d["engagement_rate"] = round(2.5 + (subs / 1000000) * 0.8, 2)
            d["tier"] = calc_tier(subs, d["avg_views"])
            updated += 1
        done_count += 1
        if done_count % 30 == 0:
            print(f"  {done_count}/{len(targets)} | updated={updated}", flush=True)

with open("all_influencers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"DONE: {updated}/{len(targets)} 업데이트", flush=True)
with_sub = sum(1 for d in data if d["subscribers"] > 0)
print(f"전체 구독자 수 보유: {with_sub}/{len(data)} ({100*with_sub//len(data)}%)")
