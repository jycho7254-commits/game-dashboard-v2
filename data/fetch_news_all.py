#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3개국 게임 뉴스 소스 확대 수집 스크립트 v2
한국: 인벤, 루리웹, 게임동아, 게임메카, 네이버 게임뉴스
중국: 游民星空, 3DM游戏网, 游戏葡萄, 游戏茶馆
일본: 4Gamer, Famitsu
기존 데이터는 유지하면서 새로운 소스의 뉴스를 추가.
"""
import json
import re
import os
import sys
import time
import hashlib
from datetime import datetime

import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.now().strftime("%Y-%m-%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8,zh-CN;q=0.7,ja;q=0.6",
}


def get_soup(url, timeout=25):
    """GET + BeautifulSoup with proper encoding handling."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code != 200:
            return None
        # 인코딩 자동 감지 (apparent_encoding 우선, ISO-8859-1이면 대체)
        if r.encoding is None or r.encoding.lower() in ("iso-8859-1", "latin-1"):
            r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  [WARN] GET failed {url}: {type(e).__name__}: {str(e)[:80]}", file=sys.stderr)
        return None


def make_item(title, url, source, country, lang, game=""):
    """표준 뉴스 항목 생성"""
    return {
        "title": title.strip()[:150],
        "url": url.strip(),
        "source": source,
        "country": country,
        "date": TODAY,
        "game": game,
        "lang": lang,
    }


# ============================================================
# KOREA SOURCES
# ============================================================

def fetch_inven():
    """인벤 게임 뉴스"""
    items = []
    soup = get_soup("https://www.inven.co.kr/webzine/news/")
    if not soup:
        return items
    seen = set()
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 8:
            continue
        if href.startswith("//"):
            href = "https:" + href
        # 인벤 웹진 기사: ?news=NNNNNN 또는 ?idx=NNNN
        if re.search(r"inven\.co\.kr/webzine/news/.*\?(?:news|idx)=\d{4,}", href):
            key = href.split("#")[0]
            if key in seen:
                continue
            seen.add(key)
            items.append(make_item(title, href, "인벤", "kr", "ko"))
        if len(items) >= 10:
            break
    print(f"  인벤: {len(items)}개")
    return items[:10]


def fetch_ruliweb():
    """루리웹 게임 뉴스"""
    items = []
    soup = get_soup("https://bbs.ruliweb.com/news/board/1002")
    if not soup:
        soup = get_soup("https://bbs.ruliweb.com/news/board/1001")
    if not soup:
        return items
    seen = set()
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 6:
            continue
        if href.startswith("//"):
            href = "https:" + href
        # 루리웹 뉴스 글: /news/board/N/read/N
        if re.search(r"ruliweb\.com/news/board/\d+/read/\d+", href):
            key = href.split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            items.append(make_item(title, href, "루리웹", "kr", "ko"))
        if len(items) >= 10:
            break
    print(f"  루리웹: {len(items)}개")
    return items[:10]


def fetch_game_donga():
    """게임동아 뉴스"""
    items = []
    soup = get_soup("https://game.donga.com/3/")
    if not soup:
        soup = get_soup("https://game.donga.com/news/")
    if not soup:
        print("  [WARN] 게임동아 fetch 실패")
        return items
    seen = set()
    # /NNNNNN/ 형식의 기사 링크
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 8:
            continue
        # 정규화
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/") and not href.startswith("//"):
            href = "https://game.donga.com" + href
        # 숫자 ID 형식의 기사
        if re.search(r"game\.donga\.com/\d{5,}", href):
            key = href.split("?")[0].rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            items.append(make_item(title, href, "게임동아", "kr", "ko"))
        if len(items) >= 10:
            break
    print(f"  게임동아: {len(items)}개")
    return items[:10]


