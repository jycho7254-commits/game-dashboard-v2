# Game Dashboard v2.1

3개국(한국/중국/일본) 모바일 게임 시장 통합 대시보드

🔗 **한국어**: https://jycho7254-commits.github.io/game-dashboard-v2/  
🔗 **중국어**: https://jycho7254-commits.github.io/game-dashboard-v2/cn/

## 📊 탭 구성

| 탭 | 내용 | 데이터 소스 |
|----|------|------------|
| **종합** | 3개국 매출 Top10 + 시장 분석 요약 + 각국 TOP10 동향 | GP/iOS 랭킹 + 여론 + 영상 데이터 |
| **매출 순위** | 국가별 Top50 매출 추정 순위 (3개국 통합 뷰) | Google Play Scraper (KR/JP), iOS (CN) |
| **여론 분석** | 게임별 여론 지수 + 긍정/부정 % (DC/GP/YT/Bilibili/Twitter/5ch) | DC Inside, Google Play, YouTube, Bilibili, TapTap, Twitter, 5ch |
| **인플루언서** | 466명 KOL 랭킹 + 채널 정보 + 최근 영상 5개 + 실시간 방송 | SESI (KR), Cloudtrons (JP), Bilibili (CN), 치지직 API, YouTube Live |
| **게임사 매출분석** | 113개사 전사 재무 (3년) + 영업이익률 차트 | DART, EDINET, CSRC, HKEX, SEC |
| **뉴스** | 최근 7일 게임 뉴스 (3개국) | DC Inside, Bilibili, X/Twitter |
| **캘린더** | 월별 게임 이벤트 캘린더 (101개 이벤트 / 42일) | 수동 + 월별 갱신 |

## 🏗️ 아키텍처

```
game_dashboard_v2/
├── templates/
│   └── index.html              # 메인 템플릿 (HTML+CSS+JS 인라인)
├── data/                       # JSON 데이터
│   ├── kr_rankings.json        # 한국 매출순위 Top50
│   ├── cn_rankings.json        # 중국 매출순위 Top50
│   ├── jp_rankings.json        # 일본 매출순위 Top50
│   ├── kr_sentiment_full.json  # 한국 여론 (87개)
│   ├── cn_sentiment_full.json  # 중국 여론 (280개)
│   ├── jp_sentiment_full.json  # 일본 여론 (282개)
│   ├── all_influencers.json    # 인플루언서 466명 + recent_videos
│   ├── all_calendar.json       # 캘린더 이벤트 (101개)
│   ├── game_company_financials.json  # 113개사 재무
│   ├── softc_data.json         # 실시간 방송 현황 (치지직+YouTube Live)
│   ├── dc_gal_map.json         # DC 갤러리 ID 매핑 (163개)
│   ├── arca_slug_map.json      # 아카라이브 슬러그 매핑 (63개)
│   ├── game_i18n.json          # 게임명 다국어 매핑
│   ├── yt_full_data.json       # YouTube 영상 데이터
│   ├── kr_news.json            # 한국 뉴스
│   ├── cn_news.json            # 중국 뉴스
│   └── jp_news.json            # 일본 뉴스
├── scripts/                    # 데이터 수집 스크립트
│   ├── collect_kr_sentiment_full.py   # 한국 여론 수집
│   ├── collect_cn_rankings.py         # 중국 매출순위 수집
│   ├── collect_yt_full.py             # YouTube 영상 수집
│   ├── reestimate_v3.py              # 매출 추정 (로그-로그 2차 곡선)
│   ├── fix_local_names.py            # 게임명 자동 보정
│   ├── fix_kr_sentiment_safe.py      # 한국 여론 누락 자동 보정
│   └── chzzk_proxy.py                # 치지직 CORS 프록시
├── build_dashboard.py          # 빌드 스크립트 (JSON→인라인 HTML)
└── data/bg_gameshow.jpg        # 배경 이미지
```

### 빌드 파이프라인
```
data/*.json → build_dashboard.py → 인라인 HTML → GitHub Pages 배포
```

- `build_dashboard.py`가 `templates/index.html`의 `__xxx_DATA__` 플레이스홀더를 JSON으로 치환
- 모든 데이터를 HTML 안에 인라인 (외부 JSON fetch 없음 → 빠른 로딩)
- `softc_data.json`만 GitHub Pages에 별도 파일로 두어 새로고침 시 fetch
- 빌드 결과: `game-dashboard-v2/index.html` (~1.5MB)

