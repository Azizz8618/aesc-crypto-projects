# Бесплатный доступ к ИИ через агента: сравнительная таблица

Дата сбора: 25.11.2026. Сбор выполнен OSINT-методами проекта `privod-apparat`
(иерархия доступа curl → trafilatura → webfetch, Bing News через
`tools/bing_news.py`, отказ от фабрикации цитат, фиксация доступности источников).
Первичные источники — официальная документация провайдеров; каждый факт ниже
имеет номер ссылки из раздела 5. Вторичные данные помечены отдельно.

Документ дополняет [methodology.md](methodology.md) (раздел 4 «ИИ как инструмент
разработчика») и раздел оптимизации расходов `docs/cost-optimization.md`:
в нём собраны варианты, как подключить агента к модели без оплаты и где
находятся бесплатные лимиты.

## 1. Основная сравнительная таблица

| Провайдер / режим | Модель (ID) | Параметры модели | Контекст в бесплатном доступе | Бесплатная квота | Период обновления квоты | Доступ для агента | Источник |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Google Gemini API, Free | `gemini-4-hydrogen` | не раскрывается | 1 048 576 входных токенов; вывод до 1 М [1][4] | Вход, выход и кэширование — `Free of charge`; RPM/TPM/RPD устанавливаются проектом и видны в AI Studio [2][3] | RPD сбрасываются в 00:00 по тихоокеанскому времени; лимит — на проект, не на ключ [3] | Interactions API, function calling, Gemini CLI, agent skills [4][6] | [1][2][3][4][6] |
| Google Gemini API, Free | `gemini-3.8-flash` | не раскрывается | 1 048 576 входных / 65 536 выходных [4] | Вход и выход бесплатны; лимиты RPD/RPM/TPM динамические [2][3] | Ежедневно, 00:00 Pacific [3] | Function calling, computer use, file search, managed agents [2][4][6] | [2][3][4][6] |
| Google Gemini API, Free | `gemini-3.5-flash-lite` | не раскрывается | 1 048 576 входных / 65 536 выходных [5] | Вход и выход бесплатны; ориентирована на высокочастотные агентные задачи [2][5] | Ежедневно, 00:00 Pacific [3] | Function calling, Interactions API [5][6] | [2][3][5][6] |
| Google Gemini API, Free | `gemini-2.5-flash-lite` | не раскрывается | 1 М токенов [1][2] | Вход и выход бесплатны; 500 RPD на заземление Google Search [2] | Ежедневно, 00:00 Pacific [3] | Legacy-доступ; с 01.12.2026 запросы `gemini-2.5-flash` маршрутизируются в `gemini-3.5-flash-lite` [1] | [1][2][3] |
| Google Gemini Decisions API, Free | `gemini-decision-1` | не раскрывается | не приведено на странице лимитов | 200 RPM, 50 000 TPM, 10 000 RPD; 0 выходных токенов [3] | Ежедневно, 00:00 Pacific [3] | Специализированный API бинарных/категориальных решений [3] | [3] |
| Cerebras Cloud, Free Trial | `gpt-oss-120b` | 120 млрд [8] | 65 тыс. бесплатно (131 тыс. на платном tier) [8] | 5 RPM; 30 тыс. uncached TPM; 90 тыс. total TPM; 1 млн TPH и TPD; $5 стартовых кредитов [7] | Непрерывное пополнение по алгоритму token bucket; кредиты действуют 30 дней; постоянно бесплатного tier нет [7] | OpenAI-совместимый API [7] | [7][8] |
| Cerebras Cloud, Free Trial | `qwen-3.8-27b` | 27 млрд [8] | 64 тыс. бесплатно (128 тыс. на платном tier) [8] | 300 RPM; 150 тыс. uncached TPM; 750 тыс. total TPM; часы/сутки не ограничены; $5 кредитов [7] | Непрерывное пополнение; кредиты 30 дней [7] | OpenAI-совместимый API; поддержка изображений [7][8] | [7][8] |
| Cloudflare Workers AI, Free | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | 70 млрд, fp8 [10] | 24 000 токенов [10] | 10 000 Neurons в сутки на аккаунт (общая квота на все модели) [9] | Ежедневно [9] | Function calling: да; Workers AI binding, REST и AI Gateway [10] | [9][10] |
| Cohere, trial/evaluation key | `command-a` | 111 млрд [12] | 256 тыс. [12] | 1 000 вызовов API в месяц; 20 запросов в минуту [11] | Календарный месяц [11] | Нативная поддержка tool use и REACT-агентов [12] | [11][12] |
| Ollama, локально | `gemma3` (4b / 12b / 27b) | 4 / 12 / 27 млрд (есть 270M и 1B) [14] | 128 тыс.; у 270M и 1B — 32 тыс. [14] | Без квоты: модель запускается на собственном оборудовании [14] | Нет обновления квоты | `ollama launch opencode --model gemma3` и аналоги для Claude/Hermes [14] | [14] |
| Ollama, локально | `deepseek-r1:671b` | 671 млрд (доступны дистилляты, в том числе 8B) [15] | Задаётся локально, на странице модели не фиксировано [15] | Без квоты; требует значительных ресурсов [15] | Нет обновления квоты | Локальный OpenAI-совместимый сервер Ollama [15] | [15] |
| Ollama, локально | `qwen3` | Размеры семейства, включая 30B-A3B и 4B [13] | Задаётся локально | Без квоты [13] | Нет обновления квоты | `ollama launch opencode --model qwen3` [13] | [13] |

