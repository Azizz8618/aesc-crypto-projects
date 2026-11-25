# Учёт экономии токенов (machine-local)

Набор сценариев для ежедневного снимка расхода OpenCode и еженедельного
сводного отчёта. Сценарии только читают локальные журналы `ccusage`, не
вызывают API и не пишут в репозиторий. Методика расчёта — в
[docs/repeated-read-efficiency.md](../../docs/repeated-read-efficiency.md),
фактические замеры — в [docs/token-savings-stats.md](../../docs/token-savings-stats.md).

## Состав

| Файл | Назначение |
| --- | --- |
| `snapshot.sh` | снимает `ccusage opencode daily --json` в `~/.local/share/aesc-token-metrics/<дата>.json` |
| `report.py` | сводит снимки в `~/.local/share/aesc-token-metrics/summary.csv` |
| `crontab.example` | готовые строки для `crontab` |

## Требования

- `ccusage` 20.1.2 в `~/.local/bin/ccusage` (путь можно переопределить переменной `CCUSAGE`);
- Python 3 для `report.py`;
- каталог `~/.local/share/aesc-token-metrics/` создаётся сценарием автоматически.

## Установка cron

```sh
crontab -l > /tmp/cron.bak
cat tools/token-metrics/crontab.example >> /tmp/cron.bak
crontab /tmp/cron.bak
crontab -l | grep aesc-token
```

Cron использует `$HOME`, поэтому путь к репозиторию не нужно править при
изменении имени пользователя. Снимки и CSV остаются вне git.

## Проверка

```sh
tools/token-metrics/snapshot.sh
python3 tools/token-metrics/report.py
tail -3 ~/.local/share/aesc-token-metrics/snapshot.log
head -5 ~/.local/share/aesc-token-metrics/summary.csv
```

## Оговорки

- `ccusage daily` группирует по календарным суткам; сравнивать нужно снимки
  с одинаковым набором дат.
- У бесплатных моделей цена равна 0, поэтому отчёт показывает токены, а не деньги.
- `cacheCreate = 0` в текущих сессиях: метод следит за повторным чтением
  уже прогретого кэша, а не за созданием нового.
