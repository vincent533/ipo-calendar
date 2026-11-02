#!/usr/bin/env bash
# 공모주 달력 배포: calendar.ics 재생성 → 커밋 → push (GitHub Pages 자동 반영)
# 사용: ./deploy.sh ["커밋 메시지"]
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/build_ics.py
FILES=()
for f in data/ipos.json calendar.ics index.html scripts deploy.sh README.md; do
  [ -e "$f" ] && FILES+=("$f")
done
git add -- "${FILES[@]}"
if git diff --cached --quiet; then
  echo "변경 없음 — 배포 생략"
  exit 0
fi
git -c user.name=vincent533 -c user.email=vincent533@users.noreply.github.com \
  commit -q -m "${1:-Update IPO data $(TZ=Asia/Seoul date '+%Y-%m-%d %H:%M')}"
git push -q origin main
echo "배포 완료: $(git rev-parse --short HEAD)"