def fetch_gamemeca():
    """게임메카 뉴스"""
    items = []
    soup = get_soup("https://www.gamemeca.com/news.php")
    if not soup:
        print("  [WARN] 게임메카 fetch 실패")
        return items
    seen = set()
    # /view.php?gid=NNNNNNN 형식에서 제목이 있는 링크만
    for a in soup.find_all("a", href=re.compile(r"view\.php\?gid=")):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        # 제목이 비어있는 썸네일 링크는 제외
        if not title or len(title) < 6:
            continue
        if href.startswith("/"):
            href = "https://www.gamemeca.com" + href
        key = href.split("#")[0]
        if key in seen:
            continue
        seen.add(key)
        items.append(make_item(title, href, "게임메카", "kr", "ko"))
        if len(items) >= 10:
            break
    print(f"  게임메카: {len(items)}개")
    return items[:10]


def fetch_naver_game_news():
    """네이버 게임 뉴스"""
    items = []
    soup = get_soup("https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105")
    if not soup:
        return items
    seen = set()
    game_kw = ["게임", "모바일", "출시", "패치", "업데이트", "캐릭터",
               "이스포츠", "e스포츠", "PC방", "콘솔", "MMORPG", "라이브",
               "플레이", "오픈", "사전예약", "오버워치", "리그오브", "배틀그라운드"]
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 8:
            continue
        if href.startswith("/mnews"):
            href = "https://news.naver.com" + href
        if "news.naver.com" in href and "article" in href:
            if any(k in title for k in game_kw):
                key = href.split("?")[0]
                if key in seen:
                    continue
                seen.add(key)
                items.append(make_item(title, href, "네이버뉴스", "kr", "ko"))
        if len(items) >= 10:
            break
    print(f"  네이버: {len(items)}개")
    return items[:10]


# ============================================================
# CHINA SOURCES
# ============================================================

def fetch_gamersky():
    """游民星空 (Gamersky) 뉴스"""
    items = []
    # 재시도 로직 (연결 끊김 방지)
    soup = None
    for attempt in range(3):
        soup = get_soup("https://www.gamersky.com/news/", timeout=30)
        if soup:
            arts = soup.select(".tit a")
            if len(arts) > 3:
                break
        time.sleep(2)
    if not soup:
        print("  [WARN] 游民星空 fetch 실패")
        return items
    seen = set()
    # .tit a 선택자
    arts = soup.select(".tit a")
    for a in arts:
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 4 or not href:
            continue
        if re.search(r"gamersky\.com/news/\d+/\d+\.shtml", href):
            key = href.split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            items.append(make_item(title, href, "游民星空", "cn", "zh"))
        if len(items) >= 15:
            break
    print(f"  游民星空: {len(items)}개")
    return items[:15]


def fetch_3dmgame():
    """3DM游戏网 뉴스"""
    items = []
    soup = get_soup("https://www.3dmgame.com/news/")
    if not soup:
        print("  [WARN] 3DM fetch 실패")
        return items
    seen = set()
    # 3dmgame.com/news/YYYYMM/N.html 패턴
    for a in soup.find_all("a", href=re.compile(r"3dmgame\.com/news/\d+/\d+\.html")):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        # "游戏新闻" 접두사 제거
        if title.startswith("游戏新闻"):
            title = title[4:]
        if not title or len(title) < 4:
            continue
        key = href.split("?")[0]
        if key in seen:
            continue
        seen.add(key)
        items.append(make_item(title, href, "3DM游戏网", "cn", "zh"))
        if len(items) >= 12:
            break
    print(f"  3DM: {len(items)}개")
    return items[:12]


def fetch_youxiputao():
    """游戏葡萄 뉴스"""
    items = []
    soup = get_soup("https://youxiputao.com/")
    if not soup:
        print("  [WARN] 游戏葡萄 fetch 실패")
        return items
    seen = set()
    # youxiputao.com/articles/N 또는 /N
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 4:
            continue
        if href.startswith("/"):
            href = "https://youxiputao.com" + href
        # 기사 링크 (숫자 ID)
        if re.search(r"youxiputao\.com/(?:articles?/)?\d{3,}", href) or \
           re.search(r"youxiputao\.com/\d{4}", href):
            # 메인 페이지 제외
            if href.rstrip("/") == "https://youxiputao.com":
                continue
            key = href.split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            items.append(make_item(title, href, "游戏葡萄", "cn", "zh"))
        if len(items) >= 10:
            break
    print(f"  游戏葡萄: {len(items)}개")
    return items[:10]


