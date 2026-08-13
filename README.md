# Game Market Insight v3.3

3개국(한국/중국/일본) 모바일 게임 시장 통합 대시보드

## URL
- **Cloudflare (메인)**: https://gameinsight.pages.dev
- **GitHub Pages (개발)**: https://jycho7254-commits.github.io/game-dashboard-v2/
- **운영툴**: https://gameinsight.pages.dev/admin.html

## 주요 기능 (v3.3)

### 대시보드
- **7개 탭**: 종합 / 매출순위 / 여론분석 / 인플루언서 / 게임사매출분석 / 뉴스 / 캘린더
- **탭 드롭다운**: 매출순위/여론/인플루언서/뉴스/캘린더에 국가별 서브메뉴 (탭 내부 absolute)
- **다크 테마 only** (라이트 모드 제거)

### 게임사 매출분석
- **매출 TOP15 차트** + **영업이익률 TOP15 차트** (접기/펼치기, 지연 렌더링)
- **게임사 상세 모달**: KPI + 기업정보 + 바로가기 + 연간 매출/영업이익/성장률 차트
- **분기별 추이**: 버튼 클릭 시 4년×4분기 막대 차트 (토글)
- **136개사** (비상장 5개사 추가: 님블뉴런, 세시소프트, 엠게임, 한빛소프트, 블루포션게임즈)

### 회원 서비스
- **회원가입/로그인** (Supabase Auth, 이메일+비밀번호)
- **여론 리포트 신청** (로그인 필수, 14개 수신빈도 옵션)
- **첨부파일 업로드** (Supabase Storage, report-templates 버킷)
- **Gmail SMTP 자동 발송** (send_report_cron.py, 8~18시 매시간)

### 운영툴 (/admin.html)
- 관리자 화이트리스트 (jycho7253@naver.com)
- 회원 목록 (이메일/가입일/로그인/인증상태/삭제)
- 리포트 구독 현황 (이메일/게임/빈도/요청사항/첨부파일 다운로드/차단/해제)
- service_role key로 RLS 무시 조회

### 뉴스
- **주요 뉴스**: 소스별 비율 (인벤 3 + 게임메카 1 + 데일리게임 1)
- **썸네일 반응형**: 16:9 비율, object-fit:cover
- **한국 뉴스 자동 수집**: 루리웹, 인벤, 게임메카, 데일리게임, 게임동아
- **제목 색상**: 하얀색(var(--t1)) 고정

### 데이터 자동화
| 크론 | 시간 | 내용 |
|------|------|------|
| live_update | 10분 | 치지직/YT Live 수집 + GitHub push |
| daily_p1 | 11:00, 17:00 | 매출+DC여론+한국여론+빌드+배포 |
| daily_p2 | 11:20, 17:20 | 한국/중국/일본 뉴스+빌드+배포 |
| weekly | 월 12:00 | Bilibili+JP리뷰 |
| send_report | 8~18시 매시간 | 여론 리포트 이메일 발송 |
| auto_new_games | 새벽 1시 | 신작 게임 자동 감지 |
| backup | 새벽 3시 | 메모리+스킬 백업 |

### 한국 게임명 자동화
- `reestimate_revenue.py`에 36개 수동 매핑 (KR_NAME_MAP)
- Google Play `hl=ko`에서 자동 한국어명 조회

## 데이터 규모 (v3.3)
| 항목 | 수량 |
|------|------|
| 추적 게임 | 150개 (KR/CN/JP 각 50) |
| 게임사 | 136개사 |
| 인플루언서 | 464명 (KR 209 / JP 183 / CN 74) |
| 한국 여론 | 95게임 |
| 한국 뉴스 | 200개 (루리웹 109 + 데일리게임 30 + 인벤 28 + 게임동아 19 + 게임메카 14) |
| 캘린더 이벤트 | 77개 |

## 기술 스택
| 계층 | 기술 |
|------|------|
| 프론트엔드 | HTML + CSS + JavaScript + Chart.js |
| 호스팅 | Cloudflare Pages (no-cache) |
| 인증 | Supabase Auth |
| DB | Supabase PostgreSQL (RLS 적용) |
| 파일 | Supabase Storage |
| 데이터 수집 | Python (cron) |
| 이메일 | Gmail SMTP |

## 파일 구조
```
game_dashboard_v2/
├── templates/index.html      # 메인 템플릿
├── build_dashboard.py        # 빌드 스크립트
├── data/
│   ├── kr_rankings.json      # 한국 매출순위 (50개)
│   ├── cn_rankings.json      # 중국 매출순위 (50개)
│   ├── jp_rankings.json      # 일본 매출순위 (50개)
│   ├── game_company_financials.json  # 게임사 재무 (136개사)
│   ├── kr_news.json          # 한국 뉴스 (200개)
│   ├── cn_news.json          # 중국 뉴스 (25개)
│   ├── jp_news.json          # 일본 뉴스 (10개)
│   ├── all_influencers.json  # 인플루언서 (464명)
│   ├── kr_sentiment_full.json # 한국 여론 (95게임)
│   ├── calendar_events.json  # 캘린더 (77개)
│   └── softc_data.json       # 실시간 스트리머
└── scripts/
    ├── reestimate_revenue.py # 매출 추정 + 한국어명 자동화
    ├── collect_kr_news.py    # 한국 뉴스 자동 수집
    ├── collect_cn_news.py    # 중국 뉴스
    ├── collect_jp_news.py    # 일본 뉴스
    └── collect_dc_mobile.py  # DC 여론 수집 (전체 갤러리)

hermes/scripts/
├── daily_update_p1.py        # 일일 업데이트 Part 1
├── daily_update_p2.py        # 일일 업데이트 Part 2
├── live_update.py            # 실시간 업데이트 (10분)
├── send_report_cron.py       # 여론 리포트 발송
└── auto_new_games.py         # 신작 게임 감지

game-dashboard-v2/            # 배포 폴더
├── index.html                # 빌드 결과 (~1750KB)
├── admin.html                # 운영툴
├── privacy.html              # 개인정보처리방침
├── about.html                # 서비스 소개
├── ARCHITECTURE.md           # 아키텍처 문서
└── README.md                 # 이 파일
```

## 보안
- RLS: authenticated만 INSERT/SELECT (비로그인 차단)
- admin 화이트리스트: jycho7253@naver.com만 접근
- service_role key: admin.html에서만 사용 (운영툴)
- publishable key: 프론트엔드 공개용 (정상)

## TODO (Phase 2)
- 분기별 재무 데이터 공식 수집 (dart-fss)
- 도메인 구매 (gameinsight.kr) + AdSense
- Slack 웹훅 알림
- QA팀용 PDF 리포트 템플릿
- 엑셀/CSV 내보내기
