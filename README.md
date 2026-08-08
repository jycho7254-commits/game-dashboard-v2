# Game Market Insight v3.0

3개국(한국/중국/일본) 모바일 게임 시장 통합 대시보드

## URL
- **Cloudflare (메인)**: https://gameinsight.pages.dev
- **GitHub Pages (개발)**: https://jycho7254-commits.github.io/game-dashboard-v2/
- **운영툴**: https://gameinsight.pages.dev/admin.html

## 아키텍처
```
[데이터 수집]
  ├─ live_update.py (10분 크론) — 치지직 + YouTube Live + softc_data.json
  ├─ daily_update_p1.py (11시/17시) — 매출 + 여론 + 뉴스 + 빌드
  └─ build_dashboard.py — 인라인 HTML 빌드

[배포]
  ├─ Cloudflare Pages (gameinsight.pages.dev) — 메인, no-cache, 무료 무제한
  ├─ GitHub Pages — 개발/백업
  └─ Netlify — 폐기 (크레딧 소모)

[백엔드]
  └─ Supabase — Auth (회원가입/로그인) + Storage (첨부파일) + DB (구독 관리)
```

## 데이터 규모
| 항목 | 수량 |
|------|------|
| 한국 매출 순위 | 50개 (Google Play) |
| 중국 매출 순위 | 50개 (iOS Qimai) |
| 일본 매출 순위 | 50개 (Google Play) |
| 게임사 재무 | 131개사 (한국/중국/일본/미국) |
| 인플루언서 | 464명 (KR 207 / JP 183 / CN 74) |
| 한국 여론 | 87개 게임 |
| 중국 여론 | 280개 게임 |
| 일본 여론 | 282개 게임 |
| 한국 뉴스 | 149개 (5개 소스) |
| 캘린더 | 177개 이벤트 |
| 실시간 방송 | 치지직 30 + YouTube Live |

## 탭 구조
1. **종합** — KPI + 매출 Top10 차트 + 시장 점유율 + 트렌드 아이콘 그리드 + 팝업
2. **매출 순위** — 국가별 Top50 + 국가별 차트 (한/중/일 분리) + 매출 추정 팝업
3. **여론 분석** — 게임별 여론 지수 + 여론 지수 기준 팝업 + 여론 리포트 신청
4. **인플루언서** — 464명 KOL 랭킹 + 실시간 방송 (치지직/YouTube)
5. **게임사 매출분석** — 131개사 3년(2023-2025) 매출/영업이익
6. **뉴스** — 주요 뉴스 5건 (썸네일) + 최근 뉴스 (20개 펼치기/접기)
7. **캘린더** — 월별 게임 이벤트 + 신작 런칭 (한국/전체만)

## 주요 기능
- **회원가입/로그인** (Supabase Auth)
- **여론 리포트 신청** (로그인 필수, 첨부파일 업로드, 6개 수신 빈도)
- **운영툴** (/admin.html) — 회원/구독 현황
- **매출 추정 방식 팝업** — 국가별 산출 방식 설명
- **다크/라이트 모드**
- **모바일 반응형** (3줄 topbar, 터치 영역 40px)

## 기술 스택
- Frontend: HTML/CSS/JS (인라인, Chart.js)
- Backend: Supabase (Auth + Storage + PostgreSQL)
- Hosting: Cloudflare Pages
- Data: Google Play, Qimai, DC Inside, 치지직 API, YouTube, Sensor Tower
- Build: Python (build_dashboard.py)

## 개발 경로
```
C:\Users\user\Desktop\game_dashboard_v2\     ← 개발 폴더
C:\Users\user\game-dashboard-v2\             ← 배포 폴더 (Cloudflare + GitHub)
```

## Python 경로
```
C:\Users\user\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe
```