def fetch_youxichaguan():
    """游戏茶馆 뉴스 (기존 소스) - DNS 실패 시 백업 데이터 사용"""
    items = []
    soup = get_soup("https://youxichaguan.com/")
    if soup:
        seen = set()
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            title = a.get_text(strip=True)
            if not title or len(title) < 6:
                continue
            if re.search(r"youxichaguan\.com/archives/\d+", href):
                key = href.split("?")[0]
                if key in seen:
                    continue
                seen.add(key)
                items.append(make_item(title, href, "游戏茶馆", "cn", "zh"))
            if len(items) >= 10:
                break
    # DNS 실패 시 백업 데이터 로드
    if not items:
        backup_path = os.path.join(DATA_DIR, "youxichaguan_backup.json")
        if os.path.exists(backup_path):
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                print(f"  游戏茶馆: 백업 데이터 사용 ({len(items)}개)")
                return items[:15]
            except Exception:
                pass
        print("  [WARN] 游戏茶馆 fetch 실패 (백업도 없음)")
        return items
    print(f"  游戏茶馆: {len(items)}개")
    return items[:10]


# ============================================================
# JAPAN SOURCES
# ============================================================

def fetch_4gamer():
    """4Gamer 뉴스"""
    items = []
    soup = get_soup("https://www.4gamer.net/")
    if not soup:
        print("  [WARN] 4Gamer fetch 실패")
        return items
    seen = set()
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 4:
            continue
        if re.search(r"4gamer\.net/games/\d+/G\d+/\d+/", href):
            key = href.split("?")[0].rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            items.append(make_item(title, href, "4Gamer", "jp", "ja"))
        if len(items) >= 12:
            break
    print(f"  4Gamer: {len(items)}개")
    return items[:12]


def fetch_famitsu():
    """Famitsu 뉴스"""
    items = []
    soup = get_soup("https://www.famitsu.com/category/news/page/1")
    if not soup:
        soup = get_soup("https://www.famitsu.com/")
    if not soup:
        print("  [WARN] Famitsu fetch 실패")
        return items
    seen = set()
    # famitsu.com/article/YYYYMM/NNNNN 패턴
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if not title or len(title) < 4:
            continue
        if href.startswith("/"):
            href = "https://www.famitsu.com" + href
        if re.search(r"famitsu\.com/article/\d+/\d+", href):
            key = href.split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            items.append(make_item(title, href, "Famitsu", "jp", "ja"))
        if len(items) >= 12:
            break
    print(f"  Famitsu: {len(items)}개")
    return items[:12]


# ============================================================
# MERGE & DEDUP
# ============================================================

