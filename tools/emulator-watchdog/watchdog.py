#!/usr/bin/env python3
"""Контроль процессов dispak / simh и завершение зависших.

Цели ищутся по comm: dispak, besm6, svs (исполняемые файлы simh).
Интерактивные процессы с терминалом (tty) не трогаются: они могут
законно ждать ввода. Зомби только фиксируются в журнале: их должен
подобрать родитель. Зависшим считается процесс без терминала,
старше --max-age, у которого не растёт CPU-time дольше --stale.
"""

import argparse
import json
import os
import signal
import time

TARGETS = {"dispak", "besm6", "svs"}
HOME_STATE = os.path.expanduser("~/.local/share/emulator-watchdog")
STATE_PATH = os.path.join(HOME_STATE, "state.json")
LOG_PATH = os.path.join(HOME_STATE, "watchdog.log")
HZ = os.sysconf("SC_CLK_TCK")


def boot_time():
    with open("/proc/stat", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("btime"):
                return int(line.split()[1])
    return 0


def read_proc(pid):
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as fh:
            raw = fh.read()
        with open(f"/proc/{pid}/comm", encoding="utf-8") as fh:
            comm = fh.read().strip()
        with open(f"/proc/{pid}/cmdline", "rb") as fh:
            cmdline = fh.read().replace(b"\0", b" ").decode("utf-8", "replace")
    except (OSError, ValueError):
        return None
    rest = raw[raw.rfind(")") + 2:].split()
    if len(rest) < 20:
        return None
    return {
        "pid": pid,
        "comm": comm,
        "state": rest[0],
        "tty_nr": int(rest[4]),
        "cpu": int(rest[11]) + int(rest[12]),
        "starttime": int(rest[19]),
        "cmdline": cmdline[:200],
    }


def log(message):
    os.makedirs(HOME_STATE, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S%z')} {message}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age", type=int, default=7200,
                    help="возраст процесса в секундах (по умолчанию 7200)")
    ap.add_argument("--stale", type=int, default=1800,
                    help="отсутствие CPU-прогресса в секундах (по умолчанию 1800)")
    ap.add_argument("--grace", type=int, default=300,
                    help="пауза между SIGTERM и SIGKILL (по умолчанию 300)")
    ap.add_argument("--dry-run", action="store_true",
                    help="только журналировать, не посылать сигналы")
    args = ap.parse_args()

    btime = boot_time()
    now = time.time()
    state = {}
    try:
        with open(STATE_PATH, encoding="utf-8") as fh:
            state = json.load(fh)
    except (OSError, ValueError):
        pass

    alive = set()
    found = 0
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        info = read_proc(int(name))
        if not info or info["comm"] not in TARGETS:
            continue
        found += 1
        age = now - (btime + info["starttime"] / HZ)
        key = f"{info['pid']}:{info['starttime']}"
        alive.add(key)
        prefix = (f"pid={info['pid']} comm={info['comm']} age={age:.0f}s "
                  f"state={info['state']} tty={info['tty_nr']}")

        if info["tty_nr"] != 0:
            log(f"SKIP interactive {prefix}")
            continue
        if info["state"] == "Z":
            log(f"ZOMBIE {prefix} (нужен родитель)")
            continue

        prev = state.get(key, {})
        if info["state"] == "D" and age > args.max_age:
            log(f"HANG-D {prefix} -> SIGKILL" + (" (dry-run)" if args.dry_run else ""))
            if not args.dry_run:
                os.kill(info["pid"], signal.SIGKILL)
            state.pop(key, None)
            continue

        if age <= args.max_age:
            state[key] = {"cpu": info["cpu"], "seen": now}
            log(f"WATCH {prefix}")
            continue

        cpu_same = prev and prev.get("cpu") == info["cpu"]
        stale_for = now - prev.get("seen", now) if prev else 0
        if cpu_same and stale_for >= args.stale:
            term = prev.get("term")
            if term and now - term >= args.grace:
                log(f"HANG-CPU {prefix} -> SIGKILL" + (" (dry-run)" if args.dry_run else ""))
                if not args.dry_run:
                    os.kill(info["pid"], signal.SIGKILL)
                state.pop(key, None)
            else:
                log(f"HANG-CPU {prefix} -> SIGTERM" + (" (dry-run)" if args.dry_run else ""))
                if not args.dry_run:
                    os.kill(info["pid"], signal.SIGTERM)
                    prev["term"] = now
                    state[key] = prev
        else:
            state[key] = {"cpu": info["cpu"], "seen": now,
                          "term": prev.get("term") if cpu_same else None}
            log(f"WATCH {prefix} cpu-progress")

    for key in list(state):
        if key not in alive:
            state.pop(key, None)

    os.makedirs(HOME_STATE, exist_ok=True)
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    os.replace(tmp, STATE_PATH)
    log(f"SCAN targets={found} tracked={len(state)}")


if __name__ == "__main__":
    main()
