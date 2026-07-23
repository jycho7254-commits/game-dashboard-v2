#!/usr/bin/env python3
"""日本ゲームインフルエンサー大規模検索 (yt-dlp)"""
import subprocess, json

QUERIES = [
    "原神 日本 実況",
    "モンスト ユーチューバー",
    "ブルーアーカイブ 実況",
    "プロセカ ユーチューバー",
    "ウマ娘 ユーチューバー",
    "FGO 実況 ユーチューバー",
    "ゲーム実況 人気",
    "スプラトゥーン 実況",
    "マイクラ 日本 実況",
    "ホロライブ ゲーム",
    "にじさんじ ゲーム実況",
    "Apex 日本 実況者",
    "スマホゲーム 実況 日本",
    "ゲーム攻略 チャンネル",
    "パズドラ ユーチューバー",
    "原神 攻略 日本",
    "ストライクウィッチーズ",
    "アイドルマスター 実況",
    "ポケモン 日本 実況",
    "ゼルダ 日本 実況",
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

with open("jp_search_results.json", "w", encoding="utf-8") as f:
    json.dump(list(found.values()), f, ensure_ascii=False, indent=2)

print(f"DONE: {len(found)} unique channels")
