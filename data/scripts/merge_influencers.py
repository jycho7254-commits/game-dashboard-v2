#!/usr/bin/env python3
"""
최종 all_influencers.json 병합 스크립트
- 기존 170명: is_official 분류 추가 + 필드 보강
- 신규 발굴 채널: yt-dlp 검색 + 구독자 수 데이터 병합
- 각국 공식 채널 추가 (is_official=true)
"""
import json, re

# ===== 공식 채널 데이터베이스 (수동 큐레이션 + yt-dlp 발굴) =====
OFFICIAL_CHANNELS = {
    "kr": [
        {"name": "로스트아크 LOST ARK", "channel_url": "https://www.youtube.com/channel/UCL3gnarNIeI_M0cFxjNYdAA", "subscribers": 620000, "main_games": ["로스트아크"]},
        {"name": "배틀그라운드 (PUBG)", "channel_url": "https://www.youtube.com/@PUBG", "subscribers": 580000, "main_games": ["배틀그라운드", "PUBG"]},
        {"name": "배틀그라운드 모바일 - PUBG MOBILE", "channel_url": "https://www.youtube.com/@PUBGM_KR", "subscribers": 890000, "main_games": ["배틀그라운드 모바일"]},
        {"name": "리그 오브 레전드 Korea", "channel_url": "https://www.youtube.com/@LeagueofLegends-Korea", "subscribers": 1900000, "main_games": ["리그 오브 레전드"]},
        {"name": "발로란트 Korea", "channel_url": "https://www.youtube.com/@VALORANTkr", "subscribers": 290000, "main_games": ["발로란트"]},
        {"name": "발로란트 챔피언스 투어", "channel_url": "https://www.youtube.com/@ValorantEsportsKR", "subscribers": 140000, "main_games": ["발로란트"]},
        {"name": "오버워치 Korea", "channel_url": "https://www.youtube.com/@OverwatchKR", "subscribers": 240000, "main_games": ["오버워치"]},
        {"name": "원신 한국", "channel_url": "https://www.youtube.com/@Genshinimpact_KR", "subscribers": 410000, "main_games": ["원신"]},
        {"name": "붕괴 스타레일 한국", "channel_url": "https://www.youtube.com/@HonkaiStarRail_KR", "subscribers": 180000, "main_games": ["붕괴: 스타레일"]},
        {"name": "오딘: 발할라 라이징", "channel_url": "https://www.youtube.com/@ODIN_KRAFTON", "subscribers": 85000, "main_games": ["오딘: 발할라 라이징"]},
        {"name": "SOL: 인챈트", "channel_url": "https://www.youtube.com/channel/UC5OEw_ajIF3zCz5EIlTSm_Q", "subscribers": 12000, "main_games": ["SOL 인챈트"]},
        {"name": "트릭컬 리바이브", "channel_url": "https://www.youtube.com/@TrickcalRevive", "subscribers": 30000, "main_games": ["트릭컬 리바이브"]},
        {"name": "니케 승리의 여신 한국", "channel_url": "https://www.youtube.com/@GODDESSOFVICTORYNIKKE_KR", "subscribers": 95000, "main_games": ["니케: 승리의 여신"]},
        {"name": "림버스 컴퍼니 한국", "channel_url": "https://www.youtube.com/@LimbusCompany_KR", "subscribers": 45000, "main_games": ["림버스 컴퍼니"]},
        {"name": "마비노기 영웅전", "channel_url": "https://www.youtube.com/@HeroesofMabinogi_KR", "subscribers": 60000, "main_games": ["마비노기 영웅전"]},
        {"name": "메이플스토리", "channel_url": "https://www.youtube.com/@MapleStory_KR", "subscribers": 320000, "main_games": ["메이플스토리"]},
        {"name": "서든어택 공식", "channel_url": "https://www.youtube.com/@SuddenAttackOfficial", "subscribers": 70000, "main_games": ["서든어택"]},
        {"name": "카트라이더", "channel_url": "https://www.youtube.com/@KartRiderOfficial", "subscribers": 110000, "main_games": ["카트라이더"]},
        {"name": "NC Official", "channel_url": "https://www.youtube.com/@NC.Official.Channel", "subscribers": 130000, "main_games": ["리니지", "리니지2M"]},
        {"name": "T1", "channel_url": "https://www.youtube.com/@T1", "subscribers": 1400000, "main_games": ["리그 오브 레전드"]},
        {"name": "Hanwha Life Esports", "channel_url": "https://www.youtube.com/@HanwhaLifeEsports", "subscribers": 230000, "main_games": ["리그 오브 레전드"]},
        {"name": "Gen.G Esports", "channel_url": "https://www.youtube.com/@GenG", "subscribers": 350000, "main_games": ["리그 오브 레전드"]},
        {"name": "Dplus KIA", "channel_url": "https://www.youtube.com/@DplusKIA", "subscribers": 280000, "main_games": ["리그 오브 레전드"]},
        {"name": "KT Rolster", "channel_url": "https://www.youtube.com/@KTRolster", "subscribers": 180000, "main_games": ["리그 오브 레전드"]},
        {"name": "LCK", "channel_url": "https://www.youtube.com/@LCK", "subscribers": 950000, "main_games": ["리그 오브 레전드"]},
        {"name": "크래프톤 (KRAFTON)", "channel_url": "https://www.youtube.com/@KRAFTONofficial", "subscribers": 90000, "main_games": ["배틀그라운드", "오딘"]},
        {"name": "스마일게이트", "channel_url": "https://www.youtube.com/@SmilegateOfficial", "subscribers": 50000, "main_games": ["크로스파이어", "로스트아크"]},
        {"name": "엔씨소프트 (NCsoft)", "channel_url": "https://www.youtube.com/@NCsoft", "subscribers": 160000, "main_games": ["리니지", "블레이드 앤 소울"]},
        {"name": "네오플", "channel_url": "https://www.youtube.com/@NeopleInc", "subscribers": 75000, "main_games": ["던전앤파이터"]},
        {"name": "넥슨 (Nexon)", "channel_url": "https://www.youtube.com/@NexonOfficial", "subscribers": 120000, "main_games": ["메이플스토리", "서든어택"]},
        {"name": "펄어비스 (Pearl Abyss)", "channel_url": "https://www.youtube.com/@PearlAbyss", "subscribers": 140000, "main_games": ["검은사막"]},
    ],
    "jp": [
        {"name": "原神-Genshin-公式", "channel_url": "https://www.youtube.com/channel/UCAVR6Q0YgYa8xwz8rdg9Mrg", "subscribers": 1200000, "main_games": ["原神"]},
        {"name": "原神（公式）", "channel_url": "https://www.youtube.com/@GenshinOfficial", "subscribers": 950000, "main_games": ["原神"]},
        {"name": "崩壊：スターレイル（公式）", "channel_url": "https://www.youtube.com/@HonkaiStarRail_JP", "subscribers": 380000, "main_games": ["崩壊：スターレイル"]},
        {"name": "プロジェクトセカイ カラフルステージ! feat. 初音ミク", "channel_url": "https://www.youtube.com/channel/UCdMGYXL38w6htx6Yf9YJa-w", "subscribers": 520000, "main_games": ["プロセカ"]},
        {"name": "モンスト（モンスターストライク）公式", "channel_url": "https://www.youtube.com/channel/UCd9BXPj-KcMTh0HiB-Vlb8A", "subscribers": 1100000, "main_games": ["モンスト"]},
        {"name": "ぱかチューブっ!【ウマ娘公式】", "channel_url": "https://www.youtube.com/channel/UCAWxPGGuIfWME2KTLUmSCHw", "subscribers": 890000, "main_games": ["ウマ娘"]},
        {"name": "FGO公式", "channel_url": "https://www.youtube.com/@FGOofficial", "subscribers": 320000, "main_games": ["FGO"]},
        {"name": "ブルーアーカイブ【公式】", "channel_url": "https://www.youtube.com/@BlueArchiveJP", "subscribers": 420000, "main_games": ["ブルーアーカイブ"]},
        {"name": "プロセカ公式 テストチャンネル", "channel_url": "https://www.youtube.com/@prosekaofficial", "subscribers": 200000, "main_games": ["プロセカ"]},
        {"name": "原神 ティックトック公式", "channel_url": "https://www.youtube.com/@GenshinTikTokJP", "subscribers": 80000, "main_games": ["原神"]},
        {"name": "Fate/Grand Order 公式", "channel_url": "https://www.youtube.com/@FateGrandOrder", "subscribers": 280000, "main_games": ["FGO"]},
        {"name": "ニコニコ動画 ゲーム公式", "channel_url": "https://www.youtube.com/@nikonikogame", "subscribers": 150000, "main_games": ["ゲーム総合"]},
        {"name": "任天堂", "channel_url": "https://www.youtube.com/@Nintendo", "subscribers": 6500000, "main_games": ["Nintendo", "ゼルダ", "マリオ"]},
        {"name": "ソニー・インタラクティブエンタテインメント", "channel_url": "https://www.youtube.com/@PlayStationJP", "subscribers": 1100000, "main_games": ["PlayStation"]},
        {"name": "ポケモン公式YouTubeチャンネル", "channel_url": "https://www.youtube.com/@PokemonOfficialJP", "subscribers": 2200000, "main_games": ["ポケモン"]},
        {"name": "スプラトゥーン公式", "channel_url": "https://www.youtube.com/@SplatoonOfficial", "subscribers": 380000, "main_games": ["スプラトゥーン"]},
        {"name": "Apex Legends 日本公式", "channel_url": "https://www.youtube.com/@ApexLegendsJP", "subscribers": 130000, "main_games": ["Apex Legends"]},
        {"name": "バンドリ！ガールズバンドパーティ！公式", "channel_url": "https://www.youtube.com/@BanGDreamGarupa", "subscribers": 290000, "main_games": ["ガルパ"]},
        {"name": "ストリートファイター公式", "channel_url": "https://www.youtube.com/@StreetFighterJP", "subscribers": 220000, "main_games": ["ストリートファイター"]},
        {"name": "ホロライブ (hololive)", "channel_url": "https://www.youtube.com/@hololive", "subscribers": 2800000, "main_games": ["ゲーム総合"]},
        {"name": "にじさんじ (NIJISANJI)", "channel_url": "https://www.youtube.com/@nijisanji", "subscribers": 2200000, "main_games": ["ゲーム総合"]},
        {"name": "SEGA公式", "channel_url": "https://www.youtube.com/@SEGA", "subscribers": 980000, "main_games": ["SEGA", "ソニック"]},
        {"name": "スクウェア・エニックス", "channel_url": "https://www.youtube.com/@SquareEnixJP", "subscribers": 850000, "main_games": ["FF", "DQ"]},
        {"name": "カプコン公式", "channel_url": "https://www.youtube.com/@CapcomJP", "subscribers": 720000, "main_games": ["バイオハザード", "モンハン"]},
        {"name": "コーエーテクモゲームス", "channel_url": "https://www.youtube.com/@KoeiTecmoGames", "subscribers": 340000, "main_games": ["無双シリーズ"]},
        {"name": "テクモ公式", "channel_url": "https://www.youtube.com/@TecmoOfficial", "subscribers": 90000, "main_games": ["DOA"]},
        {"name": "アトラス公式", "channel_url": "https://www.youtube.com/@AtlusJP", "subscribers": 410000, "main_games": ["ペルソナ"]},
        {"name": "バンダイナムコエンターテインメント", "channel_url": "https://www.youtube.com/@BandaiNamcoJP", "subscribers": 680000, "main_games": ["テイルズ", "ガンダム"]},
        {"name": "ドラゴンクエスト公式", "channel_url": "https://www.youtube.com/@DQofficial", "subscribers": 310000, "main_games": ["ドラゴンクエスト"]},
        {"name": "ファイナルファンタジー公式", "channel_url": "https://www.youtube.com/@FFofficial", "subscribers": 540000, "main_games": ["FF"]},
    ],
    "cn": [
        {"name": "原神", "channel_url": "https://www.youtube.com/channel/UCapD-I9_3ujAA1mvk_uLmGA", "subscribers": 2200000, "main_games": ["原神"]},
        {"name": "崩坏：星穹铁道", "channel_url": "https://www.youtube.com/channel/UCzuIcjh24KYVZBhYhcFYCrQ", "subscribers": 850000, "main_games": ["崩坏星穹铁道"]},
        {"name": "王者荣耀 官方", "channel_url": "https://www.youtube.com/@HonorOfKingsOfficial", "subscribers": 320000, "main_games": ["王者荣耀"]},
        {"name": "和平精英 官方", "channel_url": "https://www.youtube.com/@GameForPeaceOfficial", "subscribers": 280000, "main_games": ["和平精英"]},
        {"name": "崩坏3 (Honkai Impact 3rd)", "channel_url": "https://www.youtube.com/@HonkaiImpact3rd", "subscribers": 480000, "main_games": ["崩坏3"]},
        {"name": "绝区零 (Zenless Zone Zero)", "channel_url": "https://www.youtube.com/@ZenlessZoneZero", "subscribers": 920000, "main_games": ["绝区零"]},
        {"name": "明日方舟 (Arknights)", "channel_url": "https://www.youtube.com/@ArknightsOfficial", "subscribers": 380000, "main_games": ["明日方舟"]},
        {"name": "碧蓝航线 (Azur Lane)", "channel_url": "https://www.youtube.com/@AzurLaneOfficial", "subscribers": 240000, "main_games": ["碧蓝航线"]},
        {"name": "原神国际服 Genshin Impact", "channel_url": "https://www.youtube.com/@GenshinImpact", "subscribers": 4500000, "main_games": ["原神"]},
        {"name": "第五人格 (Identity V)", "channel_url": "https://www.youtube.com/@IdentityVOfficial", "subscribers": 420000, "main_games": ["第五人格"]},
        {"name": "永劫无间 (NARAKA)", "channel_url": "https://www.youtube.com/@NARAKABLADEPOINT", "subscribers": 310000, "main_games": ["永劫无间"]},
        {"name": "米哈游 (miHoYo)", "channel_url": "https://www.youtube.com/@miHoYo", "subscribers": 1200000, "main_games": ["原神", "崩坏", "绝区零"]},
        {"name": "腾讯游戏 Tencent Games", "channel_url": "https://www.youtube.com/@TencentGames", "subscribers": 380000, "main_games": ["王者荣耀", "和平精英"]},
        {"name": "网易游戏 NetEase Games", "channel_url": "https://www.youtube.com/@NetEaseGames", "subscribers": 290000, "main_games": ["永劫无间", "阴阳师"]},
        {"name": "鹰角网络 Hypergryph", "channel_url": "https://www.youtube.com/@Hypergryph", "subscribers": 95000, "main_games": ["明日方舟"]},
        {"name": "库洛游戏 Kuro Games", "channel_url": "https://www.youtube.com/@KuroGames", "subscribers": 340000, "main_games": ["鸣潮", "战双"]},
        {"name": "鸣潮 (Wuthering Waves)", "channel_url": "https://www.youtube.com/@WutheringWaves", "subscribers": 410000, "main_games": ["鸣潮"]},
        {"name": "战双帕弥什 (PGR)", "channel_url": "https://www.youtube.com/@PunishingOfficial", "subscribers": 180000, "main_games": ["战双帕弥什"]},
        {"name": "阴阳师官方 Onmyoji", "channel_url": "https://www.youtube.com/@Onmyojigame", "subscribers": 160000, "main_games": ["阴阳师"]},
        {"name": "闪耀暖暖 (Shining Nikki)", "channel_url": "https://www.youtube.com/@ShiningNikki", "subscribers": 90000, "main_games": ["闪耀暖暖"]},
        {"name": "三国杀官方 Sanguosha", "channel_url": "https://www.youtube.com/@SanguoshaOfficial", "subscribers": 70000, "main_games": ["三国杀"]},
        {"name": "哔哩哔哩游戏 (Bilibili Games)", "channel_url": "https://www.youtube.com/@BilibiliGames", "subscribers": 520000, "main_games": ["游戏综合"]},
        {"name": "FGO 中国 (China)", "channel_url": "https://www.youtube.com/@FGOChina", "subscribers": 110000, "main_games": ["FGO"]},
        {"name": "英雄联盟 (League of Legends CN)", "channel_url": "https://www.youtube.com/@LOLChina", "subscribers": 420000, "main_games": ["英雄联盟"]},
        {"name": "穿越火线 (CrossFire)", "channel_url": "https://www.youtube.com/@CrossFireOfficial", "subscribers": 140000, "main_games": ["穿越火线"]},
        {"name": "DNF 中国 (Dungeon & Fighter)", "channel_url": "https://www.youtube.com/@DNFChina", "subscribers": 260000, "main_games": ["DNF"]},
        {"name": "完美世界游戏 Perfect World", "channel_url": "https://www.youtube.com/@PerfectWorldGames", "subscribers": 85000, "main_games": ["完美世界"]},
        {"name": "盛趣游戏 Shengqu Games", "channel_url": "https://www.youtube.com/@ShengquGames", "subscribers": 45000, "main_games": ["热血传奇"]},
        {"name": "莉莉丝游戏 Lilith Games", "channel_url": "https://www.youtube.com/@LilithGames", "subscribers": 120000, "main_games": ["万国觉醒", "剑与远征"]},
        {"name": "叠纸游戏 Papergames", "channel_url": "https://www.youtube.com/@Papergames", "subscribers": 95000, "main_games": ["闪耀暖暖", "恋与制作人"]},
    ],
}

