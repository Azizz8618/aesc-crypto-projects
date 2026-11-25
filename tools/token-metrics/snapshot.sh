#!/bin/sh
# Ежедневный machine-local снимок расхода OpenCode.
# Не отправляет данные в сеть и не пишет в репозиторий.
set -eu
export PATH=/usr/bin:/bin:/usr/local/bin:$HOME/.local/bin

OUT="$HOME/.local/share/aesc-token-metrics"
CCUSAGE="${CCUSAGE:-$HOME/.local/bin/ccusage}"
mkdir -p "$OUT"

DAY=$(date +%F)
TMP="$OUT/.$DAY.json.$$"
FILE="$OUT/$DAY.json"

"$CCUSAGE" opencode daily --json > "$TMP"
mv "$TMP" "$FILE"

printf '%s snapshot=%s bytes=%s\n' \
    "$(date -Is)" "$FILE" "$(wc -c < "$FILE")" >> "$OUT/snapshot.log"
