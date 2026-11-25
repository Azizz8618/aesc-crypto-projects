# Значения опкодов БЭСМ-6 020, 021, 033, 036, 046, 047 — итоги веб-исследования

Дата: 2026-11-19. Режим: только чтение + один выходной файл (src/, include, REFERENCE не изменены).

> **ФИНАЛЬНАЯ КОРРЕКЦИЯ (2026-11-19, перекрывает выводы ниже).** Наши машинные слова имеют **бит 20 = 0 ⇒ SHORT (первый тип, `CmdSheet.md:17`)**, а не LONG (`CmdSheet.md:96` — второй тип, бит 20 = 1). В `besm6tape.py:84` стоит `is_long = (h >> 19) & 1` — **off-by-one баг**: проверяется бит 19 вместо бита 20, поэтому он даёт **ошибочный `is_long=1` из-за бита 19**. Все прежние выводы «в нашем коде LONG», «Additional system call», «flush BRZ» и «втбрз» для наших слов недействительны: `втбрз` — имя подпрограммы `gens1.be`, а не мнемоника opcode. Корректные SHORT-значения: 020=`сбр`/`APX`, 021=`рзб`/`AUX`, 033=`увв`/`EXT`, 036=`сда`/`ASN` (сдвиг на N−64), 046/047=незаконные/не используемые (`disbesm6.c:61,62,72,75,83,84`).


## 0. Главное предупреждение: один opcode = две разные команды

БЭСМ-6 имеет **два формата 24-битной команды**, и восьмеричный opcode сам по себе не определяет команду — нужен бит 20 (формат):

- **Формат 1 (короткий, bit 20 = 0)**: opcode = биты 19…13, диапазон **000–077**.
- **Формат 2 (длинный, bit 20 = 1)**: opcode = биты 19…16, диапазон **20–37**.

> Цитата (mailcom, база opcodes):
> «Traditionally, the opcodes in opcode lists are written in octal including bits 20 to 13 or 20 to 16 and assuming S = 0, therefore the opcode ranges are 000 to 077 for format 1 and 20 to 37 for format 2.»
> — https://www.mailcom.com/besm6/instset.shtml

> Цитата (Besm6_Instruction_Set.md):
> «Note that opcode 033 names *two* instructions: this one in the first structure (Format 1, long address) and STOP in the second (Format 2). The address-field width is what distinguishes them.»
> — https://github.com/sergev/vcc/blob/main/backend/besm6/Besm6_Instruction_Set.md

Поэтому все запрошенные opcode следует читать **в обоих форматах**; ниже приведены оба значения.

## 1. Авторитетные источники (найдены и использованы)

| # | Источник | URL | Статус |
|---|----------|-----|--------|
| S1 | «Краткий перечень команд БЭСМ-6», Энциклопедия БЭСМ-6 (besm6.org) | https://www.besm6.org/wiki/CmdSheet.html | Первичная таблица opcode'ов; есть обе структуры (короткая и длинная) |
| S2 | BESM-6 Instruction Set, Leonid Broukhis | https://www.mailcom.com/besm6/instset.shtml | Классическое описание набора команд с формулами и ω-режимом |
| S3 | BESM-6 Instruction Set Reference, S. Vakulenko (vcc) | https://github.com/sergev/vcc/blob/main/backend/besm6/Besm6_Instruction_Set.md | Самая полная современная спецификация; основана на руководстве + эмуляторе |
| S4 | Bemsh: The BESM-6 Autocode (Shtarkman, 1967), S. Vakulenko | https://github.com/sergev/vcc/blob/main/backend/besm6/Bemsh.md | Таблицы мнемоник БЕМШ по opcode'ам (короткие и длинные) |
| S5 | BESM-6 Unix Assembler Manual (b6as) | https://github.com/sergev/vcc/blob/main/backend/besm6/Besm6_Unix_Assembler.md | Подтверждает, у каких opcode нет мнемоники |
| S6 | BESM-6 Compiler Intrinsics | https://github.com/sergev/vcc/blob/main/backend/besm6/Besm6_Intrinsics.md | Назначение 020/021/033, имя «э74», «кэш БРЗ» |

Сырые (raw) ссылки для цитирования:
- https://raw.githubusercontent.com/sergev/vcc/main/backend/besm6/Besm6_Instruction_Set.md
- https://raw.githubusercontent.com/sergev/vcc/main/backend/besm6/Bemsh.md
- https://raw.githubusercontent.com/sergev/vcc/main/backend/besm6/Besm6_Unix_Assembler.md
- https://raw.githubusercontent.com/sergev/vcc/main/backend/besm6/Besm6_Intrinsics.md

Недоступно/не дало результата: https://www.computer-museum.ru/histsoft/besm6.htm → 404; https://ru.wikipedia.org/wiki/БЭСМ-6 — только общие сведения (50 команд, 24 бита, 15 индексных регистров), таблицы opcode'ов нет.