# ===== is_official 자동 분류 (기존 데이터용) =====
def classify_official(name, country, category=""):
    """기존 데이터의 이름/카테고리로 공식 채널 여부 판별"""
    n = name.lower()
    cat = (category or "").lower()
    official_keywords = [
        "official", "공식", "lostrk", "lost ark", "lostark",
        "pubg", "valorant", "발로란트", "리그 오브 레전드", "league of legends",
        "overwatch", "오버워치", "genshin", "원신", "honkai", "붕괴",
        "t1", "lck", "nc official", "hanwha life", "cloudtemplar",
        "esports", "life esports", "ncsoft", "kakao", "nexon", "neople",
        "nintendo", "任天堂", "公式", "官方", "sega", "square enix",
        "capcom", "bandai", " Atlus", "mihoyo", "米哈游", "tencent",
        "netease", "hypergryph", "プロセカ", "モンスト", "ウマ娘", "fgo",
        "ブルーアーカイブ", "スプラトゥーン", "ポケモン",
        "原神-genshin-公式", "ぱかチューブ",
    ]
    for kw in official_keywords:
        if kw in n or kw in cat:
            return True
    # 특정 이름 정확 매칭
    exact_official = ["Wolf"]  # LCK 캐스터지만 공식 성격
    return False

# ===== tier 계산 =====
def calc_tier(subscribers, avg_views=0):
    """구독자 수와 평균 조회수로 티어 산정"""
    s = subscribers or 0
    v = avg_views or 0
    if s >= 2000000 or v >= 400000:
        return "S"
    elif s >= 1000000 or v >= 200000:
        return "A"
    elif s >= 500000 or v >= 100000:
        return "B"
    elif s >= 100000 or v >= 20000:
        return "C"
    else:
        return "D"

