# Game Market Insight v2.4

3개국(한국/중국/일본) 모바일 게임 시장 통합 대시보드

🔗 **한국어**: https://jycho7254-commits.github.io/game-dashboard-v2/  
🔗 **중국어**: https://jycho7254-commits.github.io/game-dashboard-v2/cn/

## 📊 탭 구성

| 탭 | 내용 | 데이터 소스 |
|----|------|------------|
| **종합** | 3개국 매출 Top10 (그라데이션 차트) + 시장 인사이트 + 각국 TOP10 트렌드 분석 | GP/iOS 랭킹 + 여론 + 영상 데이터 |
| **매출 순위** | 국가별 Top50 매출 추정 순위 (10개 표시 + 더보기/접기) | Google Play Scraper (KR/JP), Qimai iOS (CN) |
| **여론 분석** | 게임별 여론 지수 + 긍정/부정 % (DC/GP/YT/Bilibili/Twitter/5ch) | DC Inside, Google Play, YouTube, Bilibili, TapTap, Twitter, 5ch |
| **인플루언서** | 465명 KOL 랭킹 + 최근 영상 5개 + 실시간 방송 (치지직 + YouTube Live) | SESI (KR), Cloudtrons (JP), Bilibili (CN), 치지직 API, YouTube 검색 |
| **게임사 매출분석** | 131개사 전사 재무 (3년) + 영업이익률 차트 | DART, EDINET, CSRC, HKEX, SEC, Sensor Tower |
| **뉴스** | 최근 7일 게임 뉴스 (3개국) | DC Inside, Bilibili, X/Twitter |
| **캘린더** | 월별 게임 이벤트 캘린더 (101개 이벤트) | 수동 + 월별 갱신 |

## 🎨 UI 특징

- **중앙 타이틀**: "Game Market Insight" + 7개 대형 탭
- **다크/라이트 모드**: 게임 배경 이미지 (92% 투명도 오버레이)
- **그라데이션 차트**: Chart.js createLinearGradient (상단 95% → 하단 60%)
- **10개 페이징**: 매출순위/여론/인플루언서 — 10개만 표시 + 더보기/접기 버튼
- **실시간 랭킹 접기**: 치지직(좌) / YouTube Live(우) 분리 + 펼치기/접기
- **업데이트 버튼**: 게임 모달에서 Google Play 최근 업데이트 토글
- **반응형**: 480px / 768px / 1024px 분기 (모바일 세로 배치)
- **폰트**: 최소 11px (Pretendard), AdSense 대응 단색 배경 옵션

## 🏗️ 아키텍처

```
[데이터 수집]                    [데이터 저장]              [배포]
                    ┌───────────────────────────────────────────────────────┐
                    │                                                       │
live_update.py      │  softc_data.json (치지직 + YouTube Live)             │  GitHub Pages
(10분 크론)  ──────▶│  kr/cn/jp_rankings.json (매출순위)                    │  index.html (인라인)
                    │  kr_sentiment_full.json (여론 87개)                   │  data/softc_data.json (fetch용)
daily_update_p1.py  │  all_influencers.json (465명 + recent_videos)        │
(11시/17시 크론)───▶│  game_company_financials.json (131개사)               │  cn/index.html (중국어)
                    │  GAME_UPDATES (Google Play 실제 업데이트 46개)        │
                    └───────────────────────────────────────────────────────┘
```

### 새로고침 구조 (부하 없음)

```
브라우저 새로고침
  → fetch GitHub Pages/data/softc_data.json (0.1초)
  → 외부 API 호출 0개 → PC 부하 0
  → 5초 쿨다운 (연속 클릭 차단)
```

### YouTube Live 안정화

```
collect_yt_live.py (YouTube 검색 기반)
  → 10개 키워드 검색 (게임/롤/발로란트/오버워치/배그/마인크래프트/서든/로아/FC온/스타)
  → "명 시청 중" 패턴으로 라이브 감지
  → oEmbed로 채널명 보정
  → 실패 시 기존 YouTube 데이터 유지 (softc_data.json에서 복원)
```

## 📈 데이터 규모