## 2. Сводная таблица requested opcode'ов

| Opcode (восьм.) | Формат 1 — короткий (000–077) | Формат 2 — длинный (20–37) |
|---|---|---|
| **020** | **СБР / сбр / APX** — «сборка», упаковка битов A по маске X (сброс Y, ω=логический). | **Э20 / э20** — неименованная команда, отнесённая к «экстракодам» в S1; в S3/S6: extracode 020 (0200) = «Additional system call»; ω=логический. |
| **021** | **РЗБ / рзб / AUX** — «разборка», распаковка старших битов A по маске X (обратная APX, сброс Y, ω=логический). | **Э21 / э21** — то же, что 020: extracode 021 (0210) = «Additional system call»; ω=логический. |
| **033** | **Э033 / УВВ / EXT** — «управление вводом-выводом»: обмен A ↔ периферийный регистр по EA. **Только супервизорный режим** (в пользовательском — Illegal instruction). | **Э33 / СТОП / STOP** — останов процессора; доступен в обоих режимах; на реальной машине возобновляемый (код останова в 15-битном поле адреса). |
| **036** | **СД / СДА / ASN** — «сдвиг по адресу» / shift immediate: сдвиг A на `N − 64` (N = EA[7:1]), без обращения к памяти, Y=0, ω=логический. | **Э36 / *36** — недокументированная команда; работает как VZM (034): переход при ИР=0. В оригинальном руководстве описан **дополнительный эффект «flush BRZ»**; в эмуляторе не реализован. |
| **046** | **Э046** — в S1 первая из диапазона «экстракоды» (046–077); в S3/S4 — **незаконный код**: «соп» (special memory access), Illegal instruction; в S5 — «Unused, but identical to 044»; в S2 — «Unused, but identical to 044». | Не существует (диапазон длинных opcode'ов — 020–037). |
| **047** | В S1 пустая строка (диапазон экстракодов); в S3/S4 — **незаконный код** (э47), Illegal instruction; в S2 — «Unused, but identical to 045». | Не существует. |

Ключевой вывод: **046/047 не являются «обычными» рабочими командами** — это зарезервированные/незаконные коды (в S1 они записаны как начало области экстракодов 046–077, в S3/S4 — Illegal).

## 3. Детальные значения с цитатами

### 020 (короткий) — APX / СБР, упаковка битов

> S3: «#### 020 — APX (сбр) — Pack bits — Compresses the bits of A selected by mask X into the LSBs of the result… Bits of A where the corresponding mask bit in X is 1 are gathered and packed into the most-significant positions of the result. ω mode: Logical.»

> S6: «__besm6_apx — gather (сбр). For each bit position i from 1 to 48, if mask[i] is set, a[i] is collected… k = popcount(mask) bits occupy result bits 48 down to 48−k+1. This is the opposite alignment from x86's PEXT.»

> S1 (таблица, короткий тип): «020 | сб | сбр | apx | сборка | Л»

> S2: «020 | APX | Pack bits in A masked by X. Did the inventors of INTERCAL know about this instruction? | Logical»

### 021 (короткий) — AUX / РЗБ, распаковка битов

> S3: «#### 021 — AUX (рзб) — Unpack bits — Spreads the MSBs of A into positions selected by mask X (inverse of APX)… ω mode: Logical.»

> S1: «021 | рб | рзб | aux | разборка | Л»

> S2: «021 | AUX | Unpack bits in A using mask X | Logical»

> S6: «__besm6_aux — scatter (рзб). The exact inverse. Each 1-bit of mask, scanned from bit 48 down, consumes one bit from a taken from a's MSB downward and deposits it at that position; 0-bits of mask yield 0.»

### 020 / 021 (длинный) — «э20 / э21», дополнительные системные вызовы

> S1 (таблица команд второго типа, 20 бит = «1»): «20 | э20 | | | экстракоды |» и «21 | э21 | | |» (прочерк в строке 21 означает продолжение группы «экстракоды»).

> S4 (long table): «Э20 | 020 | extracode | —» и «Э21 | 021 | extracode | —».

> S3 (раздел Extracodes): «020 (0200) | Additional system call» и «021 (0210) | Additional system call»; «Extracodes are the system call and mathematical library interface… They execute in user mode… Each assembler spells an extracode by its opcode rather than by a mnemonic, and each does it differently: Madlen `,*74,`, Bemsh `э74`, `b6as` `$74`.»

> S5: «Opcodes with no dedicated mnemonic (the extracodes and reserved slots — e.g. `032`, `046`…`077`, and long `020`, `021`, `036`) have no named form; write them with the raw `$NN`/`@NN` syntax.»

### 033 — две команды: EXT (короткий) и STOP (длинный)

> S1 короткий: «033 | э033 | увв | ext | управление вводом-выводом | П»
> S1 длинный: «33 | э33 | стоп | 33 | останов процессора | -»

> S3 §033 EXT: «A ↔ peripheral register named by EA. Kernel mode only. Throws Illegal instruction in user mode. The machine's other supervisor instruction, and the only way to reach a peripheral: drums, disks, tape, printer, punches, card equipment, terminals… One bit of the address — 04000 — selects a read.»

> S3 §033 STOP: «halt. Stops the processor. Accessible in both user and kernel mode. On real hardware the halt is resumable: the machine stops, the operator reads the halt reason — the instruction's own 15-bit address field — off the console, presses continue, and execution carries on at the next instruction.»

> S6: «There is no way to express either one in C… `033` `ext` увв reaches the peripherals… Every device driver becomes a sequence of `033` control words.»

### 036 — ASN (короткий) и *36/э36 (длинный)

> S1 короткий: «036 | сд | сда | asn | сдвиг по адресу | Л»
> S1 длинный: «36 | э36 | | | тоже что и э34 |» (э34 = «пио»/VZM — переход при ИР=0).

> S3 §036 ASN: «Immediate form of ASX: shifts by N − 64 bits using the low 7 bits of EA. When N > 64 — shift to the right. When N < 64 — shift to the left. No memory access. ω mode: Logical.»

> S3 §036 *36: «#### 036 — *36 (э36) — (Undocumented, same as VZM)… Behaves identically to VZM (034). **Documented in the original manual as having an additional "flush BRZ" side-effect, but implemented identically in this emulator.**»

> S2: «036 | ASN | Shift immediate | Y = 0; if (N >= 64) [A,Y] >>= N-64; else [Y,A] <<= 64-N; | Logical»; и «36 | Unused, but identical to 34» (в таблице формата 2).

> S4 long table: «— | 036 | free operation code | *36».

### 046 / 047

> S1: «046 | э046 | | | экстракоды | -», «047 | … | -» (пустые строки 047–077).

> S3: «#### 046 — (соп) — Special memory access — **Illegal.** Throws `Illegal instruction` in all modes.»; «#### 047 — (э47) — **Illegal.** Throws `Illegal instruction` in all modes.»

> S2: «046 | Unused, but identical to 044 and 045, respectively | 047»; «050...077 | *nn | Extra-codes, used as system calls and math library functions».

> S3 §8: «When the emulator encounters opcode 002, 032, 033, 046, 047, or 0320, it throws a C++ Processor::Exception with the message "Illegal instruction …".»

> S6: «the cache БРЗ, the page registers РП, the protection register РЗ, the interrupt register ГРП (0237) and its mask МГРП (036)» — т.е. «036» здесь встречается как **адрес регистра МГРП внутри opcode 002**, а не как самостоятельный opcode 036.

## 4. Проверка гипотез

### Гипотеза A: «036 = втбрз (выбор/установка базового регистра?)»

**Прямо НЕ подтверждено: буквальная строка «втбрз» ни в одном из найденных источников не встречается** (поиск по «втбрз», «БЭСМ-6 втбрз», «втбрз базовый регистр 036» дал 0 результатов).

**Частично подтверждено в близкой форме.** Для **длинного** opcode 036 (э36/*36) S3 прямо указывает задокументированный в оригинальном руководстве побочный эффект **«flush BRZ»** — сброс/выталкивание БРЗ. БРЗ в терминологии БЭСМ-6 — это быстрый буфер/кэш (S6 называет его «the cache БРЗ»; по besm6.org БРЗ — 8 регистров; в вики — кэш на 16 48-битных слов). То есть «втбрз» наиболее правдоподобно читается как **«вытолкнуть/сбросить БРЗ»** — но это не «выбор/установка базового регистра», а сброс буфера. Одновременно сама команда работает как VZM (переход при ИР=0); в эмуляторе дополнительный эффект не моделируется.

Для **короткого** opcode 036 гипотеза **опровергается**: это СДА/ASN — сдвиг аккумулятора, никакого отношения к базовым регистрам или БРЗ не имеет.

**Итог по гипотезе A:** считать «036 = втбрз» недоказанным; максимально близкий факт — «long 036 (э36) = VZM + документированный flush BRZ». Если в коде/логике имеется в виду короткий 036 — это точно ASN (сдвиг).

### Гипотеза B: «020/021 = э20/э21»

**Подтверждено для длинного формата, с оговоркой.**
- S1: в таблице команд второго типа строки «20 э20» и «21 э21» отнесены к группе «экстракоды».
- S4: long-таблица даёт «Э20 020 extracode», «Э21 021 extracode».
- S3: 020 и 021 перечислены в разделе «Extracodes» как «Additional system call» (записаны как 0200/0210, т.е. со старым 4-разрядным представлением кода).
- S5: «long 020, 021, 036» названы среди opcode'ов, не имеющих собственной мнемоники.

**Что именно означают имена:** приставка «э» — это не особый мнемонический префикс, а способ записать команду **по её номеру** (от «экстракод» / «э-код»): у команды нет буквенной мнемоники, и ассемблер/автокод пишет её как «э» + номер opcode'а. S3: «Each assembler spells an extracode by its opcode rather than by a mnemonic… Madlen `,*74,`, Bemsh `э74`, `b6as` `$74`». S6: «Bemsh names them by their opcode: `э74` is extracode 074». По этой причине «э20» = «команда с кодом 20, не имеющая имени», а в длинном формате это действительно экстракод/системный вызов.

**Важная оговорка:** в **коротком** формате 020/021 — это не экстракоды, а совсем другие команды: СБР/APX и РЗБ/AUX (упаковка/распаковка битов). Если исходный код использует `э20`/`э21` в синтаксисе БЕМШ/Мадлен, нужно смотреть, какой формат cmdword получается; в long-кодировке это системные вызовы, в short — битовые операции.

### Дополнительно найденное (полезно для plan-f77)

- «э»-именование экстракодов (050–077) подтверждено для БЕМШ: `э74`, `э77` и т.п. (S3, S6). Экстракоды выполняются в пользовательском режиме, при выполнении `M[016] = EA`, ω становится логическим; системный вызов `$77 N` из Unix v7 использует именно этот механизм.
- 033 short (EXT) и 002 (MOD) — единственные две супервизорные инструкции; 033 long (STOP) — пользовательская.
- 046/047 как «незаконные» подтверждено S2/S3/S4/S5; S1 даёт альтернативную («экстракоды») трактовку 046 — расхождение между источниками зафиксировано, выбрать однозначно не удалось.

## 5. Что именно проверялось и что НЕ найдено

Проверено:
1. https://ru.wikipedia.org/wiki/БЭСМ-6 — нет таблицы opcode'ов (только общая характеристика: 50 команд по 24 бита, 48-битное слово, 15 индексных регистров, экстракоды как системные вызовы).
2. https://www.computer-museum.ru/histsoft/besm6.htm — 404, страница недоступна (в выдаче есть только английская версия https://www.computer-museum.ru/english/besm6.htm, справки по opcode'ам там нет).
3. https://www.besm6.org/wiki/CmdSheet.html — найдена и разобрана полностью (две таблицы).
4. https://www.mailcom.com/besm6/instset.shtml — найдена и разобрана полностью.
5. https://github.com/sergev/vcc/backend/besm6/*.md (Instruction Set, Bemsh, Unix Assembler, Intrinsics) — найдены и разобраны.
6. Web-поиск: «БЭСМ-6 система команд opcode 036 втбрз», «besm6 opcode table 020 021 033 036 046 047», «БЭСМ-6 "втбрз" команда», «"втбрз" БЭСМ-6 базовый регистр 036», «besm6 "flush BRZ" opcode 36 manual», «БЭСМ-6 БРЗ буфер регистров что такое кэш».

НЕ найдено:
- Прямого упоминания строки **«втбрз»** ни в одном источнике. Гипотеза «выбор/установка базового регистра» опровергнута; ближайший факт — «flush BRZ» у long-036 (э36).
- Авторитетного подтверждения, что 046 — рабочий экстракод: S1 называет его экстракодом, но S2/S3/S4/S5 единогласно считают 046/047 незаконными/неиспользуемыми. Расхождение не разрешено.
- Русскоязычного описания «э20/э21» как отдельной поименованной команды — найдено только общее правило «э + номер opcode'а» для экстракодов; long 020/021 описаны как «Additional system call» в S3.

## 6. Рекомендация спавнеру

1. **Формат уже установлен авторитетно:** бит 20 = 0 ⇒ SHORT (первый тип, `CmdSheet.md:17`); бит 20 = 1 ⇒ LONG (`CmdSheet.md:96`). Наши слова имеют бит 20 = 0.
2. `besm6tape.py:84` (`is_long = (h >> 19) & 1`) — off-by-one баг: проверяет бит 19 вместо бита 20 и даёт **ошибочный `is_long=1` из-за бита 19**. Прежний вывод «в нашем коде LONG» неверен.
3. К нашим словам применяются SHORT-значения: 020=`сбр`/`APX`, 021=`рзб`/`AUX`, 033=`увв`/`EXT`, 036=`сда`/`ASN` (сдвиг на N−64), 046/047=незаконные/не используемые (`disbesm6.c:61,62,72,75,83,84`). LONG-интерпретации («Additional system call», «flush BRZ», «стоп») к ним не применяются.
4. `втбрз` — имя подпрограммы `gens1.be`, а не мнемоника opcode.
