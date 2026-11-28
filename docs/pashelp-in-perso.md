# PASHELP в PERSO-библиотеке тома 2348

Цель: рабочая P2C-колода на simh не должна содержать `*LIBRA:13`; все
вспомогательные модули, включая `PASHELP`, должны браться из одной библиотеки
`*PERSO:413600`.

## Источник PASHELP

`pascal-re/PERSO.md` указывает системную модульную библиотеку `/*PASCAL` на
диске 2148, зона `440₈` (`*PERSO:410440`). Проверено:

```sh
BESM6_PATH=/usr/local/share/besm6 besmtool view 2148 --start=288 --length=24 --encoding=t
```

В каталоге есть `РАSНЕLР` (строка 18 вывода), первый модуль — `РАSСОМРL`.

## Сборка объединённой библиотеки

Рабочий каталог: `/tmp/.private/azizz/opencode/p2c-all-perso/`.

```sh
# 2148 подключается напрямую как LUN 44; 3041=work.bin, 3042=ccom.bin, 3043=libc.bin
cat > merge_all.job <<'EOF'
user 419900зс5^
dis 41(3041)42(3042)43(3043)44(2148)67(3067-wr)^
dis 31(2113)32(77)33(2148-440)34(2048)^
EEB1A3
*name comball
*perso:440440
*perso:43,cont
*perso:42,cont
*perso:41,cont
*to perso:670000
*end file
``````
ЕКОНЕЦ
EOF
BESM6_PATH=$PWD dispak --path=$PWD --input-encoding=utf8 -l merge_all.job > merge_all.lst
```

Листинг (`merge_all.lst`) показывает загрузку четырёх библиотек и
`ДЛИHA LIBRARY 034 ЗOH` (28 зон); `PASHELP` присутствует в дампе каталога:

```
*PERSO:440440   LIBRARY OT 26.02.82 M3
*PERSO:43,CONT  LIBRARY OT 28.11.26 M1
*PERSO:42,CONT  LIBRARY OT 25.11.26 M1
*PERSO:41,CONT  LIBRARY OT 26.11.26 M1
*TO PERSO:670000   ДЛИHA LIBRARY  034 ЗOH
```

## Запись в том 2348

Дамп 28 зон (`allperso.bin`) записан в зоны `3600..3627₈` рабочей копии
`~/.besm6/2348`; SIMH-заголовки 28 зон пересобраны проверенным
`make_simh_image.py` (`phys=logical+4`, том `2048`, шифр `4103`, тег `01`).
Перед записью создан бэкап
`~/.besm6/2348.bak-pashelp-merge-20261128-093328`.

Текущая контрольная сумма рабочего тома:

```
e3db03178cb4ab29e03dcddb977d5074412df74e11cecf13e6d24d281886ff38  ~/.besm6/2348
be23632c85a231ce643aedaad77a35e054b1c217ba92f81f8207db7e65611960  /usr/local/share/besm6/2348 (эталон, не менялся)
```

## Проверка на simh

Колода `p2c_only_perso.b6` содержит **только одну карту каталога** — `*PERSO:413600`;
карт `*LIBRA` нет:

```
ШИФР 419999 ЗС5^
ОЗУ 32^ТРА 100^АЦП 64^ВРЕ 966^ВХО 4000^
ДИС 41(2048)^
ЕЕВ1А3
*NAME P2CWRK
*CALL YESMEMORY
*PERSO:413600
*NO LOAD LIST
*CALL PASHELP
P 2 0 0001410023B .
*CALL CCOM
*COPY:0,000000,000000
*EXECUTE
*END FILE
``````
ЕКОНЕЦ
```

Свёрка: `grep -c '^\*LIBRA' p2c_only_perso.b6` → `0`.

Образ для md41 собран из проверенного `md41_single`: библиотека записана в
логические зоны `3600..3627`, исходник — в зону `0023₈`. Эмулятор
`d058305796bcd0aa` (SHA-пин), изолированный tmux, case `ONLYPERSO`.

Свежий `runs/localprn_ONLYPERSO.txt` (homoglyphs нормализованы):

```
BESM-6 C THAT NEVER WAS
INITHEAP = ...
MAXHEAP = ...
*EXECUTE
HELLO FROM P2C!
КОНЕЦ ЗАДАЧИ
```

`verdict_ONLYPERSO.txt`: `plumbing PASS`, `completion_marker True`,
`absence_marker False`, `fatal_error False`. `product_gate FAIL` — только
эвристика драйвера, ищущая Fortran-строку `21`, к P2C не относится.

## Итог

`*LIBRA:13` и `*LIBRA:41` удалены из рабочей колоды; `PASHELP`, `PASCOMPL`,
`CCOM` и libc берутся из одной PERSO-библиотеки в зоне `3600₈` тома 2348.
