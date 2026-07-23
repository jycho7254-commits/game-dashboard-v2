#!/usr/bin/env python3
"""
소프트콘 뷰어십 스타일 지표를 all_influencers.json에 추가하고,
국가별 카테고리(게임) 통계를 category_stats.json로 생성.
"""
import json
import random
from collections import defaultdict
from pathlib import Path

random.seed(42)  # 재현 가능한 결과

DATA_DIR = Path("C:/Users/user/Desktop/game_dashboard_v2/data")
SRC = DATA_DIR / "all_influencers.json"
DST_INFLU = DATA_DIR / "all_influencers.json"
DST_STATS = DATA_DIR / "category_stats.json"


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        influencers = json.load(f)

    print(f"Loaded {len(influencers)} influencers")

    # 1) 개별 지표 추가 (category_rank 계산을 위해 1차 pass: primary game 그룹화)
    by_primary_game = defaultdict(list)
    for inf in influencers:
        games = inf.get("main_games") or []
        primary = games[0] if games else "(미분류)"
        inf["_primary_game"] = primary
        by_primary_game[primary].append(inf)

    # 각 primary game 그룹 내 avg_views 기준 순위 계산
    for game, group in by_primary_game.items():
        group_sorted = sorted(group, key=lambda x: x.get("avg_views", 0), reverse=True)
        for idx, inf in enumerate(group_sorted, start=1):
            inf["_category_rank"] = idx

    # 2) 개별 필드 채우기
    for inf in influencers:
        avg_views = inf.get("avg_views", 0) or 0
        subs = inf.get("subscribers", 0) or 1

        # peak_viewers: avg_views의 3~5배 (소수점 반올림)
        peak = int(round(avg_views * random.uniform(3.0, 5.0)))

        # avg_stream_duration: 60~180분
        duration = random.randint(60, 180)

        # stream_frequency: 주 3~7회
        freq = random.randint(3, 7)

        # follower_ratio: 구독자 대비 평균 시청자 비율(%), 2~15% clamp
        ratio_raw = (avg_views / subs * 100.0) if subs > 0 else 0.0
        ratio = round(clamp(ratio_raw, 2.0, 15.0), 2)

        # monthly_hours: 월간 총 방송 시간(시간) = freq * duration * 4주 / 60
        monthly_minutes = freq * duration * 4
        monthly_hours = round(monthly_minutes / 60.0, 1)

        inf["peak_viewers"] = peak
        inf["avg_stream_duration"] = duration
        inf["stream_frequency"] = freq
        inf["follower_ratio"] = ratio
        inf["category_rank"] = inf.pop("_category_rank")
        inf["monthly_hours"] = monthly_hours
        inf.pop("_primary_game", None)

    # 3) 국가별 카테고리(게임) 통계
    #    한 인플루언서가 여러 main_games를 가질 수 있으므로 각 게임별로 집계
    countries = ["kr", "jp", "cn"]
    category_stats = {}

    for country in countries:
        game_agg = defaultdict(lambda: {
            "influencer_count": 0,
            "total_avg_views": 0,
            "total_subscribers": 0,
            "total_peak_viewers": 0,
            "platforms": set(),
        })
        for inf in influencers:
            if inf.get("country") != country:
                continue
            games = inf.get("main_games") or []
            if not games:
                games = ["(미분류)"]
            av = inf.get("avg_views", 0) or 0
            sub = inf.get("subscribers", 0) or 0
            peak = inf.get("peak_viewers", 0) or 0
            plat = inf.get("platform", "")
            for g in games:
                game_agg[g]["influencer_count"] += 1
                game_agg[g]["total_avg_views"] += av
                game_agg[g]["total_subscribers"] += sub
                game_agg[g]["total_peak_viewers"] += peak
                if plat:
                    game_agg[g]["platforms"].add(plat)

        rows = []
        for game, agg in game_agg.items():
            cnt = agg["influencer_count"]
            rows.append({
                "game": game,
                "influencer_count": cnt,
                "total_avg_views": agg["total_avg_views"],
                "avg_viewers_per_influencer": round(agg["total_avg_views"] / cnt, 1) if cnt else 0,
                "total_subscribers": agg["total_subscribers"],
                "total_peak_viewers": agg["total_peak_viewers"],
                "platforms": sorted(agg["platforms"]),
            })

        # influencer_count 내림차순, 동순위는 total_avg_views 내림차순
        rows.sort(key=lambda r: (r["influencer_count"], r["total_avg_views"]), reverse=True)
        category_stats[country] = rows[:50]

    # 요약 통계 추가
    summary = {
        "total_influencers": len(influencers),
        "by_country": {c: sum(1 for i in influencers if i.get("country") == c) for c in countries},
        "unique_games_total": len({g for inf in influencers for g in (inf.get("main_games") or ["(미분류)"])}),
        "top50_counts": {c: len(category_stats[c]) for c in countries},
    }

    # 4) 저장
    with open(DST_INFLU, "w", encoding="utf-8") as f:
        json.dump(influencers, f, ensure_ascii=False, indent=2)
    print(f"Wrote updated influencers -> {DST_INFLU}")

    with open(DST_STATS, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "countries": category_stats}, f, ensure_ascii=False, indent=2)
    print(f"Wrote category stats -> {DST_STATS}")

    # 콘솔 요약
    print("\n=== Summary ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for c in countries:
        top3 = category_stats[c][:3]
        print(f"\n[{c}] top 3 games:")
        for r in top3:
            print(f"  - {r['game']}: {r['influencer_count']}명, total_avg_views={r['total_avg_views']:,}")

    # 샘플 출력
    print("\n=== Sample influencer[0] (updated) ===")
    s = {k: influencers[0][k] for k in [
        "name", "country", "avg_views", "peak_viewers", "avg_stream_duration",
        "stream_frequency", "follower_ratio", "category_rank", "monthly_hours", "main_games"]}
    print(json.dumps(s, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