### 1.1. Что бесплатным не является

| Сервис | Факт | Источник |
| --- | --- | --- |
| Hugging Face Inference Providers | У free-аккаунта ежемесячных кредитов нет; PRO и Team/Enterprise получают $2 в месяц. Бесплатного tier для API нет | [16] |
| GitHub Models | Сервис полностью упразднён 30.07.2026: playground, каталог, inference API и BYOK недоступны | [17] |
| OpenAI API | Бесплатна только веб-версия ChatGPT; в таблице цен API указаны платные тарифы | [18] |
| Anthropic API | Бесплатный план есть у чата; API-кредиты указаны только для Max ($100/мес) и Enterprise (до $500/мес) | [19] |
| DeepSeek API | Бесплатного tier нет; модель `deepseek-flash` имеет контекст 1 М и платную тарификацию | [20] |
| Gemini 4 Carbon / Argon / Neon | В документации прямо указано: `not available on the Free tier` | [2] |

## 2. Источники, которые не удалось верифицировать в этой сессии

| Сервис | URL | Статус доступа | Что делать |
| --- | --- | --- | --- |
| Groq, rate limits | <https://console.groq.com/docs/rate-limits> | HTTP 403 через curl, webfetch и reader-прокси | Проверить из браузера/с других сетей; числовые лимиты не приводятся |
| OpenRouter, limits и каталог | <https://openrouter.ai/docs/api-reference/limits>, <https://openrouter.ai/api/v1/models> | HTTP 403 | Проверить список `:free` моделей и лимиты вручную |
| Mistral AI, platform limits | <https://docs.mistral.ai/getting-started/platform-limits/> | timeout / 404 | Уточнить актуальный URL документации |
| Cerebras FLARE-обход | локальный FlareSolverr :8191 | браузер не запустился в этой сессии | Использован прямой доступ к docs (успешно) |

Вторичный, не подтверждённый первичной документацией сигнал: Bing News
(запрос «Gemini 4 Hydrogen free API requests per day») вернул сниппет
<https://note.com/deep_orchid437/n/nbdc60fe4eedd?hl=en> с утверждением, что
бесплатный API ограничен примерно 20 вызовами в день. Официальная страница
лимитов отсылает к персональному кабинету AI Studio, поэтому число
рассматривается как ориентир, а не как подтверждённый факт. [21]

## 3. Практические выводы для проекта

1. Максимальный бесплатный контекст (1 М токенов) дают Gemini 4 Hydrogen,
   Gemini 3.8 Flash и Gemini 3.5 Flash-Lite; кэширование контекста в free tier
   бесплатно [2][4][5]. Это напрямую закрывает главную статью расхода
   `cost-optimization.md` (98,10 % Cache Read).
2. У Gemini лимиты считаются на проект, RPD сбрасываются в полночь Pacific;
   конкретные числа нужно снимать в AI Studio, а не фиксировать в документах
   проекта [3].
3. Если нужны предсказуемые числовые лимиты и OpenAI-совместимый endpoint —
   Cerebras Free Trial (`qwen-3.8-27b`: 300 RPM) или Cohere trial
   (1 000 вызовов/мес, 20 RPM) [7][11].
4. Если нужна полная независимость от квот — локальный Ollama;
   `ollama launch opencode --model ...` уже поддерживается страницами моделей,
   а Gemma 3 даёт 128K контекста [13][14].
5. Cloudflare Workers AI даёт 10 000 Neurons/сутки на все модели сразу, поэтому
   при обширном контексте квота расходуется быстро [9].