| 항목 | 수량 |
|------|------|
| 매출순위 | 한국 50 / 중국 50 / 일본 50 |
| 여론 분석 | 한국 87 / 중국 125 / 일본 131 |
| 인플루언서 | 한국 209 / 일본 183 / 중국 74 (총 465명) |
| recent_videos | 2,042개 (한국 931 / 일본 855 / 중국 256) |
| 게임사 재무 | 131개사 (한국 33 / 중국 48 / 일본 39 / 기타 11) |
| 뉴스 | 한국 50 / 중국 25 / 일본 10 |
| 캘린더 이벤트 | 101개 |
| DC 갤러리 매핑 | 163개 |
| 게임 업데이트 | 46개 (Google Play 실제 데이터) |
| 실시간 방송 | 치지직 30명 + YouTube Live ~20개 |

## 🔄 크론 구성

| 크론 | 주기 | 내용 |
|------|------|------|
| `live_update.py` | 10분 | 치지직 실시간 + YouTube Live + 매출순위 로테이션 + 배포 |
| `daily_update_p1.py` | 11시/17시 | 매출순위 + DC 여론 + local_name 보정 + 한국 여론 보정 + 빌드 |
| `collect_cn_rankings.py` | 일 1회 | 중국 iOS 순위 (Qimai) + 매출 추정 자동 계산 |

## 🛠️ 기술 스택

- **프론트엔드**: HTML/CSS/JS (인라인 빌드, Chart.js via CDN)
- **데이터 수집**: Python (urllib), Node.js (google-play-scraper)
- **배포**: GitHub Pages (정적 사이트)
- **빌드**: `build_dashboard.py` — 템플릿 플레이스홀더 치환 방식
- **크론**: Hermes Agent no_agent 스크립트
- **Python**: `C:\Users\user\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe`

## 📁 폴더 구조

```
game_dashboard_v2/
├── templates/index.html          # 메인 템플릿 (수정 위치)
├── data/                         # JSON 데이터
│   ├── softc_data.json           # 실시간 방송 (치지직 + YouTube Live)
│   ├── kr_rankings.json          # 한국 매출순위 50
│   ├── cn_rankings.json          # 중국 매출순위 50
│   ├── jp_rankings.json          # 일본 매출순위 50
│   ├── all_influencers.json      # 465명 KOL + recent_videos
│   ├── kr_sentiment_full.json    # 한국 여론 87개
│   ├── game_company_financials.json  # 131개사 재무
│   └── bg_gameshow.jpg           # 배경 이미지
├── scripts/                      # 수집 스크립트
│   ├── collect_cn_rankings.py    # 중국 순위 + 매출 자동 계산
│   ├── collect_yt_live.py        # YouTube Live 검색 수집
│   ├── reestimate_v3.py          # 매출 추정
│   ├── fix_local_names.py        # 게임명 자동 보정
│   └── fix_kr_sentiment_safe.py  # 한국 여론 누락 보정
├── build_dashboard.py            # 빌드 스크립트
└── README.md

game-dashboard-v2/                 # 배포 폴더 (GitHub Pages)
├── index.html                    # 한국어 빌드 (인라인)
├── cn/index.html                 # 중국어 빌드
└── data/softc_data.json          # fetch용 JSON

~/AppData/Local/hermes/scripts/   # 크론 스크립트
├── live_update.py                # 10분 크론
├── daily_update_p1.py            # 일 2회 크론
├── collect_chzzk.py              # 치지직 데이터 수집
└── collect_yt_live.py            # YouTube Live 수집
```

## 🎯 핵심 설계 원칙

1. **브라우저 외부 API 호출 금지** — 전부 GitHub Pages JSON fetch
2. **빌드는 JSON 수정 금지** — 템플릿 플레이스홀더 치환만
3. **Python 경로 명시** — `python3` 대신 uv 절대경로 사용
4. **YouTube 실패 시 기존 데이터 유지** — 빈 리스트로 덮어쓰기 방지
5. **OMP 검증 의수** — CN 매출 50/50, SOOP 0, tunnel 0, 젠티스 0, JS OK

---
Updated: 2026-08-05
