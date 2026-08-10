# 대시보드 아키텍처 v3.1

## 시스템 구성도

```
┌─────────────────────────────────────────────────┐
│                  사용자 브라우저                    │
│  https://gameinsight.pages.dev (Cloudflare CDN)  │
├─────────────────────────────────────────────────┤
│  Frontend (인라인 HTML + Chart.js)               │
│  ├─ 7개 탭 (종합/매출/여론/인플루언서/게임사/뉴스/캘린더) │
│  ├─ 호버 드롭다운 서브메뉴 (KR/CN/JP)              │
│  ├─ 회원가입/로그인 (Supabase Auth)               │
│  ├─ 여론 리포트 신청 (Supabase Storage)           │
│  └─ 다크/라이트 모드                               │
├─────────────────────────────────────────────────┤
│  Supabase Backend                                │
│  ├─ Auth (이메일 회원가입/로그인)                   │
│  ├─ Storage (report-templates bucket)            │
│  └─ PostgreSQL (report_subscriptions 테이블)      │
├─────────────────────────────────────────────────┤
│  데이터 수집 (Hermes 크론)                         │
│  ├─ 10분: live_update.py (치지직+YT Live)        │
│  ├─ 일(11시/17시): daily_update_p1.py            │
│  └─ 수동: reestimate_revenue.py (매출 추정)       │
├─────────────────────────────────────────────────┤
│  데이터 소스                                       │
│  ├─ Google Play API (한국/일본 매출)               │
│  ├─ Qimai (중국 iOS 매출)                        │
│  ├─ 치지직 API (실시간 방송)                      │
│  ├─ YouTube 검색 (Live + 영상)                   │
│  ├─ DC Inside / 아카라이브 (여론)                 │
│  ├─ 게임메카/인벤/루리웹/데일리게임/게임동아 (뉴스) │
│  ├─ wame.is (신작 런칭 캘린더)                    │
│  ├─ DART/CSRC/HKEX/EDINET (게임사 공시)           │
│  └─ Sensor Tower (비상장사 추정)                  │
├─────────────────────────────────────────────────┤
│  배포                                             │
│  ├─ Cloudflare Pages (메인, no-cache, 무료)       │
│  ├─ GitHub Pages (개발/백업)                      │
│  └─ Netlify (폐기)                               │
└─────────────────────────────────────────────────┘
```

## 파일 구조
```
C:\Users\user\Desktop\game_dashboard_v2\     ← 개발
├── templates/index.html                      ← 메인 템플릿 (모든 UI/JS)
├── build_dashboard.py                        ← 빌드 스크립트
├── scripts/
│   ├── live_update.py                        ← 10분 크론
│   ├── daily_update_p1.py                    ← 일 크론
│   ├── collect_yt_live.py                    ← YouTube Live 수집
│   ├── collect_cn_rankings.py                ← 중국 순위 + 매출표 내장
│   ├── collect_kr_sentiment_full.py          ← 한국 여론 수집
│   ├── reestimate_revenue.py                 ← 3개국 매출 추정
│   └── scrape_kr_news.py                     ← 다중 소스 뉴스 스크랩
├── data/
│   ├── kr_rankings.json                      ← 한국 매출 50개
│   ├── cn_rankings.json                      ← 중국 매출 50개
│   ├── jp_rankings.json                      ← 일본 매출 50개
│   ├── all_influencers.json                  ← 464명 인플루언서
│   ├── kr_sentiment_full.json                ← 한국 여론 87개
│   ├── game_company_financials.json          ← 131개사 재무
│   ├── kr_news.json                          ← 한국 뉴스 149개
│   ├── softc_data.json                       ← 실시간 방송
│   ├── all_calendar.json                     ← 캘린더 177개
│   └── gp_updates.json                       ← GP 업데이트
└── README.md / ARCHITECTURE.md

C:\Users\user\game-dashboard-v2\             ← 배포
├── index.html                                ← 빌드된 인라인 HTML
├── privacy.html / about.html / admin.html
├── data/ (JSON 파일들)
├── netlify.toml (폐기)
└── README.md
```

## 캐시 정책
| 파일 | 캐시 |
|------|------|
| Cloudflare 전체 | **no-cache** (즉시 갱신) |
| GitHub Pages | ~10분 |
| softc_data.json | no-cache (실시간) |