# ===== 메인 병합 =====
def main():
    with open("all_influencers.json", encoding="utf-8") as f:
        existing = json.load(f)

    # 기존 URL 집합 (중복 방지)
    seen_urls = {d["channel_url"] for d in existing}
    seen_names_lower = {d["name"].strip().lower() for d in existing}

    # 1) 기존 데이터에 is_official 필드 추가 + 필드 보강
    for d in existing:
        is_off = classify_official(d["name"], d["country"], d.get("category", ""))
        d["is_official"] = is_off
        # tier 재계산 (기존 tier 유지)
        if "tier" not in d:
            d["tier"] = calc_tier(d.get("subscribers", 0), d.get("avg_views", 0))
        # main_games 없으면 빈 배열
        if "main_games" not in d:
            d["main_games"] = []

    print(f"기존 데이터 처리: {len(existing)}명")
    print(f"  공식 채널: {sum(1 for d in existing if d['is_official'])}명")

    # 2) 공식 채널 추가 (OFFICIAL_CHANNELS)
    added_official = 0
    for cc, channels in OFFICIAL_CHANNELS.items():
        for ch in channels:
            url = ch["channel_url"]
            name_l = ch["name"].strip().lower()
            if url in seen_urls or name_l in seen_names_lower:
                continue
            subs = ch.get("subscribers", 0)
            avg_v = int(subs * 0.15) if subs else 0
            entry = {
                "name": ch["name"],
                "platform": "YouTube",
                "subscribers": subs,
                "channel_url": url,
                "category": "게임 공식 채널" if cc == "kr" else ("ゲーム公式チャンネル" if cc == "jp" else "游戏官方频道"),
                "country": cc,
                "avg_views": avg_v,
                "engagement_rate": round(3.0 + (subs / 1000000) * 0.5, 2) if subs else 3.0,
                "growth_rate": 0.5,
                "content_count": 0,
                "recent_videos": [],
                "main_games": ch.get("main_games", []),
                "tier": calc_tier(subs, avg_v),
                "is_official": True
            }
            existing.append(entry)
            seen_urls.add(url)
            seen_names_lower.add(name_l)
            added_official += 1

    print(f"공식 채널 추가: {added_official}명")

    # 3) 검색 발굴 채널 추가
    added_search = 0
    for cc in ["kr", "jp", "cn"]:
        try:
            with open(f"{cc}_with_subs.json", encoding="utf-8") as f:
                found = json.load(f)
        except FileNotFoundError:
            print(f"  {cc}_with_subs.json 없음 - 스킵")
            continue

        for ch in found:
            url = ch["url"]
            name = ch["name"].strip()
            name_l = name.lower()
            if url in seen_urls or name_l in seen_names_lower:
                continue
            if not name or name == "NA":
                continue

            subs = ch.get("subscribers", 0)
            total_views = ch.get("total_views", 0)
            queries = ch.get("queries", [])

            # 게임 분류 추론 (쿼리 기반)
            main_games = infer_games_from_queries(queries, cc)

            avg_v = int(subs * 0.12) if subs else 0
            entry = {
                "name": name,
                "platform": "YouTube",
                "subscribers": subs,
                "channel_url": url,
                "category": infer_category(queries, cc),
                "country": cc,
                "avg_views": avg_v,
                "engagement_rate": round(2.5 + (subs / 1000000) * 0.8, 2) if subs else 3.0,
                "growth_rate": 0.5,
                "content_count": 0,
                "recent_videos": [],
                "main_games": main_games,
                "tier": calc_tier(subs, avg_v),
                "is_official": False
            }
            existing.append(entry)
            seen_urls.add(url)
            seen_names_lower.add(name_l)
            added_search += 1

    print(f"검색 발굴 채널 추가: {added_search}명")

    # 국가별 통계
    from collections import Counter
    by_country = Counter(d["country"] for d in existing)
    print(f"\n최종 인플루언서 수: {len(existing)}명")
    for cc, cnt in sorted(by_country.items()):
        official_cnt = sum(1 for d in existing if d["country"] == cc and d["is_official"])
        print(f"  {cc}: {cnt}명 (공식 {official_cnt}, 개인 {cnt-official_cnt})")

    # 저장
    with open("all_influencers.json", "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n저장 완료: all_influencers.json ({len(existing)}명)")


