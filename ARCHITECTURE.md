# 대시보드 아키텍처 v3.3

## 시스템 구성도

```
┌─────────────────────────────────────────────────────┐
│                  사용자 브라우저                       │
│         https://gameinsight.pages.dev                │
│              (Cloudflare CDN, no-cache)              │
├─────────────────────────────────────────────────────┤
│  HTML/CSS/JS (인라인)  │  Chart.js  │  Supabase JS   │
├──────────┬──────────┬──────────┬───────────────────┤
│  대시보드  │  운영툴   │  Auth    │  Storage          │
│  7개 탭   │ /admin   │ 회원가입  │ report-templates  │
│  드롭다운  │ 화이트리스트│ 로그인   │ 첨부파일 업로드    │
└──────────┴──────────┴────┬─────┴───────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Supabase   │
                    │ PostgreSQL  │
                    │   (RLS)     │
                    │             │
                    │ report_     │
                    │ subscriptions│
                    │ Auth Users  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Gmail     │
                    │   SMTP      │
                    │ 리포트 발송  │
                    └─────────────┘

┌─────────────────────────────────────────────────────┐
│                  Python 데이터 파이프라인              │
│                  (Hermes Cron)                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [10분] live_update.py                              │
│    └─ 치지직/YT Live 수집 → GitHub push              │
│                                                     │
│  [11:00/17:00] daily_update_p1.py                   │
│    ├─ Google Play / Qimai 랭킹 수집                  │
│    ├─ DC 모바일 여론 수집 (전체 90개 갤러리)           │
│    ├─ 한국 여론 통합 (DC + GP + YT)                  │
│    └─ 빌드 + 배포                                    │
│                                                     │
│  [11:20/17:20] daily_update_p2.py                   │
│    ├─ 한국 뉴스 수집 (루리웹/인벤/게임메카/데일리게임)  │
│    ├─ 중국/일본 뉴스 수집                             │
│    └─ 빌드 + 배포                                    │
│                                                     │
│  [8~18시 매시간] send_report_cron.py                │
│    ├─ Supabase에서 구독자 조회                       │
│    ├─ freq별 발송 대상 필터링                        │
│    ├─ 게임별 여론+매출 데이터 수집                    │
│    └─ Gmail SMTP 발송                               │
│                                                     │
│  [새벽 1시] auto_new_games.py                       │
│    └─ 신작 게임 자동 감지 + 아이콘/여론 수집          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 데이터 흐름

```
Google Play / Qimai / DC갤러리 / 치지직 / YouTube
              │
              ▼
     Python 수집 스크립트 (cron)
              │
              ▼
     JSON 파일 (data/*.json)
              │
              ▼
     build_dashboard.py (인라인 빌드)
              │
              ▼
     index.html (단일 파일, ~1.75MB)
              │
              ├──→ Cloudflare Pages (wrangler deploy)
              └──→ GitHub Pages (git push)
              │
              ▼
        사용자 브라우저
```

## 캐시 정책

| 플랫폼 | 캐시 | 비고 |
|--------|------|------|
| Cloudflare Pages | **no-cache** | must-revalidate, 즉시 반영 |
| GitHub Pages | 10분 | 개발용 |

## Chart.js 인스턴스 관리

| 변수명 | 위치 | 용도 |
|--------|------|------|
| `window.rankChart` | 매출순위 탭 | 국가별 TOP10 막대 |
| `window.ovChart` | 종합 탭 | 전체 TOP10 막대 |
| `window.coChart` | 게임사 탭 메인 | 매출 TOP15 (메인 페이지) |
| Chart.getChart('co-profit-chart') | 게임사 탭 | 영업이익률 TOP15 (지연 렌더링) |
| `window.coChartModal` | 게임사 모달 | 개별사 연간 매출+영업이익+성장률 |
| `window.coChartQ` | 게임사 모달 | 분기별 추이 (토글) |
| `window.modalChart` | 게임 상세 모달 | 게임별 매출 추이 |

> **주의**: Canvas ID 충돌 방지를 위해 모달 차트는 `co-modal-chart` ID 사용

## Supabase 테이블

```sql
-- report_subscriptions
CREATE TABLE report_subscriptions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT NOT NULL,
  game TEXT NOT NULL,
  freq TEXT DEFAULT 'daily-8',
  notes TEXT,
  file_name TEXT,
  file_url TEXT,
  file_path TEXT,
  user_id UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  active BOOLEAN DEFAULT TRUE
);

-- RLS 정책
-- INSERT: authenticated만
-- SELECT: authenticated 전체 (운영툴에서 service_role로 조회)
-- Storage: authenticated만 업로드/조회 (report-templates 버킷)
```

## 뉴스 데이터 구조

```
주요 뉴스 (5개):
  인벤 3개 + 게임메카 1개 + 데일리게임 1개
  썸네일 비율: 16:9 (aspect-ratio)
  제목 색상: var(--t1) !important (링크 파란색 방지)

일반 뉴스 (20개):
  전체 소스에서 최신순
```

## 한국 여론 데이터

```
수집 소스:
  - DC 갤러리 (90개 고유 갤러리, collect_dc_mobile.py)
  - Google Play 평점 (kr_rankings.json)
  - YouTube 댓글 (yt_sentiment_data.json)

통합 가중치:
  DC 40% + GP 35% + YT 25%

지수 계산:
  index = 50 + (total_pos - total_neg) * 3
  범위: 0~100
  70+ 긍정 / 45-54 중립 / 30- 부정

현재: 95게임 (DC 갤러리 90개에서 수집)
```

## 크론 스케줄

| 크론 ID | 이름 | 스케줄 | 스크립트 |
|---------|------|--------|---------|
| 77cddc6a27ee | 실시간 통합 업데이트 | every 10m | live_update.py |
| 9bd09d267be7 | Part1 매출+DC+빌드 | 0 11 * * * | daily_update_p1.py |
| b5b5b9baf5c3 | Part2 뉴스+배포 | 20 11 * * * | daily_update_p2.py |
| ccf52c34f6c3 | 2차 업데이트 | 0 17 * * * | daily_update_p1.py |
| 28ae4aad8586 | 2차 배포 | 20 17 * * * | daily_update_p2.py |
| 656d175f02f9 | 리포트 자동 발송 | 0 8-18 * * * | send_report_cron.py |
| aaa557c34300 | 신작 게임 감지 | 0 1 * * * | auto_new_games.py |
| 6d83018a30ba | 메모리+스킬 백업 | 0 3 * * * | backup_memory.py |
| dad08213e838 | 인플루언서 재확인 | 0 2 * * * | influencer_check.py |
| 84bd9633ade0 | 주간 Bilibili+JP리뷰 | 0 12 * * 1 | weekly_data.py |
