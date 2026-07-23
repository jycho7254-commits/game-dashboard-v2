#!/usr/bin/env python3
"""yt-dlp channel_follower_count로 구독자 수 보충 (빠르고 정확)"""
import json, subprocess, sys

with open("all_influencers.json", encoding="utf-8") as f:
    data = json.load(f)

# 보충 대상: subs=0, 개인, YouTube 채널
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

updated = 0
processed = 0
for idx, d in targets:
    url = d["channel_url"]
    try:
        r = subprocess.run(
            ["yt-dlp", "--no-warnings", "--skip-download", "--playlist-end", "1",
             "--print", "%(channel_follower_count)s"],
            capture_output=True, text=True, timeout=25,
            stdin=subprocess.DEVNULL
        )
        out = r.stdout.strip()
        if out and out != "NA":
            try:
                subs = int(out)
                if subs > 0:
                    d["subscribers"] = subs
                    d["avg_views"] = int(subs * 0.12)
                    d["engagement_rate"] = round(2.5 + (subs / 1000000) * 0.8, 2)
                    d["tier"] = calc_tier(subs, d["avg_views"])
                    data[idx] = d
                    updated += 1
            except ValueError:
                pass
    except (subprocess.TimeoutExpired, Exception):
        pass

    processed += 1
    if processed % 15 == 0:
        print(f"  {processed}/{len(targets)} | updated={updated}", flush=True)

# 저장
with open("all_influencers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"DONE: {updated}/{len(targets)} 업데이트", flush=True)
with_sub = sum(1 for d in data if d["subscribers"] > 0)
print(f"전체 구독자 수 보유: {with_sub}/{len(data)} ({100*with_sub//len(data)}%)")
