#!/usr/bin/env python3
"""中国游戏网红大规模搜索 (yt-dlp)"""
import subprocess, json

QUERIES = [
    "原神 实况 UP主",
    "王者荣耀 主播",
    "和平精英 主播",
    "崩坏星穹铁道 UP主",
    "游戏实况 UP主",
    "英雄联盟 主播 中国",
    "手游 UP主",
    "游戏解说 B站",
    "明日方舟 UP主",
    "我的世界 中国 UP主",
    "绝地求生 主播",
    "原神 攻略 UP主",
    "游戏测评 UP主",
    "网游 主播 B站",
    "蛋仔派对 UP主",
    "第五人格 UP主",
    "永劫无间 主播",
    "阴阳师 UP主",
    "暗区突围 主播",
    "无畏契约 主播",
]

found = {}
for q in QUERIES:
    try:
        r = subprocess.run(
            ["yt-dlp", f"ytsearch10:{q}", "--flat-playlist",
             "--print", "%(channel)s|||%(channel_url)s",
             "--skip-download", "--no-warnings"],
            capture_output=True, text=True, timeout=45
        )
        for line in r.stdout.strip().split("\n"):
            if "|||" in line:
                name, url = line.split("|||", 1)
                name = name.strip()
                url = url.strip()
                if not url or url == "NA":
                    continue
                if url not in found:
                    found[url] = {"name": name, "url": url, "queries": []}
                found[url]["queries"].append(q)
        print(f"[{q}] done", flush=True)
    except subprocess.TimeoutExpired:
        print(f"[{q}] TIMEOUT", flush=True)
    except Exception as e:
        print(f"[{q}] ERROR: {e}", flush=True)

with open("cn_search_results.json", "w", encoding="utf-8") as f:
    json.dump(list(found.values()), f, ensure_ascii=False, indent=2)

print(f"DONE: {len(found)} unique channels")