## ⏱️ 데이터 갱신 체계

### 자동 갱신 (크론)

| 크론 | 스케줄 | 갱신 내용 |
|------|--------|----------|
| **live_update.py** | **10분마다** | 치지직 실시간 + YouTube Live 수집 + 매출순위 로테이션 (KR→CN→JP) + 빌드/배포 |
| **daily_update_p1.py** | 11:00, 17:00 | 매출순위 전체 + DC 여론 + GP 평점 + local_name 보정 + 한국 여론 자동 보정 + 빌드 |
| **daily_update_p2.py** | 11:20, 17:20 | Bilibili 영상 + 뉴스 + CDN 배포 |

### 새로고침 아키텍처
```
브라우저 새로고침 버튼
  → GitHub Pages/softc_data.json fetch (0.1초)
  → 외부 API 호출 없음 → PC 부하 없음
  → 5초 쿨다운 (연속 클릭 차단)
```

### 매출순위 로테이션 (10분 크론)
```
00-09분 → 한국 (KR)    Google Play Scraper
10-19분 → 중국 (CN)    iOS Rankings
20-29분 → 일본 (JP)    Google Play Scraper
30-39분 → 한국 (KR)    ...
→ 각국 20분마다 갱신
```

### 수동 갱신 필요

| 데이터 | 권장 주기 | 비고 |
|--------|----------|------|
| 인플루언서 recent_videos | 주 1회 | YouTube RSS에서 5개 영상 수집 |
| 캘린더 이벤트 | 월 1회 | 월별 게임 이벤트 추가 |
| 게임사 재무 | 분기 1회 | 공시 발표 후 업데이트 |

## 🌐 중국어 버전

- URL: `/cn/` 경로
- 빌드: 한국어 빌드 파일을 베이스로 UI 텍스트 중국어 치환 (100+개)
- 게임명/뉴스 제목은 원문 유지

## 🔧 외부 연동

### 치지직 실시간 API
- 공개 API: `api.chzzk.naver.com/service/v1/search/lives`
- 10개 카테고리 수집 → streamers 데이터 생성
- CORS: GitHub Pages에서 직접 호출 불가 → 크론에서 수집 후 JSON 배포

### YouTube Live
- 게임 키워드 검색 (12개 키워드) → `"명 시청 중"` 패턴으로 라이브 감지
- oEmbed로 채널명 자동 보정
- 비게임 채널 자동 필터링 (런닝맨/SBS 등)

### Google Play Scraper
- 한국/일본 매출순위 (GROSSING 카테고리 Top50)
- 경로: `C:\Users\user\node_modules\google-play-scraper`

### DC Inside 갤러리 매핑
- `dc_gal_map.json`: 게임명 → 갤러리 ID (163개)
- 마이너/미니/메인 갤러리 자동 경로 분류
- 없는 게임: DC 통합검색으로 fallback

## 📈 기술 스택

- **Frontend**: HTML/CSS/JS (vanilla, 프레임워크 없음)
- **Charts**: Chart.js (CDN)
- **데이터 수집**: Python (urllib, openpyxl), Node.js (google-play-scraper)
- **배포**: GitHub Pages (자동 push)
- **크론**: Hermes Agent 크론 시스템
- **MCP**: Z.AI Vision MCP Server (이미지/비디오 분석)

## 📁 파일 위치

| 항목 | 경로 |
|------|------|
| 개발 폴더 | `C:\Users\user\Desktop\game_dashboard_v2\` |
| 배포 폴더 | `C:\Users\user\game-dashboard-v2\` (git repo) |
| 크론 스크립트 | `~/AppData/Local/hermes/scripts/` |
| GitHub repo | `jycho7254-commits/game-dashboard-v2` |

## 📊 데이터 규모

| 항목 | 수량 |
|------|------|
| 추정 매출 게임 | 150개 (3개국 × 50) |
| 여론 분석 게임 | 649개 (KR 87 + CN 280 + JP 282) |
| 인플루언서 | 466명 (KR 209 + JP 183 + CN 74) |
| recent_videos | 2,042개 (KR 931 + JP 855 + CN 256) |
| 게임사 재무 | 113개사 |
| 캘린더 이벤트 | 101개 / 42일 |
| DC 갤러리 매핑 | 163개 |
| 실시간 방송 | 치지직 30명 + YouTube Live 11개 |

---

© 2026 Game Dashboard v2.1 | KR·CN·JP 통합 게임 시장 분석