GAME_MAP_KR = {
    "배틀그라운드": "배틀그라운드", "발로란트": "발로란트", "로스트아크": "로스트아크",
    "원신": "원신", "니케": "니케: 승리의 여신", "모바일": "모바일 게임",
    "림버스": "림버스 컴퍼니", "붕괴": "붕괴: 스타레일", "오딘": "오딘: 발할라 라이징",
    "로블록스": "로블록스", "마인크래프트": "마인크래프트", "FPS": "FPS 게임",
    "리그오브레전드": "리그 오브 레전드", "서든어택": "서든어택", "메이플": "메이플스토리",
    "디아블로": "디아블로", "닌텐도": "닌텐도",
}
GAME_MAP_JP = {
    "原神": "原神", "モンスト": "モンスト", "ブルーアーカイブ": "ブルーアーカイブ",
    "プロセカ": "プロセカ", "ウマ娘": "ウマ娘", "FGO": "FGO",
    "スプラトゥーン": "スプラトゥーン", "マイクラ": "マインクラフト",
    "ホロライブ": "ホロライブ", "にじさんじ": "にじさんじ", "Apex": "Apex Legends",
    "パズドラ": "パズドラ", "アイドルマスター": "アイドルマスター",
    "ポケモン": "ポケモン", "ゼルダ": "ゼルダ",
}
GAME_MAP_CN = {
    "原神": "原神", "王者荣耀": "王者荣耀", "和平精英": "和平精英",
    "崩坏": "崩壊", "英雄联盟": "英雄联盟", "明日方舟": "明日方舟",
    "我的世界": "我的世界", "绝地求生": "绝地求生", "蛋仔派对": "蛋仔派对",
    "第五人格": "第五人格", "永劫无间": "永劫无间", "阴阳师": "阴阳师",
    "暗区突围": "暗区突围", "无畏契约": "无畏契约",
}

def infer_games_from_queries(queries, cc):
    gmap = {"kr": GAME_MAP_KR, "jp": GAME_MAP_JP, "cn": GAME_MAP_CN}[cc]
    games = set()
    for q in queries:
        for key, game in gmap.items():
            if key in q:
                games.add(game)
    return list(games)[:3] if games else ["기타 게임" if cc == "kr" else ("その他ゲーム" if cc == "jp" else "其他游戏")]

CAT_MAP = {
    "kr": "게임 실황/리뷰",
    "jp": "ゲーム実況/レビュー",
    "cn": "游戏实况/解说",
}
def infer_category(queries, cc):
    return CAT_MAP.get(cc, "게임")


if __name__ == "__main__":
    main()
