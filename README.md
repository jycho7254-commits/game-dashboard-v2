# Game Dashboard v2

3개국(한국/중국/일본) 모바일 게임 시장 통합 대시보드  
🔗 **URL**: https://jycho7254-commits.github.io/game-dashboard-v2/

## 📊 탭 구성

| 탭 | 내용 | 데이터 소스 |
|----|------|------------|
| **종합** | 3개국 매출 Top10 + 시장 분석 요약 + 트렌드 점수 | GP/iOS 랭킹 + 여론 + 영상 데이터 |
| **매출 순위** | 국가별 Top50 매출 추정 순위 | Google Play Scraper (KR/JP), iOS (CN) |
| **여론 분석** | 게임별 여론 지수 + 긍정/부정 % | DC Inside, Google Play, YouTube, Bilibili, TapTap |
| **인플루언서** | 465명 KOL 랭킹 + 채널 정보 + 최근 영상 5개 | SESI (KR), Cloudtrons (JP), Bilibili (CN) |
| **게임사 매출분석** | 113개사 전사 재무 (3년) | DART, EDINET, CSRC, HKEX, SEC |
| **뉴스** | 최근 7일 게임 뉴스 | DC Inside, Bilibili, X/Twitter |
| **캘린더** | 월별 게임 이벤트 캘린더 | 수동 + 월별 갱신 |

## 🏗️ 아키텍처

```
game_dashboard_v2/
├── templates/
│   └── index.html          # 메인 템플릿 (HTML+CSS+JS 인라인)
├── data/                   # JSON 데이터
│   ├── kr_rankings.json    # 한국 매출순위 Top50
│   ├── cn_rankings.json    # 중국 매출순위 Top50
│   ├── jp_rankings.json    # 일본 매출순위 Top50
│   ├── kr_sentiment_full.json  # 한국 여론 (74개)
│   ├── cn_sentiment_full.json  # 중국 여론 (279개)
│   ├── jp_sentiment_full.json  # 일본 여론 (282개)
│   ├── all_influencers.json    # 인플루언서 465명
│   ├── all_calendar.json       # 캘린더 이벤트
│   ├── game_company_financials.json  # 113개사 재무
│   ├── softc_data.json         # 실시간 방송 현황
│   ├── dc_gal_map.json         # DC 갤러리 ID 매핑
│   ├── arca_slug_map.json      # 아카라이브 슬러그 매핑
│   ├── game_i18n.json          # 게임명 다국어 매핑
│   └── yt_full_data.json       # YouTube 영상 데이터
├── scripts/                # 데이터 수집 스크립트
│   ├── collect_cn_rankings.py
│   ├── collect_dc_mobile.py
│   ├── collect_kr_sentiment_full.py
│   ├── reestimate_v3.py    # 매출 추정 (로그-로그 2차 곡선)
│   ├── fix_local_names.py  # 게임명 자동 보정
│   └── chzzk_proxy.py      # 치지직 CORS 프록시
├── build_dashboard.py      # 빌드 스크립트 (JSON→인라인 HTML)
└── data/bg_gameshow.jpg    # 배경 이미지 (52KB)
```

### 빌드 파이프라인
```
data/*.json → build_dashboard.py → 인라인 HTML → GitHub Pages 배포
```

- `build_dashboard.py`가 `templates/index.html`의 `__DATA__` 플레이스홀더를 JSON으로 치환
- 모든 데이터를 HTML 안에 인라인 (외부 JSON fetch 불필요 → 빠른 로딩)
- 빌드 결과: `game-dashboard-v2/index.html` (~1.5MB)

## ⏱️ 데이터 갱신 체계

### 자동 갱신 (크론)

| 크론 | 스케줄 | 갱신 내용 |
|------|--------|----------|
| **live_update.py** | **10분마다** | 치지직 실시간 + 매출순위 (30분 로테이션: KR→CN→JP) + 빌드/배포 |
| **daily_update_p1.py** | 11:00, 17:00 | 매출순위 전체 + DC 여론 + 소프트콘 + local_name 보정 + 빌드 |
| **daily_update_p2.py** | 11:20, 17:20 | Bilibili 영상 + 뉴스 + CDN 배포 |

### 매출순위 갱신 로테이션 (10분 크론)

```
시간별 실행국가 (10분 주기 로테이션):
00-09분 → 한국 (KR)
10-19분 → 중국 (CN)  
20-29분 → 일본 (JP)
30-39분 → 한국 (KR)
40-49분 → 중국 (CN)
50-59분 → 일본 (JP)
→ 각국 20분마다 갱신
```

### 수동 갱신 필요

| 데이터 | 권장 주기 | 비고 |
|--------|----------|------|
| 인플루언서 recent_videos | 주 1회 | YouTube RSS에서 5개 영상 수집 |
| 캘린더 이벤트 | 월 1회 | 월별 게임 이벤트 추가 |
| 게임사 재무 | 분기 1회 | 공시 발표 후 업데이트 |
| 한국 여론 (신규 게임) | 순위 변경 시 | 랭킹 진입 게임 자동 여론 추가 |

## 🌐 중국어 버전

- URL: `/cn/` 경로
- 빌드: 한국어 빌드 파일을 베이스로 UI 텍스트 중국어 치환 (682개)
- 게임명/뉴스 제목은 원문 유지 (GAME_I18N 매핑으로 처리)

## 🔧 외부 연동

### 치지직 실시간 API
- 직접 호출: CORS 차단 (github.io → chzzk API)
- 해결: Cloudflare tunnel 프록시 (형 PC 켜져 있을 때) + 캐시 fallback

### Google Play Scraper
- 한국/일본 매출순위 (GROSSING 카테고리 Top50)
- 경로: `C:\Users\user\node_modules\google-play-scraper`

### DC Inside 갤러리 매핑
- `dc_gal_map.json`: 게임명 → 갤러리 ID
- 마이너/미니/메인 갤러리 자동 경로 분류
- 없는 게임: DC 통합검색으로 fallback

## 📈 기술 스택

- **Frontend**: HTML/CSS/JS (vanilla, 프레임워크 없음)
- **Charts**: Chart.js (CDN)
- **데이터 수집**: Python (urllib, openpyxl), Node.js (google-play-scraper)
- **배포**: GitHub Pages (자동 push)
- **크론**: Hermes Agent 크론 시스템

## 📁 파일 위치

| 항목 | 경로 |
|------|------|
| 개발 폴더 | `C:\Users\user\Desktop\game_dashboard_v2\` |
| 배포 폴더 | `C:\Users\user\game-dashboard-v2\` (git repo) |
| 크론 스크립트 | `~/AppData/Local/hermes/scripts/` |
| 백업 | `C:\Users\user\Desktop\game_dashboard_v2_backup_0727\` |

---

© 2026 Game Dashboard v2.1 | KR·CN·JP 통합 게임 시장 분석
