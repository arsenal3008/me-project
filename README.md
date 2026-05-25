# agent_checker

Tkinter-GUI для проверки доступности моделей у OpenAI-совместимых
провайдеров и экспорта рабочих в `opencode.jsonc`.

## Запуск

```bash
python agent_checker.py
# или
python -m agent_checker
```

Зависимости опциональны (см. `requirements.txt`). По умолчанию хватает
stdlib Python 3.7+.

## Структура

```
agent_checker/
  __init__.py          — версия пакета
  __main__.py          — точка входа `python -m agent_checker`
  jsonc.py             — парсер JSON с // и /* */ комментариями
  paths.py             — кросс-платформенные пути конфигов и логов
  settings.py          — load/save пользовательских настроек
  providers.py         — загрузка/слияние/сохранение провайдеров
  http_client.py       — HTTP, кэш ключей, validate_keys, test_model
  exporter.py          — чистая сборка JSONC (без UI)
  ollama_manager.py    — автозапуск Ollama (кросс-платформенный)
  ui/
    app.py             — главное окно
    theme.py           — тёмная/светлая тема
    export_dialog.py   — диалог экспорта
tests/                 — unittest, запуск: `python -m unittest discover`
agent_checker.py       — тонкий entry-point, дёргает agent_checker.ui.app.main
```

## Тесты

```bash
python -m unittest discover -s tests
```

Тесты покрывают чистую логику (jsonc, settings, paths, providers,
http_client, exporter). UI не требует tkinter для запуска тестов.

## Кросс-платформенность

- Ollama ищется через `$OLLAMA_BIN` → `PATH` → системные каталоги.
- Конфиг opencode ищется через `$OPENCODE_CONFIG` → `~/.config/opencode/`
  → `%APPDATA%/opencode/` (Win) → рядом со скриптом.
- Скрытие окон Ollama — no-op на не-Windows.

## Что было исправлено

- `tagS=tag` → `tag` (рабочее цветовое выделение в логе);
- `p['models'][0]` → `next(iter(p['models']))` (dict, не list);
- сброс `self.running` в `finally`;
- кэш валидных ключей сбрасывается при смене URL/ключа;
- порт TCP-проверки выводится из схемы (`80/443`), а не `11434`;
- хардкод `C:\Users\msi\...` заменён на `shutil.which` + env;
- сборка JSONC через `json.dumps` (раньше — небезопасная конкатенация).
