#!/usr/bin/env python3
"""한국 게임 인플루언서 대량 검색 (yt-dlp)"""
import subprocess, json, sys

QUERIES = [
    "배틀그라운드 유튜버",
    "발로란트 한국 유튜버",
    "로스트아크 유튜버",
    "원신 한국 공략",
    "니케 승리의 여신 유튜버",
    "모바일 게임 유튜버 한국",
    "림버스 컴퍼니 유튜버",
    "붕괴 스타레일 한국",
    "오딘 발할라 라이징 유튜버",
    "게임 리뷰 유튜버 한국",
    "로블록스 한국 유튜버",
    "마인크래프트 한국 유튜버",
    "FPS 게임 유튜버 한국",
    "게임 공략 유튜버",
    "인디 게임 유튜버 한국",
    "리그오브레전드 한국 유튜버",
    "서든어택 유튜버",
    "메이플스토리 유튜버",
    "디아블로 한국 유튜버",
    "닌텐도 한국 유튜버",
]

found = {}  # channel_url -> {name, queries}
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
        print(f"[{q}] {len(r.stdout.strip().splitlines())} rows", flush=True)
    except subprocess.TimeoutExpired:
        print(f"[{q}] TIMEOUT", flush=True)
    except Exception as e:
        print(f"[{q}] ERROR: {e}", flush=True)

with open("kr_search_results.json", "w", encoding="utf-8") as f:
    json.dump(list(found.values()), f, ensure_ascii=False, indent=2)

print(f"DONE: {len(found)} unique channels")
