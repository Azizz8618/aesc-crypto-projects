#!/usr/bin/env python3
"""Сводит ежедневные снимки ccusage в summary.csv (machine-local)."""

import csv
import glob
import json
import os

OUT = os.path.expanduser("~/.local/share/aesc-token-metrics")
FIELDS = (
    "inputTokens",
    "outputTokens",
    "cacheReadTokens",
    "cacheCreationTokens",
)

rows = {}
for path in sorted(glob.glob(os.path.join(OUT, "*.json"))):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        continue
    for item in data.get("daily", []):
        day = item.get("date")
        if not day:
            continue
        rows[day] = {key: item.get(key, 0) for key in FIELDS}

out_path = os.path.join(OUT, "summary.csv")
with open(out_path, "w", newline="", encoding="utf-8") as fh:
    writer = csv.writer(fh)
    writer.writerow([
        "date", "input", "output", "cache_read", "cache_create",
        "total", "cache_share_pct", "context_share_pct", "multiplier",
    ])
    for day in sorted(rows):
        v = rows[day]
        total = sum(v.values())
        context = v["inputTokens"] + v["cacheReadTokens"]
        writer.writerow([
            day,
            v["inputTokens"],
            v["outputTokens"],
            v["cacheReadTokens"],
            v["cacheCreationTokens"],
            total,
            round(100 * v["cacheReadTokens"] / total, 3) if total else 0,
            round(100 * v["cacheReadTokens"] / context, 3) if context else 0,
            round(context / v["inputTokens"], 2) if v["inputTokens"] else 0,
        ])

print(f"rows={len(rows)} out={out_path}")