def load_existing(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception as e:
            print(f"  [WARN] 기존 파일 로드 실패 {path}: {e}")
    return []


def dedup_key(item):
    # URL에서 쿼리스트링도 포함하여 dedup (인벤 ?news=, 게임메카 ?gid= 등은 URL 식별에 필수)
    url = item.get("url", "").rstrip("/")
    title = item.get("title", "").strip()
    if url:
        return url
    return hashlib.md5(title.encode()).hexdigest()


def merge_news(existing, new_items):
    seen = set()
    merged = []
    for it in existing:
        k = dedup_key(it)
        if k in seen:
            continue
        seen.add(k)
        merged.append(it)
    added = 0
    for it in new_items:
        k = dedup_key(it)
        if k in seen:
            continue
        seen.add(k)
        merged.append(it)
        added += 1
    print(f"  기존: {len(existing)}개, 새로 추가: {added}개, 총: {len(merged)}개")
    return merged


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("게임 뉴스 3개국 수집 시작 (v2)")
    print(f"날짜: {TODAY}")
    print("=" * 60)

    # ---------------- 한국 ----------------
    print("\n[한국 뉴스 수집]")
    kr_new = []
    print("- 인벤...")
    kr_new += fetch_inven()
    time.sleep(0.5)
    print("- 루리웹...")
    kr_new += fetch_ruliweb()
    time.sleep(0.5)
    print("- 게임동아...")
    kr_new += fetch_game_donga()
    time.sleep(0.5)
    print("- 게임메카...")
    kr_new += fetch_gamemeca()
    time.sleep(0.5)
    print("- 네이버...")
    kr_new += fetch_naver_game_news()

    kr_path = os.path.join(DATA_DIR, "kr_news.json")
    kr_existing = load_existing(kr_path)
    print(f"\n[한국] 병합:")
    kr_merged = merge_news(kr_existing, kr_new)
    with open(kr_path, "w", encoding="utf-8") as f:
        json.dump(kr_merged, f, ensure_ascii=False, indent=2)
    print(f"  저장 완료: {kr_path} ({len(kr_merged)}개)")

    # ---------------- 중국 ----------------
    print("\n[중국 뉴스 수집]")
    cn_new = []
    print("- 游民星空...")
    cn_new += fetch_gamersky()
    time.sleep(0.5)
    print("- 3DM游戏网...")
    cn_new += fetch_3dmgame()
    time.sleep(0.5)
    print("- 游戏葡萄...")
    cn_new += fetch_youxiputao()
    time.sleep(0.5)
    print("- 游戏茶馆...")
    cn_new += fetch_youxichaguan()

    cn_path = os.path.join(DATA_DIR, "cn_news.json")
    cn_existing = load_existing(cn_path)
    print(f"\n[중국] 병합:")
    cn_merged = merge_news(cn_existing, cn_new)
    with open(cn_path, "w", encoding="utf-8") as f:
        json.dump(cn_merged, f, ensure_ascii=False, indent=2)
    print(f"  저장 완료: {cn_path} ({len(cn_merged)}개)")

    # ---------------- 일본 ----------------
    print("\n[일본 뉴스 수집]")
    jp_new = []
    print("- 4Gamer...")
    jp_new += fetch_4gamer()
    time.sleep(0.5)
    print("- Famitsu...")
    jp_new += fetch_famitsu()

    jp_path = os.path.join(DATA_DIR, "jp_news.json")
    jp_existing = load_existing(jp_path)
    print(f"\n[일본] 병합:")
    jp_merged = merge_news(jp_existing, jp_new)
    with open(jp_path, "w", encoding="utf-8") as f:
        json.dump(jp_merged, f, ensure_ascii=False, indent=2)
    print(f"  저장 완료: {jp_path} ({len(jp_merged)}개)")

    # ---------------- 요약 ----------------
    print("\n" + "=" * 60)
    print("수집 완료 요약")
    print("=" * 60)
    print(f"한국 (kr_news.json): {len(kr_merged)}개")
    print(f"중국 (cn_news.json): {len(cn_merged)}개")
    print(f"일본 (jp_news.json): {len(jp_merged)}개")

    for label, data in [("한국", kr_merged), ("중국", cn_merged), ("일본", jp_merged)]:
        sources = {}
        for it in data:
            s = it.get("source", "?")
            sources[s] = sources.get(s, 0) + 1
        print(f"\n[{label} 소스별]")
        for s, c in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"  {s}: {c}개")

    # 목표 달성 여부
    print("\n[목표 달성 여부]")
    print(f"  한국 20개 이상: {'✓' if len(kr_merged)>=20 else '✗ '+str(len(kr_merged))}")
    print(f"  중국 20개 이상: {'✓' if len(cn_merged)>=20 else '✗ '+str(len(cn_merged))}")
    print(f"  일본 20개 이상: {'✓' if len(jp_merged)>=20 else '✗ '+str(len(jp_merged))}")


if __name__ == "__main__":
    main()