6. GitHub Models как бесплатный канал больше не существует [17]; Hugging Face,
   OpenAI, Anthropic и DeepSeek бесплатного API для агента не предоставляют
   [16][18][19][20].

## 4. Журнал доступности источников (OSINT-метод)

| Ресурс | Статус | Метод | Примечание |
| --- | --- | --- | --- |
| ai.google.dev (models, pricing, rate-limits) | 200 | curl + trafilatura | Полный текст документации |
| aistudio.google.com/docs/coding-agents.md | 200 | curl + trafilatura | Настройка агентов и MCP |
| inference-docs.cerebras.ai | 200 | webfetch | Таблицы лимитов и каталог моделей |
| developers.cloudflare.com | 200 | curl + trafilatura | Цены и карточки моделей |
| docs.cohere.com | 200 | webfetch | Лимиты trial-ключей, карточка Command A |
| ollama.com | 200 | curl + trafilatura | Карточки моделей и команды запуска |
| docs.github.com | 200 | webfetch | Уведомление об упразднении GitHub Models |
| openai.com, anthropic.com, api-docs.deepseek.com | 200 | curl + trafilatura | Тарифы и отсутствие free API |
| Bing News RSS (`tools/bing_news.py`) | 200 | OSINT-инструмент privod-apparat | 5–14 результатов на запрос; использован для вторичных сигналов |
| console.groq.com, openrouter.ai | 403 | curl, webfetch, прокси | Не верифицировано, см. раздел 2 |
| Yandex Search | 200 (SmartCaptcha) | curl | Сниппеты не получены |

## 5. Список источников

1. Gemini Models — <https://ai.google.dev/gemini-api/docs/models>
2. Gemini API pricing — <https://ai.google.dev/gemini-api/docs/pricing>
3. Gemini API rate limits — <https://ai.google.dev/gemini-api/docs/rate-limits>
4. Gemini 3.8 Flash — <https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash>
5. Gemini 3.5 Flash-Lite — <https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite>
6. Coding agent setup — <https://aistudio.google.com/docs/coding-agents.md>
7. Cerebras rate limits — <https://inference-docs.cerebras.ai/support/rate-limits>
8. Cerebras model catalog — <https://inference-docs.cerebras.ai/models/overview>
9. Cloudflare Workers AI pricing — <https://developers.cloudflare.com/workers-ai/platform/pricing/>
10. Cloudflare Llama 3.3 70B — <https://developers.cloudflare.com/workers-ai/models/llama-3.3-70b-instruct-fp8-fast/>
11. Cohere rate limits — <https://docs.cohere.com/docs/rate-limits>
12. Cohere Command A — <https://docs.cohere.com/v2/docs/command-a>
13. Ollama Qwen3 — <https://ollama.com/library/qwen3>
14. Ollama Gemma 3 — <https://ollama.com/library/gemma3>
15. Ollama DeepSeek R1 — <https://ollama.com/library/deepseek-r1>
16. Hugging Face Inference Providers pricing — <https://huggingface.co/docs/inference-providers/pricing>
17. GitHub Models (retired) — <https://docs.github.com/en/github-models>
18. OpenAI API pricing — <https://openai.com/api/pricing/>
19. Anthropic pricing — <https://www.anthropic.com/pricing>
20. DeepSeek pricing — <https://api-docs.deepseek.com/quick_start/pricing>
21. Bing News, запрос «Gemini 4 Hydrogen free API requests per day» — вторичный источник
22. Groq rate limits — <https://console.groq.com/docs/rate-limits> (403)
23. OpenRouter limits — <https://openrouter.ai/docs/api-reference/limits> (403)
24. Mistral platform limits — <https://docs.mistral.ai/getting-started/platform-limits/> (недоступно)

## 6. Ограничения

- Числа квот приведены по состоянию на 25.11.2026 и могут меняться без
  уведомления; Gemini явно не гарантирует заявленные лимиты [3].
- Параметры закрытых моделей Gemini не публикуются, поэтому в таблице указано
  «не раскрывается», а не оценочное значение.
- Для Groq, OpenRouter и Mistral данные не получены: в таблицу включены только
  проверенные факты, недоступные источники вынесены в раздел 2.
- Экономия контекста не отменяет контроль результата: каждый фрагмент,
  предложенный ИИ, проверяется по исходникам, прогону и побайтовой сверке
  согласно [methodology.md](methodology.md), раздел 4.
