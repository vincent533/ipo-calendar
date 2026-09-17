# 공모주 달력

한국 공모주(IPO) 청약·상장 일정을 월간 달력으로 보여주는 정적 웹페이지입니다.

## 열기

프로젝트 루트(`/workspace/ipo-calendar`)에서 정적 서버를 띄운 뒤 브라우저로 접속합니다.

```bash
cd /workspace/ipo-calendar
python3 -m http.server 8765
```

브라우저에서 열기: [http://127.0.0.1:8765/](http://127.0.0.1:8765/)

> `file://`로 `index.html`을 직접 열면 `fetch('./data/ipos.json')`이 브라우저 보안 정책 때문에 실패할 수 있습니다. 반드시 HTTP 서버로 열어 주세요.

## 데이터 업데이트

시드 데이터는 `data/ipos.json`에 있습니다. 파일을 수정한 뒤 브라우저를 새로고침하면 달력이 갱신됩니다.

### 스키마

```json
{
  "updatedAt": "2026-09-16T15:20:00+09:00",
  "items": [
    {
      "id": "neosapiens",
      "name": "네오사피엔스",
      "score": "B",
      "minDeposit": "10만원",
      "subscribeStart": "2026-09-10",
      "subscribeEnd": "2026-09-11",
      "listDate": "2026-09-21"
    }
  ]
}
```

| 필드 | 설명 |
|------|------|
| `id` | 고유 식별자 (영문 슬러그) |
| `name` | 종목명 |
| `score` | 종합점수. 모르면 `null` → 화면에는 **없음** |
| `minDeposit` | 최소청약금액. 모르면 `null` → 화면에는 **미확인** |
| `subscribeStart` / `subscribeEnd` | 청약 기간 (`YYYY-MM-DD`, 포함) |
| `listDate` | 상장일 (`YYYY-MM-DD`) |
| `updatedAt` | 데이터 갱신 시각 (ISO 8601) |

### 카드 표시

각 날짜 칸에는 **종목명 · 최소청약금액 · 종합점수**만 표시됩니다.

- 파란 계열 카드 = 청약일
- 초록 계열 카드 = 상장일

## 구성

```
ipo-calendar/
├── index.html      # 단일 페이지 앱 (vanilla HTML/CSS/JS)
├── data/ipos.json  # IPO 시드 데이터
└── README.md
```
