#!/usr/bin/env python3
"""data/ipos.json -> calendar.ics (공모주 청약·상장 일정 구독 피드).

- 청약: 시작~마감 종일 일정, 마감일 09:00 알림
- 상장: 종일 일정, 08:30 알림
- UID는 종목 id 기반이라 다시 만들어도 같은 일정으로 갱신됨
"""
import json
import os
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://vincent533.github.io/ipo-calendar/"
DOMAIN = "vincent533.github.io"


def esc(s):
    return (str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
            .replace("\r\n", "\\n").replace("\n", "\\n"))


def fold(line):
    """RFC 5545: 75 octet 단위로 접기 (UTF-8 글자 중간에서 자르지 않음)."""
    out, cur, n = [], "", 0
    limit = 75
    for ch in line:
        b = len(ch.encode("utf-8"))
        if n + b > limit:
            out.append(cur)
            cur, n, limit = " " + ch, 1 + b, 75
        else:
            cur += ch
            n += b
    out.append(cur)
    return "\r\n".join(out)


def d(s):
    return date.fromisoformat(s)


def ymd(x):
    return x.strftime("%Y%m%d")


def brokers_text(it):
    b = it.get("brokers") or []
    if isinstance(b, str):
        return b
    return ", ".join(b) if b else "확인중"


def dtstamp(updated):
    try:
        t = datetime.fromisoformat(str(updated).replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone(timedelta(hours=9)))
        return t.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return "20260101T000000Z"


def describe(it, kind):
    lines = []
    if kind == "sub":
        lines.append(f"청약 {it['subscribeStart']} ~ {it['subscribeEnd']}")
        if it.get("refundDate"):
            lines.append(f"환불일 {it['refundDate']}")
        if it.get("listDate"):
            lines.append(f"상장일 {it['listDate']}")
    else:
        lines.append(f"상장일 {it['listDate']}")
        r = it.get("result") or {}
        if r.get("openReturnPct") is not None:
            lines.append(f"시초가 수익률 {r['openReturnPct']:+.1f}%")
    lines.append(f"종합점수 {it.get('score') or '없음'}")
    lines.append(f"최소증거금 {it.get('minDeposit') or '확인중'}")
    lines.append(f"주관사 {brokers_text(it)}")
    dm = it.get("demand") or {}
    if dm.get("offerPrice"):
        lines.append(f"확정공모가 {dm['offerPrice']:,}원")
    if dm.get("instCompetition") is not None:
        lines.append(f"기관경쟁률 {dm['instCompetition']:,}:1")
    lines.append(f"달력 {SITE}")
    return "\n".join(lines)


def build():
    data = json.load(open(os.path.join(ROOT, "data", "ipos.json"), encoding="utf-8"))
    stamp = dtstamp(data.get("updatedAt"))
    L = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//vincent533//ipo-calendar//KO",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:공모주 달력", "X-WR-TIMEZONE:Asia/Seoul",
        "X-WR-CALDESC:공모주 청약·상장 일정 (" + SITE + ")",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H",
    ]
    n = 0
    for it in sorted(data["items"], key=lambda x: x.get("subscribeStart") or ""):
        iid, name = it["id"], it["name"]
        if it.get("subscribeStart") and it.get("subscribeEnd"):
            s, e = d(it["subscribeStart"]), d(it["subscribeEnd"])
            days = (e - s).days
            L += ["BEGIN:VEVENT", f"UID:{iid}-sub@{DOMAIN}", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{ymd(s)}", f"DTEND;VALUE=DATE:{ymd(e + timedelta(days=1))}",
                  f"SUMMARY:{esc('[청약] ' + name)}", f"DESCRIPTION:{esc(describe(it, 'sub'))}",
                  f"URL:{SITE}", "TRANSP:TRANSPARENT",
                  "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(name + ' 청약 마감일')}",
                  f"TRIGGER;RELATED=START:P{days}DT9H" if days else "TRIGGER;RELATED=START:PT9H",
                  "END:VALARM", "END:VEVENT"]
            n += 1
        if it.get("listDate"):
            s = d(it["listDate"])
            L += ["BEGIN:VEVENT", f"UID:{iid}-list@{DOMAIN}", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{ymd(s)}", f"DTEND;VALUE=DATE:{ymd(s + timedelta(days=1))}",
                  f"SUMMARY:{esc('[상장] ' + name)}", f"DESCRIPTION:{esc(describe(it, 'list'))}",
                  f"URL:{SITE}", "TRANSP:TRANSPARENT",
                  "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(name + ' 오늘 상장')}",
                  "TRIGGER;RELATED=START:PT8H30M", "END:VALARM", "END:VEVENT"]
            n += 1
    L.append("END:VCALENDAR")
    out = "\r\n".join(fold(x) for x in L) + "\r\n"
    with open(os.path.join(ROOT, "calendar.ics"), "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print(f"calendar.ics: {n} events")


if __name__ == "__main__":
    build()
