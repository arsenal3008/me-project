#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgentChecker 3.0 — современное GUI-приложение для проверки доступности AI-моделей.

Возможности:
    • Загрузка провайдеров и моделей из opencode.jsonc / opencode.json
    • Проверка доступности моделей (многопоточно, с ретраями)
    • Управление API-ключами и URL провайдеров (с маскировкой ключей)
    • Экспорт рабочих моделей обратно в opencode.jsonc + экспорт результатов в JSON/CSV
    • Современный интерфейс с вкладками (Дашборд / Модели / Провайдеры / Лог / Настройки)
    • Светлая и тёмная темы

Безопасность:
    • Проверка TLS-сертификатов ВКЛЮЧЕНА по умолчанию (можно отключить только осознанно)
    • API-ключи маскируются в логах
    • Файл providers.json сохраняется с правами 0600 (только владелец)

Требуется Python 3.7+. Зависимость `requests` опциональна (есть fallback на urllib).
"""

from __future__ import annotations

import json
import os
import socket
import ssl
import sys
import threading
import time
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlparse

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# ── Опциональный backend requests ──────────────────────────────────
try:
    import requests  # type: ignore
    _HAS_REQUESTS = True
except ImportError:
    requests = None  # type: ignore
    _HAS_REQUESTS = False

# ── Пути ───────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_JSON = os.path.join(SCRIPT_DIR, "providers.json")
SETTINGS_JSON = os.path.join(SCRIPT_DIR, "settings.json")
LOGS_DIR = os.path.join(SCRIPT_DIR, "logs")

APP_VERSION = "3.0"

# Возможные расположения конфига opencode (кроссплатформенно)
OPENCODE_CONFIG_CANDIDATES = [
    os.path.expanduser("~/.config/opencode/opencode.jsonc"),
    os.path.expanduser("~/.config/opencode/opencode.json"),
    os.path.join(os.environ.get("APPDATA", ""), "opencode", "opencode.jsonc"),
    os.path.join(os.environ.get("APPDATA", ""), "opencode", "opencode.json"),
]

ERR_DESC = {
    400: "Неизвестная модель",
    401: "Неверный API-ключ",
    403: "Доступ запрещён (Cloudflare?)",
    429: "Превышен лимит запросов",
    500: "Внутренняя ошибка сервера",
    502: "Шлюз недоступен",
    503: "Провайдер не отвечает",
}

ERR_TRANSLATE = {
    "daily successful request limit exceeded": "превышен дневной лимит запросов",
    "rate limit exceeded": "превышен лимит запросов",
    "too many requests": "слишком много запросов",
    "model not found": "модель не найдена",
    "unknown model": "неизвестная модель",
    "server error": "ошибка сервера",
    "service unavailable": "сервис недоступен",
}

# Кеш валидных ключей: {base_url: [key, ...]}
VALID_KEYS_CACHE: dict = {}
VALID_KEYS_LOCK = threading.Lock()


# ════════════════════════════════════════════════════════════════════
#  Утилиты
# ════════════════════════════════════════════════════════════════════
def mask_key(key: str) -> str:
    """Маскирует API-ключ для безопасного вывода в лог: sk-…wxyz."""
    if not key:
        return "(пусто)"
    if len(key) <= 8:
        return key[:2] + "…"
    return "%s…%s" % (key[:4], key[-4:])


def _plural(n: int, forms) -> str:
    n = abs(n) % 100
    if 10 < n < 20:
        return forms[2]
    n %= 10
    if n == 1:
        return forms[0]
    if 1 < n < 5:
        return forms[1]
    return forms[2]


def key_fmt(n: int, total=None) -> str:
    word = _plural(total if total is not None else n, ("ключ", "ключа", "ключей"))
    if total is not None:
        return "%d из %d %s" % (n, total, word)
    return "%d %s" % (n, word)


def read_jsonc(path: str) -> dict:
    """Читает JSONC (JSON с // и /* */ комментариями)."""
    with open(path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    return json.loads(_strip_jsonc(text))


def _strip_jsonc(text: str) -> str:
    """Удаляет // и /* */ комментарии вне строк."""
    out = []
    i, n = 0, len(text)
    in_str = False
    in_line_comment = False
    in_block_comment = False
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                out.append(ch)
            i += 1
            continue
        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue
        if in_str:
            out.append(ch)
            if ch == "\\" and nxt:
                out.append(nxt)
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        # вне строки и комментариев
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def save_json_secure(path: str, data: dict) -> None:
    """Сохраняет JSON и выставляет права 0600 (только владелец) — для файлов с ключами."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass  # Windows / неподдерживаемая ФС


# ════════════════════════════════════════════════════════════════════
#  Сетевой слой (TLS-проверка включена по умолчанию)
# ════════════════════════════════════════════════════════════════════
def _ssl_context(verify: bool) -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if not verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def http_post(url, body, headers, timeout=20, verify=True):
    """POST JSON. body — dict. Возвращает (status_code, response_text)."""
    if _HAS_REQUESTS:
        r = requests.post(url, json=body, headers=headers, timeout=timeout, verify=verify)
        return r.status_code, r.text
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    ctx = _ssl_context(verify)
    try:
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        body_text = resp.read().decode("utf-8", errors="replace")
        return resp.getcode(), body_text
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body_text


def validate_keys(base_url, all_keys, provider_models=None, provider_name="",
                  timeout=10, verify=True, log=print):
    """Возвращает список рабочих ключей (или один первый рабочий)."""
    url = base_url.rstrip("/") + "/chat/completions"
    tag = provider_name or url
    provider_models = provider_models or {}
    first_mid = next(iter(provider_models)) if provider_models else "gpt-4o-mini"
    for k in all_keys:
        if not k:
            continue
        body = {"model": first_mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}
        headers = {"Authorization": "Bearer %s" % k, "Content-Type": "application/json"}
        try:
            code, text = http_post(url, body, headers, timeout=timeout, verify=verify)
        except Exception as e:
            log("[%s] %s -> ошибка сети: %s" % (tag, mask_key(k), str(e)[:60]))
            continue
        if code == 200:
            log("[%s] %s -> HTTP 200 (ключ работает)" % (tag, mask_key(k)))
            return [k]
        try:
            err_data = json.loads(text)
            err_msg = (err_data.get("error", {}) or err_data).get("message", "") or ""
        except Exception:
            err_msg = text[:120]
        if code in (401, 403):
            low = err_msg.lower()
            if "model" in low and ("support" in low or "not found" in low or "not exist" in low):
                log("[%s] %s -> HTTP %d: модель не найдена, ключ работает" % (tag, mask_key(k), code))
                return [k]
            log("[%s] %s -> HTTP %d: ключ НЕВЕРНЫЙ (%s)" % (tag, mask_key(k), code, err_msg[:60]))
            continue
        # прочие коды считаем «ключ рабочий, проблема на стороне модели/лимита»
        for eng, rus in ERR_TRANSLATE.items():
            if eng in err_msg.lower():
                err_msg = rus
                break
        log("[%s] %s -> HTTP %d: %s (ключ считается рабочим)" % (tag, mask_key(k), code, err_msg[:80]))
        return [k]
    log("[%s] валидных ключей не найдено (проверено %d)" % (tag, len(all_keys)))
    return []


def test_model(base_url, api_keys, model_id, timeout=20, retries=2, verify=True, log=print):
    """Проверяет модель, используя кешированные валидные ключи. -> (ok, msg, elapsed)."""
    start = time.time()
    if not api_keys:
        return False, "Нет API-ключей", 0.0
    cache_key = base_url.rstrip("/")
    with VALID_KEYS_LOCK:
        valid = VALID_KEYS_CACHE.get(cache_key)
        if valid is None:
            valid = validate_keys(base_url, api_keys, timeout=10, verify=verify, log=log)
            VALID_KEYS_CACHE[cache_key] = valid
    if not valid:
        return False, "Ни один ключ не прошёл проверку", round(time.time() - start, 2)

    url = base_url.rstrip("/") + "/chat/completions"
    for key_idx, api_key in enumerate(valid):
        body = {"model": model_id, "messages": [{"role": "user", "content": "say ok"}], "max_tokens": 5}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + api_key,
        }
        try:
            for attempt in range(retries + 1):
                code, text = http_post(url, body, headers, timeout=timeout, verify=verify)
                elapsed = round(time.time() - start, 2)
                if code == 429 and attempt < retries:
                    time.sleep(3 * (attempt + 1))
                    continue
                if code != 200 and key_idx < len(valid) - 1:
                    break  # пробуем следующий ключ
                try:
                    data = json.loads(text)
                except Exception:
                    raw = text.strip()[:120]
                    if raw:
                        return False, raw, elapsed
                    reason = "Cloudflare/блокировка" if code == 403 else "пустой ответ"
                    return False, "HTTP %d: %s" % (code, reason), elapsed
                if code == 200 and data.get("choices"):
                    content = (data["choices"][0].get("message", {}) or {}).get("content", "") or ""
                    return True, content.strip()[:80], elapsed
                err = (data.get("error", {}) or {}).get("message", "")
                desc = ERR_DESC.get(code)
                tag = "RATE" if code == 429 else "HTTP %d" % code
                return False, "%s: %s" % (tag, desc or err or ""), elapsed
        except Exception as e:
            if key_idx < len(valid) - 1:
                continue
            return False, "Ошибка соединения: %s" % str(e)[:60], round(time.time() - start, 2)
    return False, "Все ключи не подошли", round(time.time() - start, 2)


# ════════════════════════════════════════════════════════════════════
#  Палитра тем
# ════════════════════════════════════════════════════════════════════
LIGHT = {
    "bg": "#f4f6fb", "panel": "#ffffff", "card": "#ffffff", "fg": "#1f2933",
    "muted": "#6b7280", "border": "#e2e8f0", "accent": "#3b6cf6", "accent_fg": "#ffffff",
    "ok": "#16a34a", "fail": "#dc2626", "warn": "#d97706", "untested": "#94a3b8",
    "tree_bg": "#ffffff", "tree_alt": "#f1f5f9", "sel": "#dbe5ff", "sel_fg": "#1f2933",
    "log_bg": "#ffffff", "log_fg": "#1f2933", "tab_active": "#3b6cf6",
}
DARK = {
    "bg": "#11151c", "panel": "#1a202c", "card": "#1e2631", "fg": "#e6edf3",
    "muted": "#9aa6b2", "border": "#2d3543", "accent": "#4f8cff", "accent_fg": "#ffffff",
    "ok": "#3fb950", "fail": "#f85149", "warn": "#d29922", "untested": "#6e7681",
    "tree_bg": "#161b22", "tree_alt": "#1b212b", "sel": "#1f3a5f", "sel_fg": "#ffffff",
    "log_bg": "#0d1117", "log_fg": "#e6edf3", "tab_active": "#4f8cff",
}


# ════════════════════════════════════════════════════════════════════
#  Приложение
# ════════════════════════════════════════════════════════════════════
class AgentCheckerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AgentChecker %s — проверка AI-моделей" % APP_VERSION)
        self.root.geometry("1080x740")
        self.root.minsize(900, 600)

        # ── состояние ──
        self.timeout_val = tk.IntVar(value=20)
        self.retries_val = tk.IntVar(value=2)
        self.delay_val = tk.DoubleVar(value=0.3)
        self.dark_mode = tk.BooleanVar(value=True)
        self.verify_ssl = tk.BooleanVar(value=True)
        self.auto_save_config = tk.BooleanVar(value=False)
        self.geometry_val = tk.StringVar(value="1080x740")

        self.filter_provider = tk.StringVar(value="all")
        self.filter_status = tk.StringVar(value="all")
        self.filter_source = tk.StringVar(value="all")
        self.filter_free = tk.StringVar(value="all")
        self.search_var = tk.StringVar(value="")

        self.providers: dict = {}   # {name: {base_url, api_key, api_keys, models:{id:{name,source,free}}}}
        self.results: dict = {}     # {provider: {model_id: {ok,msg,elapsed}}}
        self.model_list: list = []  # [(provider, model_id, model_name, source, free)]
        self.running = False
        self.cancel_flag = False
        self.sort_col = None
        self.sort_rev = False
        self.log_file = None

        self.pal = DARK
        self._init_log_file()
        self._build_ui()
        self._load_settings()
        self.pal = DARK if self.dark_mode.get() else LIGHT
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._load_providers()
        self._rebuild_provider_filter()
        self._apply_theme()
        self._refresh_table()
        self._auto_validate_keys()

    # ════════════════════════════════════════════════════════════════
    #  Построение интерфейса
    # ════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self.style = ttk.Style()
        self._build_header()
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 8))
        self.tab_dash = ttk.Frame(self.nb)
        self.tab_models = ttk.Frame(self.nb)
        self.tab_providers = ttk.Frame(self.nb)
        self.tab_log = ttk.Frame(self.nb)
        self.tab_settings = ttk.Frame(self.nb)
        self.nb.add(self.tab_dash, text="  📊  Дашборд  ")
        self.nb.add(self.tab_models, text="  🧠  Модели  ")
        self.nb.add(self.tab_providers, text="  🔑  Провайдеры  ")
        self.nb.add(self.tab_log, text="  📜  Лог  ")
        self.nb.add(self.tab_settings, text="  ⚙  Настройки  ")
        self._build_dashboard()
        self._build_models_tab()
        self._build_providers_tab()
        self._build_log_tab()
        self._build_settings_tab()
        self._build_statusbar()

    def _build_header(self):
        self.header = tk.Frame(self.root, height=64)
        self.header.pack(side=tk.TOP, fill=tk.X)
        self.header.pack_propagate(False)
        self.title_lbl = tk.Label(self.header, text="🤖  AgentChecker",
                                  font=("Segoe UI", 17, "bold"))
        self.title_lbl.pack(side=tk.LEFT, padx=18)
        self.subtitle_lbl = tk.Label(self.header, text="проверка доступности AI-моделей",
                                     font=("Segoe UI", 10))
        self.subtitle_lbl.pack(side=tk.LEFT, padx=(0, 10), pady=(6, 0))

        btns = tk.Frame(self.header)
        btns.pack(side=tk.RIGHT, padx=14)
        self.btn_all = ttk.Button(btns, text="▶  Проверить все", style="Accent.TButton",
                                  command=self._start_all)
        self.btn_all.pack(side=tk.LEFT, padx=3)
        self.btn_sel = ttk.Button(btns, text="▶  Выбранные", command=self._start_selected)
        self.btn_sel.pack(side=tk.LEFT, padx=3)
        self.btn_stop = ttk.Button(btns, text="■  Стоп", command=self._stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=3)
        self.theme_btn = ttk.Button(btns, text="🌗", width=3, command=self._toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=(10, 0))

    # ── Дашборд ──
    def _build_dashboard(self):
        wrap = ttk.Frame(self.tab_dash, padding=18)
        wrap.pack(fill=tk.BOTH, expand=True)

        cards = ttk.Frame(wrap)
        cards.pack(fill=tk.X)
        self.card_defs = [
            ("total", "Всего моделей", "fg"),
            ("ok", "Работает", "ok"),
            ("fail", "Не работает", "fail"),
            ("untested", "Не проверено", "untested"),
        ]
        self.card_value_lbls = {}
        self.card_frames = {}
        self.card_title_lbls = {}
        for i, (key, title, _color) in enumerate(self.card_defs):
            card = tk.Frame(cards, bd=0, highlightthickness=1)
            card.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)
            val = tk.Label(card, text="0", font=("Segoe UI", 30, "bold"))
            val.pack(anchor="w", padx=16, pady=(14, 0))
            ttl = tk.Label(card, text=title, font=("Segoe UI", 10))
            ttl.pack(anchor="w", padx=16, pady=(0, 14))
            self.card_value_lbls[key] = val
            self.card_frames[key] = card
            self.card_title_lbls[key] = ttl

        # Прогресс + быстрые действия
        prog_box = ttk.LabelFrame(wrap, text="Прогресс проверки", padding=14)
        prog_box.pack(fill=tk.X, pady=(18, 8))
        self.dash_progress = ttk.Progressbar(prog_box, mode="determinate")
        self.dash_progress.pack(fill=tk.X)
        self.dash_prog_lbl = ttk.Label(prog_box, text="Готов к проверке")
        self.dash_prog_lbl.pack(anchor="w", pady=(8, 0))

        actions = ttk.LabelFrame(wrap, text="Быстрые действия", padding=14)
        actions.pack(fill=tk.X, pady=8)
        ttk.Button(actions, text="📂  Загрузить opencode.jsonc",
                   command=self._load_opencode_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="📤  Экспорт в opencode.jsonc",
                   command=self._export_dialog).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="💾  Экспорт результатов",
                   command=self._export_results).pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="🔄  Перечитать конфиг",
                   command=self._reload_config).pack(side=tk.LEFT, padx=4)

        self.dash_hint = ttk.Label(
            wrap, foreground=self.pal["muted"],
            text="Совет: двойной клик по модели копирует её ID. Правый клик — контекстное меню.")
        self.dash_hint.pack(anchor="w", pady=(14, 0))

    # ── Вкладка «Модели» ──
    def _build_models_tab(self):
        wrap = ttk.Frame(self.tab_models, padding=10)
        wrap.pack(fill=tk.BOTH, expand=True)

        bar = ttk.Frame(wrap)
        bar.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(bar, text="Провайдер:").pack(side=tk.LEFT)
        self.provider_combo = ttk.Combobox(bar, textvariable=self.filter_provider,
                                            state="readonly", values=["all"], width=16)
        self.provider_combo.pack(side=tk.LEFT, padx=(4, 12))
        self.provider_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_table())
        ttk.Label(bar, text="Статус:").pack(side=tk.LEFT)
        ttk.Combobox(bar, textvariable=self.filter_status, state="readonly", width=10,
                     values=["all", "yes", "no", "untested"]).pack(side=tk.LEFT, padx=(4, 12))
        self.filter_status.trace_add("write", lambda *a: self._refresh_table())
        ttk.Label(bar, text="Источник:").pack(side=tk.LEFT)
        ttk.Combobox(bar, textvariable=self.filter_source, state="readonly", width=10,
                     values=["all", "opencode", "custom"]).pack(side=tk.LEFT, padx=(4, 12))
        self.filter_source.trace_add("write", lambda *a: self._refresh_table())
        ttk.Label(bar, text="🔍").pack(side=tk.LEFT)
        search = ttk.Entry(bar, textvariable=self.search_var, width=22)
        search.pack(side=tk.LEFT, padx=4)
        self.search_var.trace_add("write", lambda *a: self._refresh_table())
        ttk.Button(bar, text="＋ Модель", command=self._add_custom_model).pack(side=tk.RIGHT, padx=2)

        tf = ttk.Frame(wrap)
        tf.pack(fill=tk.BOTH, expand=True)
        cols = ("provider", "model", "id", "source", "status", "response", "time")
        self.cols = [("provider", 120, "Провайдер"), ("model", 220, "Модель"),
                     ("id", 200, "ID модели"), ("source", 80, "Источник"),
                     ("status", 90, "Статус"), ("response", 240, "Ответ"), ("time", 70, "Время")]
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="extended")
        for c, w, h in self.cols:
            self.tree.heading(c, text=h, command=lambda col=c: self._sort_by(col))
            self.tree.column(c, width=w, minwidth=50)
        vsb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tf, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.grid_rowconfigure(0, weight=1)
        tf.grid_columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Button-3>", self._on_right_click)

    # ── Вкладка «Провайдеры» ──
    def _build_providers_tab(self):
        wrap = ttk.Frame(self.tab_providers, padding=10)
        wrap.pack(fill=tk.BOTH, expand=True)
        top = ttk.Frame(wrap)
        top.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(top, text="Провайдеры, URL и API-ключи",
                  font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        ttk.Button(top, text="💾 Сохранить", style="Accent.TButton",
                   command=self._save_providers_ui).pack(side=tk.RIGHT, padx=2)

        cv = tk.Canvas(wrap, highlightthickness=0)
        sb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=cv.yview)
        self.prov_frame = ttk.Frame(cv)
        self.prov_frame.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        self._prov_window = cv.create_window((0, 0), window=self.prov_frame, anchor="nw")
        cv.bind("<Configure>", lambda e: cv.itemconfigure(self._prov_window, width=e.width))
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._prov_canvas = cv
        self.prov_entries = {}

    def _render_providers(self):
        for w in self.prov_frame.winfo_children():
            w.destroy()
        self.prov_entries = {}
        if not self.providers:
            ttk.Label(self.prov_frame,
                      text="Нет провайдеров. Загрузите opencode.jsonc на вкладке «Дашборд».",
                      foreground=self.pal["muted"]).pack(anchor="w", padx=8, pady=12)
            return
        for pn in sorted(self.providers.keys()):
            p = self.providers[pn]
            box = ttk.LabelFrame(self.prov_frame,
                                 text="%s  (%d моделей)" % (pn, len(p.get("models", {}))),
                                 padding=10)
            box.pack(fill=tk.X, padx=6, pady=6)
            ttk.Label(box, text="URL:").grid(row=0, column=0, sticky="w")
            uv = tk.StringVar(value=p.get("base_url", ""))
            ttk.Entry(box, textvariable=uv, width=70).grid(row=0, column=1, columnspan=3, sticky="ew", padx=6, pady=2)

            ttk.Label(box, text="Ключи:").grid(row=1, column=0, sticky="w")
            keys = p.get("api_keys", [])
            kv = tk.StringVar(value=keys[0] if keys else "")
            combo = ttk.Combobox(box, textvariable=kv, values=[mask_key(k) for k in keys],
                                 state="readonly", width=40)
            combo.grid(row=1, column=1, sticky="ew", padx=6, pady=2)
            # Реальные ключи храним рядом со списком
            combo._real_keys = list(keys)  # type: ignore

            new_var = tk.StringVar()
            entry = ttk.Entry(box, textvariable=new_var, width=30, show="*")
            entry.grid(row=2, column=1, sticky="ew", padx=6, pady=2)
            show_var = tk.BooleanVar()
            ttk.Checkbutton(box, text="Показать", variable=show_var,
                            command=lambda e=entry, v=show_var: e.configure(show="" if v.get() else "*")
                            ).grid(row=2, column=2, sticky="w")

            def add_key(c=combo, nv=new_var, en=entry):
                k = nv.get().strip()
                if k and k not in c._real_keys:
                    c._real_keys.append(k)
                    c["values"] = [mask_key(x) for x in c._real_keys]
                    c.current(len(c._real_keys) - 1)
                    nv.set("")
                    en.delete(0, tk.END)

            def del_key(c=combo):
                idx = c.current()
                if 0 <= idx < len(c._real_keys):
                    c._real_keys.pop(idx)
                    c["values"] = [mask_key(x) for x in c._real_keys]
                    c.current(0) if c._real_keys else c.set("")

            ttk.Button(box, text="＋", width=3, command=add_key).grid(row=2, column=3, padx=2)
            ttk.Button(box, text="－", width=3, command=del_key).grid(row=1, column=3, padx=2)
            ttk.Button(box, text="Проверить ключи",
                       command=lambda name=pn, c=combo, u=uv: self._test_provider_keys(name, c, u)
                       ).grid(row=3, column=1, sticky="w", padx=6, pady=(6, 0))
            box.grid_columnconfigure(1, weight=1)
            self.prov_entries[pn] = (uv, combo)

    # ── Вкладка «Лог» ──
    def _build_log_tab(self):
        wrap = ttk.Frame(self.tab_log, padding=10)
        wrap.pack(fill=tk.BOTH, expand=True)
        bar = ttk.Frame(wrap)
        bar.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(bar, text="🧹 Очистить", command=self._clear_log).pack(side=tk.LEFT)
        ttk.Button(bar, text="📁 Логи на диске", command=self._show_log_browser).pack(side=tk.LEFT, padx=6)
        self.log = tk.Text(wrap, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10), bd=0)
        lsb = ttk.Scrollbar(wrap, command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lsb.pack(side=tk.RIGHT, fill=tk.Y)

    # ── Вкладка «Настройки» ──
    def _build_settings_tab(self):
        wrap = ttk.Frame(self.tab_settings, padding=18)
        wrap.pack(fill=tk.BOTH, expand=True)

        net = ttk.LabelFrame(wrap, text="Сеть и проверка", padding=14)
        net.pack(fill=tk.X, pady=6)
        ttk.Label(net, text="Таймаут (сек):").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Spinbox(net, from_=5, to=120, textvariable=self.timeout_val, width=8).grid(row=0, column=1, sticky="w", padx=8)
        ttk.Label(net, text="Повторов:").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Spinbox(net, from_=0, to=5, textvariable=self.retries_val, width=8).grid(row=1, column=1, sticky="w", padx=8)
        ttk.Label(net, text="Задержка (сек):").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Spinbox(net, from_=0.0, to=5.0, increment=0.1, textvariable=self.delay_val, width=8).grid(row=2, column=1, sticky="w", padx=8)

        sec = ttk.LabelFrame(wrap, text="Безопасность", padding=14)
        sec.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(sec, text="Проверять TLS-сертификаты (рекомендуется)",
                        variable=self.verify_ssl, command=self._on_verify_toggle).pack(anchor="w")
        ttk.Label(sec, foreground=self.pal["muted"],
                  text="Отключайте только для localhost / самоподписанных сертификатов. "
                       "Без проверки ключи можно перехватить.").pack(anchor="w", pady=(2, 0))

        misc = ttk.LabelFrame(wrap, text="Прочее", padding=14)
        misc.pack(fill=tk.X, pady=6)
        ttk.Checkbutton(misc, text="Тёмная тема", variable=self.dark_mode,
                        command=self._toggle_theme).pack(anchor="w")
        ttk.Checkbutton(misc, text="Авто-сохранение рабочих ключей в opencode.jsonc",
                        variable=self.auto_save_config, command=self._save_settings).pack(anchor="w")

        ttk.Button(wrap, text="💾 Сохранить настройки", style="Accent.TButton",
                   command=self._save_settings).pack(anchor="w", pady=10)
        ttk.Button(wrap, text="ℹ О программе", command=self._about).pack(anchor="w")

    def _build_statusbar(self):
        self.statusbar = tk.Label(self.root, text="Готов", anchor="w", bd=0, padx=12)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ════════════════════════════════════════════════════════════════
    #  Тема
    # ════════════════════════════════════════════════════════════════
    def _toggle_theme(self):
        self.pal = DARK if self.dark_mode.get() else LIGHT
        self._apply_theme()
        self._refresh_table()
        self._save_settings()

    def _on_verify_toggle(self):
        if not self.verify_ssl.get():
            if not messagebox.askyesno(
                    "Отключить проверку TLS?",
                    "Без проверки сертификатов ваши API-ключи можно перехватить (MITM).\n\n"
                    "Отключать только для localhost. Продолжить?"):
                self.verify_ssl.set(True)
                return
        with VALID_KEYS_LOCK:
            VALID_KEYS_CACHE.clear()
        self._save_settings()

    def _apply_theme(self):
        p = self.pal
        s = self.style
        s.theme_use("clam")
        s.configure(".", background=p["bg"], foreground=p["fg"], fieldbackground=p["panel"],
                    bordercolor=p["border"], troughcolor=p["border"], arrowcolor=p["fg"])
        s.configure("TFrame", background=p["bg"])
        s.configure("TLabel", background=p["bg"], foreground=p["fg"])
        s.configure("TLabelframe", background=p["bg"], foreground=p["fg"], bordercolor=p["border"])
        s.configure("TLabelframe.Label", background=p["bg"], foreground=p["muted"])
        s.configure("TButton", background=p["panel"], foreground=p["fg"], bordercolor=p["border"],
                    focuscolor=p["accent"], padding=6)
        s.map("TButton", background=[("active", p["sel"])])
        s.configure("Accent.TButton", background=p["accent"], foreground=p["accent_fg"],
                    font=("Segoe UI", 9, "bold"), padding=6)
        s.map("Accent.TButton", background=[("active", p["tab_active"])])
        s.configure("TEntry", fieldbackground=p["panel"], foreground=p["fg"])
        s.configure("TSpinbox", fieldbackground=p["panel"], foreground=p["fg"], arrowcolor=p["fg"])
        s.configure("TCombobox", fieldbackground=p["panel"], foreground=p["fg"], arrowcolor=p["fg"])
        s.map("TCombobox", fieldbackground=[("readonly", p["panel"])], foreground=[("readonly", p["fg"])])
        s.configure("TCheckbutton", background=p["bg"], foreground=p["fg"])
        s.map("TCheckbutton", background=[("active", p["bg"])])
        # Notebook
        s.configure("TNotebook", background=p["bg"], bordercolor=p["border"], tabmargins=(4, 6, 4, 0))
        s.configure("TNotebook.Tab", background=p["panel"], foreground=p["muted"],
                    padding=(14, 8), font=("Segoe UI", 10))
        s.map("TNotebook.Tab",
              background=[("selected", p["accent"])],
              foreground=[("selected", p["accent_fg"])])
        # Treeview
        s.configure("Treeview", background=p["tree_bg"], fieldbackground=p["tree_bg"],
                    foreground=p["fg"], rowheight=26, borderwidth=0)
        s.configure("Treeview.Heading", background=p["panel"], foreground=p["fg"],
                    font=("Segoe UI", 9, "bold"))
        s.map("Treeview", background=[("selected", p["sel"])], foreground=[("selected", p["sel_fg"])])
        s.configure("TProgressbar", background=p["accent"], troughcolor=p["border"])

        # «Сырые» tk-виджеты
        self.root.configure(bg=p["bg"])
        self.header.configure(bg=p["panel"])
        self.title_lbl.configure(bg=p["panel"], fg=p["fg"])
        self.subtitle_lbl.configure(bg=p["panel"], fg=p["muted"])
        for w in self.header.winfo_children():
            if isinstance(w, tk.Frame):
                w.configure(bg=p["panel"])
        self.statusbar.configure(bg=p["panel"], fg=p["muted"])
        self.log.configure(bg=p["log_bg"], fg=p["log_fg"], insertbackground=p["fg"],
                           selectbackground=p["sel"])
        self.log.tag_config("info", foreground=p["fg"])
        self.log.tag_config("success", foreground=p["ok"])
        self.log.tag_config("warn", foreground=p["warn"])
        self.log.tag_config("error", foreground=p["fail"])

        # Карточки дашборда
        color_map = {"fg": p["fg"], "ok": p["ok"], "fail": p["fail"], "untested": p["untested"]}
        for key, _title, color in self.card_defs:
            self.card_frames[key].configure(bg=p["card"], highlightbackground=p["border"],
                                            highlightcolor=p["border"])
            self.card_value_lbls[key].configure(bg=p["card"], fg=color_map[color])
            self.card_title_lbls[key].configure(bg=p["card"], fg=p["muted"])
        if hasattr(self, "dash_hint"):
            self.dash_hint.configure(foreground=p["muted"])

        # Цвета строк таблицы
        self.tree.tag_configure("ok", foreground=p["ok"])
        self.tree.tag_configure("fail", foreground=p["fail"])
        self.tree.tag_configure("untested", foreground=p["untested"])
        self.tree.tag_configure("odd", background=p["tree_alt"])
        self.tree.tag_configure("even", background=p["tree_bg"])
        if hasattr(self, "prov_frame"):
            self._render_providers()

    # ════════════════════════════════════════════════════════════════
    #  Данные: загрузка / сохранение
    # ════════════════════════════════════════════════════════════════
    def _find_opencode_config(self):
        for path in OPENCODE_CONFIG_CANDIDATES:
            if path and os.path.isfile(path):
                return path
        return None

    def _load_providers(self):
        # 1) из providers.json (если есть)
        if os.path.isfile(PROVIDERS_JSON):
            try:
                with open(PROVIDERS_JSON, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for pn, p in saved.items():
                    self.providers[pn] = {
                        "base_url": p.get("base_url", ""),
                        "api_key": p.get("api_key", ""),
                        "api_keys": p.get("api_keys", []),
                        "models": p.get("models", {}),
                    }
                    for mid, mc in p.get("models", {}).items():
                        self.model_list.append((pn, mid, mc.get("name", mid),
                                                mc.get("source", "opencode"), mc.get("free", False)))
            except Exception as e:
                self._log("Ошибка чтения providers.json: %s" % e, "error")
        # 2) дополняем из opencode-конфига
        path = self._find_opencode_config()
        if path:
            self._merge_opencode_config(path, announce=True)
        elif not self.providers:
            self._log("opencode.jsonc не найден — загрузите вручную на вкладке «Дашборд».", "warn")

    def _merge_opencode_config(self, path, announce=False):
        try:
            cfg = read_jsonc(path)
        except Exception as e:
            self._log("Не удалось прочитать %s: %s" % (os.path.basename(path), e), "error")
            return 0
        added = 0
        for pn, pc in cfg.get("provider", {}).items():
            opts = pc.get("options", {})
            base_url = (opts.get("baseURL") or "").rstrip("/")
            api_keys = list(opts.get("apiKeys", []))
            api_key = opts.get("apiKey", "")
            if api_key and api_key not in api_keys:
                api_keys.insert(0, api_key)
            disp = pc.get("name", pn)
            prov = self.providers.setdefault(disp, {"base_url": base_url, "api_key": "",
                                                    "api_keys": [], "models": {}})
            if base_url:
                prov["base_url"] = base_url
            for k in api_keys:
                if k and k not in prov["api_keys"]:
                    prov["api_keys"].append(k)
            if prov["api_keys"]:
                prov["api_key"] = prov["api_keys"][0]
            for mid, mc in pc.get("models", {}).items():
                if mid in prov["models"]:
                    continue
                mn = mc.get("name", mid)
                is_free = "free" in mid.lower() or "free" in mn.lower()
                prov["models"][mid] = {"name": mn, "source": "opencode", "free": is_free}
                self.model_list.append((disp, mid, mn, "opencode", is_free))
                added += 1
        if announce:
            self._log("Загружено из %s: %d моделей" % (os.path.basename(path), added), "success")
        self._save_providers()
        return added

    def _save_providers(self):
        data = {}
        for pn, p in self.providers.items():
            data[pn] = {
                "base_url": p.get("base_url", ""),
                "api_key": p.get("api_key", ""),
                "api_keys": p.get("api_keys", []),
                "models": p.get("models", {}),
            }
        try:
            save_json_secure(PROVIDERS_JSON, data)
        except Exception as e:
            self._log("Ошибка сохранения providers.json: %s" % e, "error")

    def _save_settings(self):
        data = {
            "timeout": self.timeout_val.get(),
            "retries": self.retries_val.get(),
            "delay": self.delay_val.get(),
            "dark_mode": self.dark_mode.get(),
            "verify_ssl": self.verify_ssl.get(),
            "auto_save_config": self.auto_save_config.get(),
            "geometry": self.geometry_val.get(),
        }
        try:
            with open(SETTINGS_JSON, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_settings(self):
        if not os.path.isfile(SETTINGS_JSON):
            return
        try:
            with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            return
        mapping = {
            "timeout": self.timeout_val, "retries": self.retries_val, "delay": self.delay_val,
            "dark_mode": self.dark_mode, "verify_ssl": self.verify_ssl,
            "auto_save_config": self.auto_save_config, "geometry": self.geometry_val,
        }
        for key, var in mapping.items():
            if key in d:
                try:
                    var.set(d[key])
                except Exception:
                    pass
        if d.get("geometry"):
            try:
                self.root.geometry(d["geometry"])
            except Exception:
                pass

    def _reload_config(self):
        path = self._find_opencode_config()
        if not path:
            messagebox.showinfo("Конфиг", "opencode.jsonc не найден в стандартных папках.")
            return
        n = self._merge_opencode_config(path, announce=True)
        self._rebuild_provider_filter()
        self._refresh_table()
        self._set_status("Перечитан конфиг: +%d моделей" % n)

    def _load_opencode_file(self):
        p = filedialog.askopenfilename(
            title="Выберите opencode.jsonc",
            filetypes=[("JSONC", "*.jsonc"), ("JSON", "*.json"), ("Все", "*.*")])
        if not p:
            return
        n = self._merge_opencode_config(p, announce=True)
        self._rebuild_provider_filter()
        self._refresh_table()
        self._set_status("Загружено %d новых моделей" % n)

    def _add_custom_model(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Добавить модель")
        dlg.geometry("460x230")
        dlg.transient(self.root)
        dlg.grab_set()
        f = ttk.Frame(dlg, padding=16)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text="Провайдер (выберите или введите новый):").grid(row=0, column=0, columnspan=2, sticky="w")
        pv = tk.StringVar()
        prov_vals = sorted(self.providers.keys())
        pc = ttk.Combobox(f, textvariable=pv, values=prov_vals)
        pc.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        if prov_vals:
            pc.set(prov_vals[0])
        ttk.Label(f, text="ID модели:").grid(row=2, column=0, sticky="w", pady=3)
        mv = tk.StringVar()
        ttk.Entry(f, textvariable=mv, width=34).grid(row=2, column=1, sticky="ew", padx=6)
        ttk.Label(f, text="Имя (опц.):").grid(row=3, column=0, sticky="w", pady=3)
        nv = tk.StringVar()
        ttk.Entry(f, textvariable=nv, width=34).grid(row=3, column=1, sticky="ew", padx=6)
        f.grid_columnconfigure(1, weight=1)

        def do():
            pr, mid, nm = pv.get().strip(), mv.get().strip(), (nv.get().strip() or mv.get().strip())
            if not pr or not mid:
                messagebox.showwarning("Ошибка", "Провайдер и ID обязательны.")
                return
            prov = self.providers.setdefault(
                pr, {"base_url": "https://api.freetheai.xyz/v1", "api_key": "", "api_keys": [], "models": {}})
            if mid in prov["models"]:
                messagebox.showwarning("Ошибка", "Такая модель уже есть.")
                return
            prov["models"][mid] = {"name": nm, "source": "custom", "free": False}
            self.model_list.append((pr, mid, nm, "custom", False))
            self._rebuild_provider_filter()
            self._refresh_table()
            self._save_providers()
            self._log("Добавлена модель: %s / %s" % (pr, mid), "success")
            dlg.destroy()

        bf = ttk.Frame(f)
        bf.grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Button(bf, text="Добавить", style="Accent.TButton", command=do).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Отмена", command=dlg.destroy).pack(side=tk.LEFT)

    # ════════════════════════════════════════════════════════════════
    #  Провайдеры: сохранение из UI + проверка ключей
    # ════════════════════════════════════════════════════════════════
    def _save_providers_ui(self):
        for pn, (uv, combo) in self.prov_entries.items():
            self.providers[pn]["base_url"] = uv.get().strip()
            keys = list(getattr(combo, "_real_keys", []))
            self.providers[pn]["api_keys"] = keys
            self.providers[pn]["api_key"] = keys[0] if keys else ""
        with VALID_KEYS_LOCK:
            VALID_KEYS_CACHE.clear()
        self._save_providers()
        self._log("Настройки провайдеров сохранены", "success")
        self._set_status("Провайдеры сохранены")

    def _test_provider_keys(self, provider_name, combo, url_var):
        p = self.providers.get(provider_name)
        if not p or not p.get("models"):
            self._log("Нет моделей для проверки ключей: %s" % provider_name, "warn")
            return
        keys = list(getattr(combo, "_real_keys", []))
        if not keys:
            self._log("Нет ключей для проверки: %s" % provider_name, "warn")
            return
        base_url = (url_var.get().strip() or p.get("base_url", "")).rstrip("/")
        model_id = next(iter(p["models"]))  # FIX: models — словарь
        verify = self.verify_ssl.get()
        self._log("Проверка ключей %s (через %s)..." % (provider_name, model_id))

        def run():
            results = {}
            url = base_url + "/chat/completions"
            for k in keys:
                body = {"model": model_id, "messages": [{"role": "user", "content": "say ok"}], "max_tokens": 5}
                headers = {"Content-Type": "application/json", "Authorization": "Bearer " + k}
                try:
                    code, text = http_post(url, body, headers, timeout=15, verify=verify)
                except Exception as e:
                    results[k] = (False, "ошибка: %s" % str(e)[:50])
                    continue
                if code == 200:
                    results[k] = (True, "Работает")
                    continue
                try:
                    err = (json.loads(text).get("error", {}) or {}).get("message", "")
                except Exception:
                    err = ""
                results[k] = (False, "HTTP %d: %s" % (code, (ERR_DESC.get(code) or err)[:50]))
            working = [k for k, (ok, _) in results.items() if ok]
            for k in keys:
                ok, msg = results.get(k, (False, "нет ответа"))
                self.root.after(0, self._log,
                                "%s %s: %s" % ("✓" if ok else "✗", mask_key(k), msg),
                                "success" if ok else "error")
            chosen = working[0] if working else keys[0]
            idx = keys.index(chosen)
            self.root.after(0, lambda: combo.current(idx))
            self.root.after(0, self._log,
                            ("Ключ выбран: %s" % mask_key(chosen)) if working
                            else ("Нет рабочих ключей, выбран: %s" % mask_key(chosen)),
                            "success" if working else "warn")

        threading.Thread(target=run, daemon=True).start()

    def _auto_validate_keys(self):
        def run():
            verify = self.verify_ssl.get()
            for pn, p in list(self.providers.items()):
                keys = p.get("api_keys", [])
                bu = p.get("base_url", "").rstrip("/")
                if not keys or not bu:
                    continue
                with VALID_KEYS_LOCK:
                    if bu in VALID_KEYS_CACHE:
                        continue
                self.root.after(0, self._log, "Проверка ключей %s (%s)..." % (pn, key_fmt(len(keys))))
                valid = validate_keys(bu, keys, provider_models=p["models"], provider_name=pn,
                                      timeout=10, verify=verify,
                                      log=lambda m: self.root.after(0, self._log, m))
                with VALID_KEYS_LOCK:
                    VALID_KEYS_CACHE[bu] = valid
                msg = ("  %s: работает %s" % (pn, key_fmt(len(valid), len(keys)))) if valid \
                    else ("  %s: нет рабочих ключей" % pn)
                self.root.after(0, self._log, msg, "success" if valid else "warn")
        threading.Thread(target=run, daemon=True).start()

    # ════════════════════════════════════════════════════════════════
    #  Таблица
    # ════════════════════════════════════════════════════════════════
    def _rebuild_provider_filter(self):
        names = ["all"] + sorted(self.providers.keys())
        self.provider_combo["values"] = names

    def _refresh_table(self, *_):
        for i in self.tree.get_children():
            self.tree.delete(i)
        pf = self.filter_provider.get()
        sf = self.filter_status.get()
        fc = self.filter_source.get()
        query = self.search_var.get().strip().lower()
        total = ok = fail = unt = 0
        row = 0
        for pn, mid, mn, src, fr in self.model_list:
            if pf != "all" and pn != pf:
                continue
            if fc != "all" and src != fc:
                continue
            if query and query not in mn.lower() and query not in mid.lower():
                continue
            r = self.results.get(pn, {}).get(mid)
            if r is None:
                if sf not in ("all", "untested"):
                    continue
                st, resp, el, tag = "— не проверено", "", "", "untested"
                unt += 1
            elif r["ok"]:
                if sf not in ("all", "yes"):
                    continue
                st, resp, el, tag = "✓ работает", r["msg"], "%.1fs" % r["elapsed"], "ok"
                ok += 1
            else:
                if sf not in ("all", "no"):
                    continue
                st, resp, el, tag = "✗ ошибка", r["msg"], "%.1fs" % r["elapsed"], "fail"
                fail += 1
            total += 1
            disp = mn + ("  🆓" if fr else "")
            stripe = "odd" if row % 2 else "even"
            self.tree.insert("", tk.END, values=(pn, disp, mid, src, st, resp, el), tags=(tag, stripe))
            row += 1
        self._update_cards(total, ok, fail, unt)

    def _update_cards(self, total, ok, fail, unt):
        self.card_value_lbls["total"].config(text=str(total))
        self.card_value_lbls["ok"].config(text=str(ok))
        self.card_value_lbls["fail"].config(text=str(fail))
        self.card_value_lbls["untested"].config(text=str(unt))

    def _sort_by(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        items.sort(key=lambda x: x[0].lower(),
                   reverse=self.sort_rev if self.sort_col == col else False)
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, "", idx)
        self.sort_rev = (not self.sort_rev) if self.sort_col == col else False
        self.sort_col = col
        arrow = " ▲" if self.sort_rev else " ▼"
        for c, _w, h in self.cols:
            self.tree.heading(c, text=h + (arrow if c == col else ""))

    def _items_from_sel(self, sel):
        out = []
        for iid in sel:
            v = self.tree.item(iid, "values")
            mid = v[2]
            for x in self.model_list:
                if x[0] == v[0] and x[1] == mid:
                    out.append(x)
                    break
        return out

    def _on_double_click(self, e):
        sel = self.tree.selection()
        if sel:
            mid = self.tree.item(sel[0], "values")[2]
            self.root.clipboard_clear()
            self.root.clipboard_append(mid)
            self._set_status("Скопирован ID: %s" % mid)

    def _on_right_click(self, e):
        iid = self.tree.identify_row(e.y)
        if not iid:
            return
        sel = self.tree.selection()
        if iid not in sel:
            self.tree.selection_set(iid)
            sel = (iid,)
        menu = tk.Menu(self.root, tearoff=0)
        cnt = len(sel)
        label = "Проверить выбранное" if cnt == 1 else "Проверить %d моделей" % cnt
        menu.add_command(label=label, command=lambda: self._run_tests(self._items_from_sel(sel)))
        menu.add_command(label="Копировать ID", command=lambda: self._copy_ids(sel))
        menu.add_separator()
        v = self.tree.item(sel[0], "values")
        menu.add_command(label="Проверить всё у провайдера «%s»" % v[0],
                         command=lambda: self._run_tests([x for x in self.model_list if x[0] == v[0]]))
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _copy_ids(self, sel):
        ids = [self.tree.item(iid, "values")[2] for iid in sel]
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(ids))
        self._set_status("Скопировано ID: %d" % len(ids))

    # ════════════════════════════════════════════════════════════════
    #  Запуск проверок
    # ════════════════════════════════════════════════════════════════
    def _start_all(self):
        pf, sf, fc = self.filter_provider.get(), self.filter_status.get(), self.filter_source.get()
        query = self.search_var.get().strip().lower()
        items = []
        for x in self.model_list:
            pn, mid, mn, src, fr = x
            if pf != "all" and pn != pf:
                continue
            if fc != "all" and src != fc:
                continue
            if query and query not in mn.lower() and query not in mid.lower():
                continue
            r = self.results.get(pn, {}).get(mid)
            if r is None and sf not in ("all", "untested"):
                continue
            if r is not None and r["ok"] and sf not in ("all", "yes"):
                continue
            if r is not None and not r["ok"] and sf not in ("all", "no"):
                continue
            items.append(x)
        self._run_tests(items)

    def _start_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите модели на вкладке «Модели».")
            self.nb.select(self.tab_models)
            return
        self._run_tests(self._items_from_sel(sel))

    def _run_tests(self, items):
        if self.running or not items:
            return
        self.running = True
        self.cancel_flag = False
        self.btn_all.config(state=tk.DISABLED)
        self.btn_sel.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.dash_progress["maximum"] = len(items)
        self.dash_progress["value"] = 0
        self.dash_prog_lbl.config(text="Проверка %d моделей..." % len(items))
        threading.Thread(target=self._worker, args=(items,), daemon=True).start()

    def _stop(self):
        if self.running:
            self.cancel_flag = True
            self._log("Остановка...", "warn")
            self._set_status("Остановка...")

    def _worker(self, items):
        to, rt, dl = self.timeout_val.get(), self.retries_val.get(), self.delay_val.get()
        verify = self.verify_ssl.get()
        batch_ok = 0
        for i, (pn, mid, mn, _src, _fr) in enumerate(items):
            if self.cancel_flag:
                break
            p = self.providers.get(pn)
            if not p:
                continue
            keys = p.get("api_keys", [])
            if not keys:
                self.results.setdefault(pn, {})[mid] = {"ok": False, "msg": "Нет API-ключей", "elapsed": 0}
                self.root.after(0, self._log, "  Нет ключей для %s" % pn, "warn")
                continue
            ok, msg, el = test_model(p["base_url"], keys, mid, timeout=to, retries=rt,
                                     verify=verify, log=lambda m: self.root.after(0, self._log, m))
            self.results.setdefault(pn, {})[mid] = {"ok": ok, "msg": msg, "elapsed": el}
            if ok:
                batch_ok += 1
            self.root.after(0, self._log, "  %s %s (%.1fs) — %s" %
                            ("✓" if ok else "✗", mn, el, msg), "success" if ok else "error")
            self.root.after(0, self._refresh_table)
            self.root.after(0, lambda v=i + 1: self.dash_progress.configure(value=v))
            if i < len(items) - 1 and not self.cancel_flag:
                time.sleep(dl)
        self.root.after(0, lambda: self._on_done(batch_ok))

    def _on_done(self, batch_ok=0):
        self.running = False
        self.btn_all.config(state=tk.NORMAL)
        self.btn_sel.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        ok = sum(1 for pr in self.results.values() for r in pr.values() if r["ok"])
        fail = sum(1 for pr in self.results.values() for r in pr.values() if not r["ok"])
        self.dash_prog_lbl.config(text="Завершено: %d работает, %d ошибок" % (ok, fail))
        self._set_status("Готово")
        self._log("Завершено: %d ✓ / %d ✗" % (ok, fail), "success" if ok else "info")
        if batch_ok > 0 and messagebox.askyesno(
                "Сохранить конфиг",
                "Найдено %d работающих моделей.\nЭкспортировать рабочие модели в opencode.jsonc?" % batch_ok):
            self._export_dialog(preselect_ok_only=True)

    # ════════════════════════════════════════════════════════════════
    #  Экспорт
    # ════════════════════════════════════════════════════════════════
    def _export_dialog(self, preselect_ok_only=False):
        if not self.model_list:
            messagebox.showinfo("Экспорт", "Нет моделей для экспорта.")
            return
        dlg = tk.Toplevel(self.root)
        dlg.title("Экспорт в opencode.jsonc")
        dlg.geometry("680x560")
        dlg.transient(self.root)
        dlg.grab_set()
        f = ttk.Frame(dlg, padding=12)
        f.pack(fill=tk.BOTH, expand=True)

        pf = ttk.Frame(f)
        pf.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(pf, text="Путь:").pack(side=tk.LEFT)
        path_v = tk.StringVar(value=os.path.join(SCRIPT_DIR, "opencode.jsonc"))
        ttk.Entry(pf, textvariable=path_v).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        ttk.Button(pf, text="Обзор", command=lambda: path_v.set(
            filedialog.asksaveasfilename(defaultextension=".jsonc",
                                         filetypes=[("JSONC", "*.jsonc"), ("JSON", "*.json")],
                                         initialfile="opencode.jsonc") or path_v.get())).pack(side=tk.LEFT)
        bkup_v = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Создать бэкап с датой", variable=bkup_v).pack(anchor="w")

        ttk.Label(f, text="Отметьте модели для экспорта:",
                  font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(6, 2))
        tvf = ttk.Frame(f)
        tvf.pack(fill=tk.BOTH, expand=True)
        tv = ttk.Treeview(tvf, columns=("chk", "name", "info"), show="tree", height=14)
        tv.column("#0", width=0, stretch=False)
        tv.column("chk", width=34, anchor="center")
        tv.column("name", width=360)
        tv.column("info", width=120)
        sb = ttk.Scrollbar(tvf, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=sb.set)
        tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        chk = {}  # iid -> bool
        prov_models = {}
        for pn, mid, mn, src, fr in self.model_list:
            prov_models.setdefault(pn, []).append((mid, mn, src, fr))
        node_meta = {}  # model iid -> (provider, mid, mn)
        for pn in prov_models:
            piid = tv.insert("", tk.END, values=("☑", pn, ""), open=True)
            chk[piid] = True
            for mid, mn, src, fr in prov_models[pn]:
                r = self.results.get(pn, {}).get(mid)
                info = "—" if r is None else ("✓" if r["ok"] else "✗")
                checked = True if not preselect_ok_only else (r is not None and r["ok"])
                miid = tv.insert(piid, tk.END, values=("☑" if checked else "☐", mn, info))
                chk[miid] = checked
                node_meta[miid] = (pn, mid, mn)

        def toggle(iid):
            new = not chk.get(iid, False)
            chk[iid] = new
            tv.set(iid, "chk", "☑" if new else "☐")
            for c in tv.get_children(iid):
                chk[c] = new
                tv.set(c, "chk", "☑" if new else "☐")

        def on_click(e):
            iid = tv.identify_row(e.y)
            if iid and tv.identify_column(e.x) in ("#0", "#1"):
                toggle(iid)
                return "break"
        tv.bind("<Button-1>", on_click, "+")

        bf = ttk.Frame(f)
        bf.pack(fill=tk.X, pady=8)

        def do_save():
            path = path_v.get().strip()
            if not path:
                messagebox.showerror("Ошибка", "Укажите путь.")
                return
            if bkup_v.get() and os.path.isfile(path):
                import shutil
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    shutil.copy2(path, path + ".bak_" + ts)
                except Exception:
                    pass
            provider_block = {}
            for miid, (pn, mid, mn) in node_meta.items():
                if not chk.get(miid):
                    continue
                pb = provider_block.setdefault(pn, {"name": pn, "options": {}, "models": {}})
                bu = self.providers.get(pn, {}).get("base_url", "")
                keys = self.providers.get(pn, {}).get("api_keys", [])
                if bu:
                    pb["options"]["baseURL"] = bu
                if keys:
                    pb["options"]["apiKey"] = keys[0]
                pb["models"][mid] = {"name": mn}
            if not provider_block:
                messagebox.showwarning("Экспорт", "Не выбрано ни одной модели.")
                return
            try:
                with open(path, "w", encoding="utf-8") as fp:
                    json.dump({"provider": provider_block}, fp, ensure_ascii=False, indent=2)
                self._log("Экспортировано в %s" % path, "success")
                self._set_status("Экспортировано: %s" % os.path.basename(path))
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", "Не удалось сохранить:\n%s" % e)

        ttk.Button(bf, text="💾 Сохранить", style="Accent.TButton", command=do_save).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Отмена", command=dlg.destroy).pack(side=tk.LEFT, padx=2)

    def _export_results(self):
        if not self.results:
            messagebox.showinfo("Экспорт", "Нет результатов — сначала запустите проверку.")
            return
        p = filedialog.asksaveasfilename(defaultextension=".json",
                                         filetypes=[("JSON", "*.json"), ("CSV", "*.csv")])
        if not p:
            return
        try:
            if p.lower().endswith(".csv"):
                self._export_csv(p)
            else:
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(self.results, f, ensure_ascii=False, indent=2)
            self._log("Результаты экспортированы: %s" % p, "success")
            self._set_status("Экспортировано: %s" % os.path.basename(p))
        except Exception as e:
            messagebox.showerror("Ошибка", "Не удалось экспортировать:\n%s" % e)

    def _export_csv(self, path):
        import csv
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Provider", "Model", "Source", "Status", "Response", "Time"])
            for pn, mid, mn, src, _fr in self.model_list:
                r = self.results.get(pn, {}).get(mid)
                if r is None:
                    w.writerow([pn, mn, src, "untested", "", ""])
                else:
                    w.writerow([pn, mn, src, "OK" if r["ok"] else "FAIL", r["msg"], "%.1f" % r["elapsed"]])

    # ════════════════════════════════════════════════════════════════
    #  Лог
    # ════════════════════════════════════════════════════════════════
    def _init_log_file(self):
        try:
            os.makedirs(LOGS_DIR, exist_ok=True)
            self.log_file = open(os.path.join(LOGS_DIR, time.strftime("%Y-%m-%d") + ".log"),
                                 "a", encoding="utf-8")
        except Exception:
            self.log_file = None

    def _log(self, msg, tag=None):
        if tag is None:
            low = msg.lower()
            if any(w in low for w in ("ошибка", "error", "✗", "не работает", "неверн", "403", "401")):
                tag = "error"
            elif any(w in low for w in ("работает", "успех", "✓", "success", "200", "сохранен")):
                tag = "success"
            elif any(w in low for w in ("warn", "timeout", "429", "лимит", "остановка")):
                tag = "warn"
            else:
                tag = "info"
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n", tag)   # FIX: позиционный тег вместо tagS=
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
        if self.log_file:
            try:
                self.log_file.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), msg))
                self.log_file.flush()
            except Exception:
                pass

    def _clear_log(self):
        self.log.config(state=tk.NORMAL)
        self.log.delete("1.0", tk.END)
        self.log.config(state=tk.DISABLED)

    def _show_log_browser(self):
        if not os.path.isdir(LOGS_DIR):
            messagebox.showinfo("Логи", "Нет файлов логов.")
            return
        logs = sorted((f for f in os.listdir(LOGS_DIR) if f.endswith(".log")), reverse=True)
        if not logs:
            messagebox.showinfo("Логи", "Нет файлов логов.")
            return
        dlg = tk.Toplevel(self.root)
        dlg.title("Логи на диске")
        dlg.geometry("720x500")
        dlg.transient(self.root)
        f = ttk.Frame(dlg, padding=6)
        f.pack(fill=tk.BOTH, expand=True)
        lb = tk.Listbox(f, width=26)
        lb.pack(side=tk.LEFT, fill=tk.Y)
        for lg in logs:
            lb.insert(tk.END, lg)
        txt = tk.Text(f, wrap=tk.WORD)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        def load(_=None):
            sel = lb.curselection()
            if not sel:
                return
            txt.delete("1.0", tk.END)
            try:
                with open(os.path.join(LOGS_DIR, lb.get(sel[0])), "r", encoding="utf-8") as lf:
                    txt.insert(tk.END, lf.read())
            except Exception as e:
                txt.insert(tk.END, "Ошибка: %s" % e)
        lb.bind("<<ListboxSelect>>", load)
        lb.selection_set(0)
        load()

    # ════════════════════════════════════════════════════════════════
    #  Прочее
    # ════════════════════════════════════════════════════════════════
    def _set_status(self, text):
        self.statusbar.config(text=text)

    def _about(self):
        backend = "requests" if _HAS_REQUESTS else "urllib"
        messagebox.showinfo(
            "О программе",
            "AgentChecker %s\n\nПроверка доступности AI-моделей из конфигурации OpenCode.\n\n"
            "Python: %s\nHTTP-backend: %s\nTLS-проверка: %s" %
            (APP_VERSION, sys.version.split()[0], backend,
             "включена" if self.verify_ssl.get() else "ОТКЛЮЧЕНА"))

    def _on_close(self):
        self.geometry_val.set(self.root.geometry())
        self._save_settings()
        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    AgentCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
