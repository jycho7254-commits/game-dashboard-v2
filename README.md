# Game Market Insight v3.1

3개국(한국/중국/일본) 모바일 게임 시장 통합 대시보드

## URL
- **Cloudflare (메인)**: https://gameinsight.pages.dev
- **GitHub Pages (개발)**: https://jycho7254-commits.github.io/game-dashboard-v2/
- **운영툴**: https://gameinsight.pages.dev/admin.html

## 아키텍처
```
[데이터 수집]
  ├─ live_update.py (10분 크론) — 치지직 + YouTube Live + GitHub push
  ├─ daily_update_p1.py (11시/17시) — 매출 + 여론 + 뉴스 + 빌드
  ├─ reestimate_revenue.py — 3개국 매출 추정 (로그 곡선)
  └─ build_dashboard.py — 인라인 HTML 빌드

[배포]
  ├─ Cloudflare Pages (gameinsight.pages.dev) — 메인, no-cache, 무료 무제한
  ├─ GitHub Pages — 개발/백업
  └─ Netlify — 폐기 (크레딧 소모)

[백엔드]
  └─ Supabase
      ├─ Auth (회원가입/로그인, Confirm email OFF)
      ├─ Storage (report-templates bucket)
      └─ DB (report_subscriptions 테이블, RLS 완료)
```

## 데이터 규모
| 항목 | 수량 | 출처 |
|------|------|------|
| 한국 매출 순위 | 50개 | Google Play |
| 중국 매출 순위 | 50개 | iOS Qimai |
| 일본 매출 순위 | 50개 | Google Play |
| 게임사 재무 | 131개사 | DART/CSRC/HKEX/EDINET 공식 공시 |
| 인플루언서 | 464명 | YouTube/치지직/Bilibili (중복 제거) |
| 한국 여론 | 87개 게임 | DC/GP/YT/아카 |
| 중국 여론 | 280개 게임 | Bilibili/TapTap |
| 일본 여론 | 282개 게임 | 5ch/YouTube |
| 한국 뉴스 | 149개 | 게임메카/인벤/루리웹/데일리게임/게임동아 |
| 캘린더 | 177개 이벤트 | wame.is + 자체 수집 |
| 실시간 방송 | 치지직 30 + YouTube Live | 공개 API |

## 탭 구조
1. **종합** — KPI + 매출 Top10 차트(순번) + 시장 점유율 + 트렌드 아이콘 그리드 + 클릭 시 팝업
2. **매출 순위** — 국가별 Top50 + 국가별 차트 (한/중/일 분리) + 매출 추정 팝업 + 꺾은선 추이
3. **여론 분석** — 게임별 여론 지수 + 여론 지수 기준 팝업 + 여론 리포트 신청 (로그인 필수)
4. **인플루언서** — 464명 KOL 랭킹 + 실시간 방송 (치지직/YouTube)
5. **게임사 매출분석** — 131개사 3년(2023-2025) 매출/영업이익
6. **뉴스** — 주요 뉴스 5건 (썸네일) + 최근 뉴스 20개 (날짜 표시, 펼치기/접기)
7. **캘린더** — 월별 게임 이벤트 + 신작 런칭 (한국/전체만)

## 주요 기능
- **호버 드롭다운 서브메뉴** — 탭에 마우스 올리면 국가별(한/중/일) 바로 이동
- **전체 너비 탭** — 7개 탭이 한 줄 꽉 채움 (16px 폰트)
- **회원가입/로그인** (Supabase Auth)
- **여론 리포트 신청** (로그인 필수, 첨부파일 업로드 → Supabase Storage, 6개 수신 빈도)
- **운영툴** (/admin.html) — 회원/구독 현황
- **매출 추정 방식 팝업** — 국가별 산출 방식 설명
- **다크/라이트 모드**
- **모바일 반응형** (3줄 topbar, 터치 영역 40px, 테이블 컬럼 숨김)

## 기술 스택
- Frontend: HTML/CSS/JS (인라인, Chart.js)
- Backend: Supabase (Auth + Storage + PostgreSQL)
- Hosting: Cloudflare Pages (wrangler CLI)
- Data: Google Play, Qimai, DC Inside, 치지직 API, YouTube, Sensor Tower
- Build: Python (build_dashboard.py)

## 배포 명령어
```bash
PY=/c/Users/user/AppData/Roaming/uv/python/cpython-3.11-windows-x86_64-none/python.exe

# 빌드
cd /c/Users/user/Desktop/game_dashboard_v2
$PY build_dashboard.py

# Cloudflare 배포
cd /c/Users/user/game-dashboard-v2
npx wrangler pages deploy . --project-name gameinsight --branch main

# GitHub Pages
git add -A && git commit -m "msg" && git push origin master
```

## 개발 경로
```
C:\Users\user\Desktop\game_dashboard_v2\     ← 개발 폴더
C:\Users\user\game-dashboard-v2\             ← 배포 폴더 (Cloudflare + GitHub)
```

## Python 경로
```
C:\Users\user\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe
```

## 백업
```
C:\Users\user\Desktop\game_dashboard_v2_backup_0805\  (.bak2~.bak14)
```
