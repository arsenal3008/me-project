#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AgentChecker — GUI-приложение для проверки доступности AI-моделей.
Встроенный каталог моделей FreeTheAI + OpenCode Zen - free +
пользовательские модели + загрузка opencode.jsonc + управление ключами/URL провайдеров.
"""

from __future__ import print_function, division, unicode_literals

import json
import os
import socket
import sys
import time
import threading
from urllib.parse import urlparse

# ── Python version compat ──────────────────────────────────────────
IS_PY3 = sys.version_info >= (3,)

if IS_PY3:
    import urllib.request as urllib2
    import ssl
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
else:
    import urllib2
    import ssl
    import Tkinter as tk
    import ttk
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog

# ── SSL context ────────────────────────────────────────────────────
_ssl_ctx = None
try:
    _ssl_ctx = ssl.create_default_context()
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE
except Exception:
    pass

# ── HTTP backend ───────────────────────────────────────────────────
_HTTP = 'urllib2'
try:
    import warnings
    warnings.filterwarnings('ignore')
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)
    _HTTP = 'requests'
except ImportError:
    pass

# ── Defaults ───────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROVIDERS_JSON = os.path.join(SCRIPT_DIR, 'providers.json')
SETTINGS_JSON = os.path.join(SCRIPT_DIR, 'settings.json')
LOGS_DIR = os.path.join(SCRIPT_DIR, 'logs')

# ── Built-in providers ─────────────────────────────────────────────
# Все данные загружаются из opencode.jsonc
BUILTIN_MODELS = {}

ERR_DESC = {
    400: 'Неизвестная модель', 401: 'Неверный API ключ',
    403: 'Доступ запрещён (Cloudflare?)',
    429: 'Превышен лимит запросов', 500: 'Внутренняя ошибка сервера',
    502: 'Шлюз недоступен', 503: 'Провайдер не отвечает',
}


def read_jsonc(path):
    """Читает JSONC (JSON с // комментариями)."""
    with open(path, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    lines = []
    for line in text.split('\n'):
        in_str = False
        i = 0
        while i < len(line):
            if line[i] == '"':
                in_str = not in_str
            elif line[i:i+2] == '//' and not in_str:
                line = line[:i]
                break
            i += 1
        lines.append(line)
    return json.loads('\n'.join(lines))

def save_jsonc(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print('[ERROR] Ошибка сохранения конфига: %s' % e)


# ── Helpers ────────────────────────────────────────────────────────

# Кеш валидных ключей: {base_url: [key1, key2, ...]}
VALID_KEYS_CACHE = {}
VALID_KEYS_LOCK = threading.Lock()


def _plural(n, forms):
    n = abs(n) % 100
    if 10 < n < 20:
        return forms[2]
    n %= 10
    if n == 1:
        return forms[0]
    if 1 < n < 5:
        return forms[1]
    return forms[2]


def _key_fmt(n, total=None):
    w = _plural(total or n, ('\u043a\u043b\u044e\u0447', '\u043a\u043b\u044e\u0447\u0430', '\u043a\u043b\u044e\u0447\u0435\u0439'))
    if total is not None:
        return '%d \u0438\u0437 %d %s' % (n, total, w)
    return '%d %s' % (n, w)


def validate_keys(base_url, all_keys, provider_models=None, provider_name='', timeout=10):
    url = base_url.rstrip('/') + '/chat/completions'
    tag = provider_name or url
    provider_models = provider_models or {}
    first_mid = next(iter(provider_models)) if provider_models else 'gpt-4o-mini'
    for k in all_keys:
        if not k:
            continue
        body = {'model': first_mid, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 1}
        headers = {'Authorization': 'Bearer %s' % k, 'Content-Type': 'application/json'}
        c, t = http_post(url, body, headers, timeout=timeout)
        if c == 200:
            print('[%s] %s... -> HTTP 200 (ключ работает)' % (tag, k[:12]))
            return [k]
        if c in (401, 403):
            try:
                err_data = json.loads(t)
                err_msg = (err_data.get('error', {}) or err_data).get('message', '') or ''
            except Exception:
                err_msg = t[:120]
            if 'model' in err_msg.lower() and ('support' in err_msg.lower() or 'not found' in err_msg.lower() or 'not exist' in err_msg.lower()):
                print('[%s] %s... -> HTTP %d модель не найдена, ключ работает' % (tag, k[:12], c))
                return [k]
            else:
                print('[%s] %s... -> HTTP %d ключ НЕВЕРНЫЙ (%s)' % (tag, k[:12], c, err_msg[:60]))
        else:
            try:
                err_data = json.loads(t)
                err_msg = (err_data.get('error', {}) or err_data).get('message', '') or ''
            except Exception:
                err_msg = ''
            if err_msg:
                trans = {
                    'daily successful request limit exceeded': 'превышен дневной лимит запросов',
                    'rate limit exceeded': 'превышен лимит запросов',
                    'too many requests': 'слишком много запросов',
                    'model not found': 'модель не найдена',
                    'unknown model': 'неизвестная модель',
                    'server error': 'ошибка сервера',
                    'service unavailable': 'сервис недоступен',
                }
                for eng, rus in trans.items():
                    if eng in err_msg.lower():
                        err_msg = rus
                        break
                print('[%s] %s... -> HTTP %d: %s (ключ считается рабочим)' % (tag, k[:12], c, err_msg[:80]))
            else:
                print('[%s] %s... -> HTTP %d (ключ считается рабочим)' % (tag, k[:12], c))
            return [k]
    print('[%s] URL=%s keys=%d valid=0' % (tag, url, len(all_keys)))
    return []


def http_post(url, body, headers, timeout=20):
    try:
        if _HTTP == 'requests':
            r = requests.post(url, json=body, headers=headers, timeout=timeout, verify=False)
            return r.status_code, r.text
        req = urllib2.Request(url, json.dumps(body).encode(), headers)
        if _ssl_ctx:
            resp = urllib2.urlopen(req, timeout=timeout, context=_ssl_ctx)
        else:
            resp = urllib2.urlopen(req, timeout=timeout)
        return resp.getcode(), resp.read()
    except Exception as e:
        print('[HTTP] %s -> %s' % (url[:60], e))
        raise


def test_model(base_url, api_keys, model_id, timeout=20, retries=2):
    """Проверяет модель, автоматически отфильтровывая невалидные ключи."""
    start = time.time()
    if not api_keys:
        return False, 'Нет API ключей', 0
    # Используем только валидные ключи (кеш)
    with VALID_KEYS_LOCK:
        cache_key = base_url.rstrip('/')
        valid = VALID_KEYS_CACHE.get(cache_key)
        if valid is None:
            print('[TEST] Кеш пуст для %s, запускаю validate_keys...' % cache_key)
            valid = validate_keys(base_url, api_keys, timeout=10)
            VALID_KEYS_CACHE[cache_key] = valid
        else:
            print('[TEST] Кеш для %s: %d валидных ключей' % (cache_key, len(valid)))
    if not valid:
        print('[TEST] Нет валидных ключей для %s, модель=%s' % (cache_key, model_id))
        return False, 'Ни один ключ не прошёл проверку', 0
    for key_idx, api_key in enumerate(valid):
        try:
            body = {
                'model': model_id,
                'messages': [{'role': 'user', 'content': 'say ok'}],
                'max_tokens': 5,
            }
            url = base_url.rstrip('/') + '/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            if 'localhost' not in url and '127.0.0.1' not in url:
                headers['Origin'] = 'https://opencode.ai'
                headers['Referer'] = 'https://opencode.ai/'
            if api_key:
                headers['Authorization'] = 'Bearer ' + api_key
            for attempt in range(retries + 1):
                code, resp_text = http_post(url, body, headers, timeout=timeout)
                elapsed = time.time() - start
                print('[TEST] key=%s attempt=%d model=%s HTTP=%d resp=%.120s' % (api_key[:12]+'...', attempt, model_id, code, resp_text.strip()[:120]))
                # Сначала обрабатываем HTTP-код (ретраи, смена ключа) до парсинга JSON
                if code == 429 and attempt < retries:
                    time.sleep(3 * (attempt + 1))
                    continue
                if code != 200 and key_idx < len(valid) - 1:
                    break
                # Парсим JSON
                try:
                    data = json.loads(resp_text)
                except Exception:
                    raw = resp_text.strip()[:120]
                    if raw:
                        return False, raw, elapsed
                    reason = 'Cloudflare/блокировка' if code == 403 else 'пустой ответ'
                    return False, 'HTTP %d: %s' % (code, reason), elapsed
                if code == 200 and 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0].get('message', {}).get('content', '') or ''
                    return True, content.strip()[:80], elapsed
                err = data.get('error', {}).get('message', '')
                desc = ERR_DESC.get(code)
                tag = 'RATE' if code == 429 else 'HTTP %d' % code
                msg = desc if desc else (err or '')
                return False, '%s: %s' % (tag, msg), elapsed
        except Exception as e:
            elapsed = time.time() - start
            if key_idx < len(valid) - 1:
                continue
            return False, 'Ошибка соединения: %s' % str(e)[:60], elapsed
    return False, 'Все ключи не подошли', time.time() - start


# ── GUI Application ────────────────────────────────────────────────

class AgentCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('AgentChecker — проверка AI-моделей')
        self.root.geometry('1020x720')
        self.root.minsize(860, 540)

        # state
        self.timeout_val = tk.IntVar(value=20)
        self.retries_val = tk.IntVar(value=2)
        self.delay_val = tk.DoubleVar(value=0.3)
        self.filter_status = tk.StringVar(value='all')
        self.filter_provider_s = tk.StringVar(value='all')
        self.filter_source = tk.StringVar(value='all')
        self.filter_free = tk.StringVar(value='all')
        self.providers = {}       # {name: {base_url, api_key, models: {id: {name,source}}}}
        self.results = {}         # {pname: {mid: {ok,msg,elapsed}}}
        self.model_list = []      # [(provider, model_id, model_name, source)]
        self.running = False
        self.cancel_flag = False
        self.sort_col = None
        self.sort_rev = False
        self.dark_mode = tk.BooleanVar(value=False)
        self.geometry_val = tk.StringVar(value='1020x720')
        self.log_height_val = tk.IntVar(value=5)
        self.auto_save_config = tk.BooleanVar(value=True)
        self.auto_start_ollama = tk.BooleanVar(value=True)
        self.hide_ollama_window = tk.BooleanVar(value=True)
        self.log_file = None
        self._init_log_file()

        self._build_ui()
        self._load_settings()
        self.root.geometry(self.geometry_val.get())
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)
        self._load_builtin()
        self._load_providers()
        self._purge_empty_providers()
        self._propagate_keys()
        self._rebuild_provider_filter()
        self._apply_theme()
        self._refresh_table()
        self._ensure_ollama_running()
        self._auto_validate_keys()

    # ── UI ─────────────────────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('vista' if 'vista' in style.theme_names() else 'clam')
        style.configure('TCombobox', padding=3, arrowsize=14)
        style.configure('Accent.TButton', font=('', 9, 'bold'))
        style.configure('Filter.TCombobox', arrowcolor='#555')
        self._build_menu()
        self._build_toolbar()
        self._build_main()
        self._build_statusbar()

    def _build_menu(self):
        mb = tk.Menu(self.root)
        self.root.config(menu=mb)
        fm = tk.Menu(mb, tearoff=0)
        fm.add_command(label='Загрузить opencode.jsonc...', command=self._load_opencode_file)
        fm.add_separator()
        fm.add_command(label='Экспорт результатов...', command=self._export_results)
        fm.add_separator()
        fm.add_command(label='Просмотр логов...', command=self._show_log_browser)
        fm.add_separator()
        fm.add_command(label='Выход', command=self.root.quit)
        mb.add_cascade(label='Файл', menu=fm)
        mm = tk.Menu(mb, tearoff=0)
        mm.add_command(label='Сбросить к встроенному каталогу', command=self._reset_to_builtin)
        mm.add_command(label='Добавить пользовательскую модель...', command=self._add_custom_model)
        mm.add_command(label='Удалить пользовательские модели', command=self._remove_custom_models)
        mb.add_cascade(label='Модели', menu=mm)
        tm = tk.Menu(mb, tearoff=0)
        tm.add_command(label='Проверить все', command=self._start_all)
        tm.add_command(label='Проверить выбранные', command=self._start_selected)
        tm.add_command(label='Остановить', command=self._stop)
        mb.add_cascade(label='Тест', menu=tm)
        sm = tk.Menu(mb, tearoff=0)
        sm.add_command(label='Настройки...', command=self._show_settings)
        sm.add_separator()
        sm.add_checkbutton(label='Авто-сохранение в opencode.jsonc', variable=self.auto_save_config, command=self._save_settings)
        sm.add_checkbutton(label='Авто-запуск Ollama', variable=self.auto_start_ollama, command=self._save_settings)
        sm.add_checkbutton(label='Сворачивать окно Ollama в трей', variable=self.hide_ollama_window, command=self._save_settings)
        mb.add_cascade(label='Настройки', menu=sm)
        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label='О программе', command=self._about)
        mb.add_cascade(label='Справка', menu=hm)
        vm = tk.Menu(mb, tearoff=0)
        vm.add_checkbutton(label='Тёмная тема', variable=self.dark_mode, command=self._toggle_theme)
        mb.add_cascade(label='Вид', menu=vm)

    def _build_toolbar(self):
        tb = ttk.Frame(self.root)
        tb.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))
        self.btn_all = ttk.Button(tb, text='\u25b6 Проверить все', style='Accent.TButton', command=self._start_all)
        self.btn_all.pack(side=tk.LEFT, padx=2)
        self.btn_sel = ttk.Button(tb, text='\u25b6 Выбранные', command=self._start_selected)
        self.btn_sel.pack(side=tk.LEFT, padx=2)
        self.btn_stop = ttk.Button(tb, text='\u25a0 Стоп', command=self._stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text='\u2699 Настройки', command=self._show_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(tb, text='\U0001f511 Ключи', style='Accent.TButton', command=self._show_providers_dialog).pack(side=tk.RIGHT, padx=5)
        ttk.Button(tb, text='\U0001f4e4 Экспорт', command=self._export_dialog).pack(side=tk.RIGHT, padx=2)

    def _build_main(self):
        mf = ttk.Frame(self.root)
        mf.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        left = ttk.Frame(mf, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left.pack_propagate(False)

        ttk.Label(left, text='\u0424\u0438\u043b\u044c\u0442\u0440\u044b', font=('', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(left, text='\u041f\u0440\u043e\u0432\u0430\u0439\u0434\u0435\u0440:', font=('', 8)).pack(anchor=tk.W)
        self.provider_combo = ttk.Combobox(left, textvariable=self.filter_provider_s, state='readonly', values=['all'])
        self.provider_combo.pack(fill=tk.X, pady=(0, 8))
        self.provider_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_table())
        ttk.Label(left, text='\u0421\u0442\u0430\u0442\u0443\u0441:', font=('', 8)).pack(anchor=tk.W)
        ttk.Combobox(left, textvariable=self.filter_status, state='readonly', values=['all', 'yes', 'no', 'untested']).pack(fill=tk.X, pady=(0, 8))
        self.filter_status.trace('w', lambda *a: self._refresh_table())
        ttk.Label(left, text='\u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a:', font=('', 8)).pack(anchor=tk.W)
        ttk.Combobox(left, textvariable=self.filter_source, state='readonly', values=['all', 'builtin', 'opencode', 'custom']).pack(fill=tk.X, pady=(0, 8))
        self.filter_source.trace('w', lambda *a: self._refresh_table())
        ttk.Label(left, text='\u0422\u0438\u043f \u0434\u043e\u0441\u0442\u0443\u043f\u0430:', font=('', 8)).pack(anchor=tk.W)
        self.filter_free = tk.StringVar(value='all')
        typ_combo = ttk.Combobox(left, textvariable=self.filter_free, state='readonly', values=['all', 'free', 'paid'])
        typ_combo.pack(fill=tk.X, pady=(0, 8))
        self.filter_free.trace('w', lambda *a: self._refresh_table())
        ttk.Separator(left, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        ttk.Label(left, text='Статистика', font=('', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        self.lbl_total = ttk.Label(left, text='Всего: 0'); self.lbl_total.pack(anchor=tk.W)
        self.lbl_ok = ttk.Label(left, text='Работает: 0', foreground='green'); self.lbl_ok.pack(anchor=tk.W)
        self.lbl_fail = ttk.Label(left, text='Не работает: 0', foreground='red'); self.lbl_fail.pack(anchor=tk.W)
        self.lbl_untested = ttk.Label(left, text='Не проверено: 0', foreground='gray'); self.lbl_untested.pack(anchor=tk.W)

        right = ttk.Frame(mf)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        pw = ttk.PanedWindow(right, orient=tk.VERTICAL)
        pw.pack(fill=tk.BOTH, expand=True)
        top_frame = ttk.Frame(pw)
        tf = ttk.Frame(top_frame)
        tf.pack(fill=tk.BOTH, expand=True)
        cols = ('provider', 'model', 'id', 'source', 'status', 'response', 'time')
        self.tree = ttk.Treeview(tf, columns=cols, show='headings', selectmode='extended')
        self.cols = [('provider', 110, 'Провайдер'), ('model', 200, 'Модель'), ('id', 200, 'ID модели'), ('source', 70, 'Ист.'), ('status', 70, 'Статус'), ('response', 240, 'Ответ'), ('time', 65, 'Время')]
        for c, w, h in self.cols:
            self.tree.heading(c, text=h, command=lambda col=c: self._sort_by(col))
            self.tree.column(c, width=w, minwidth=50)
        vsb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tf, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tf.grid_rowconfigure(0, weight=1); tf.grid_columnconfigure(0, weight=1)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)
        self.progress = ttk.Progressbar(top_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(3, 0))
        pw.add(top_frame, weight=3)
        lf = ttk.LabelFrame(pw, text='Лог')
        pw.add(lf, weight=1)
        self.log = tk.Text(lf, height=self.log_height_val.get(), wrap=tk.WORD, state=tk.DISABLED, font=('Consolas', 9))
        lsb = ttk.Scrollbar(lf, command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); lsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Цвета логов
        self.log.tag_config('info', foreground='black')
        self.log.tag_config('success', foreground='green')
        self.log.tag_config('warn', foreground='orange')
        self.log.tag_config('error', foreground='red')
        if self.dark_mode.get():
            self.log.tag_config('info', foreground='white')
            self.log.config(bg='#1e1e1e', fg='white', insertbackground='white')

    def _build_statusbar(self):
        self.statusbar = ttk.Label(self.root, text='Готов', relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ── Data ───────────────────────────────────────────────────────

    def _load_builtin(self):
        self.model_list = []

    def _rebuild_provider_filter(self):
        names = ['all']
        for pn in sorted(self.providers.keys()):
            mc = len(self.providers[pn]['models'])
            names.append(pn)
        self.provider_combo['values'] = names

    def _purge_empty_providers(self):
        for pn in list(self.providers.keys()):
            if not self.providers[pn].get('models'):
                del self.providers[pn]

    def _reset_to_builtin(self):
        if not messagebox.askyesno('Сброс', 'Удалить все пользовательские модели,\nоставив только встроенный каталог?'):
            return
        self.providers = {}; self.results = {}; self.model_list = []
        self._load_builtin(); self._rebuild_provider_filter(); self._refresh_table()
        self._save_providers()
        self._log('Сброшено к встроенному каталогу')
        self._set_status('Встроенный каталог')

    def _load_opencode_file(self):
        p = filedialog.askopenfilename(title='Выберите opencode.jsonc',
                                       filetypes=[('JSONC', '*.jsonc'), ('JSON', '*.json'), ('All', '*.*')])
        if not p:
            return
        try:
            cfg = read_jsonc(p)
            added = 0
            for pn, pc in cfg.get('provider', {}).items():
                pd = pc.get('name', pn)
                o = pc.get('options', {})
                bu = o.get('baseURL', '').rstrip('/')
                ak = o.get('apiKey', '')
                aks = o.get('apiKeys', [])
                if ak and ak not in aks:
                    aks = [ak] + aks
                if pd not in self.providers:
                    self.providers[pd] = {'base_url': bu, 'api_key': aks[0] if aks else ak, 'api_keys': aks, 'models': {}}
                else:
                    if bu:
                        self.providers[pd]['base_url'] = bu
                    for k in aks:
                        if k and k not in self.providers[pd].get('api_keys', []):
                            self.providers[pd].setdefault('api_keys', []).append(k)
                    if not self.providers[pd].get('api_keys') and ak:
                        self.providers[pd]['api_keys'] = [ak]
                        self.providers[pd]['api_key'] = ak
                prov = self.providers[pd]
                for mid, mc in pc.get('models', {}).items():
                    dup = False
                    for pv in self.providers.values():
                        if mid in pv.get('models', {}):
                            dup = True
                            break
                    if dup:
                        continue
                    mn = mc.get('name', mid)
                    if mid not in prov['models']:
                        prov['models'][mid] = {'name': mn, 'source': 'opencode'}
                        self.model_list.append((pd, mid, mn, 'opencode', False))
                        added += 1
            self._purge_empty_providers()
            self._rebuild_provider_filter()
            self._save_providers()
            self._refresh_table()
            self._log('Загружен %s: %d новых моделей' % (os.path.basename(p), added))
            self._set_status('Конфиг загружен')
        except Exception as e:
            messagebox.showerror('Ошибка', 'Не удалось загрузить конфиг:\n%s' % e)
            self._log('Ошибка загрузки %s: %s' % (p, e))

    def _add_custom_model(self):
        dlg = tk.Toplevel(self.root); dlg.title('Добавить пользовательскую модель')
        dlg.geometry('460x240'); dlg.resizable(False, False)
        dlg.transient(self.root); dlg.grab_set()
        f = ttk.Frame(dlg, padding=18); f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text='\u041f\u0440\u043e\u0432\u0430\u0439\u0434\u0435\u0440 (выберите или введите новый):',
                  font=('', 9)).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        pv = tk.StringVar()
        prov_vals = sorted(self.providers.keys())
        pc = ttk.Combobox(f, textvariable=pv, values=prov_vals, state='normal')
        pc.grid(row=1, column=0, columnspan=2, sticky=tk.EW, padx=0, pady=(0, 8))
        if prov_vals:
            pc.set(prov_vals[0])
        ttk.Label(f, text='ID \u043c\u043e\u0434\u0435\u043b\u0438:', font=('', 9)).grid(row=2, column=0, sticky=tk.W, pady=3)
        mv = tk.StringVar()
        ttk.Entry(f, textvariable=mv, width=35).grid(row=2, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
        ttk.Label(f, text='\u0418\u043c\u044f (\u043e\u043f\u0446\u0438\u043e\u043d\u0430\u043b\u044c\u043d\u043e):', font=('', 9)).grid(row=3, column=0, sticky=tk.W, pady=3)
        nv = tk.StringVar()
        ttk.Entry(f, textvariable=nv, width=35).grid(row=3, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
        f.grid_columnconfigure(1, weight=1)
        def do():
            pr = pv.get().strip(); mi = mv.get().strip(); nm = nv.get().strip() or mi
            if not pr or not mi: messagebox.showwarning('Ошибка', 'Провайдер и ID обязательны.'); return
            if pr not in self.providers:
                self.providers[pr] = {'base_url': 'https://api.freetheai.xyz/v1', 'api_key': '', 'api_keys': [], 'models': {}}
            if mi in self.providers[pr]['models']: messagebox.showwarning('Ошибка', 'Модель уже существует.'); return
            self.providers[pr]['models'][mi] = {'name': nm, 'source': 'custom'}
            self.model_list.append((pr, mi, nm, 'custom', False))
            self._rebuild_provider_filter(); self._refresh_table()
            self._save_providers()
            self._log('Добавлена модель: %s / %s' % (pr, mi)); dlg.destroy()
        bf = ttk.Frame(f); bf.grid(row=4, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(bf, text='Добавить', style='Accent.TButton', command=do).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text='Отмена', command=dlg.destroy).pack(side=tk.LEFT)

    def _remove_custom_models(self):
        n = sum(1 for x in self.model_list if x[3] == 'custom')
        if n == 0: messagebox.showinfo('Инфо', 'Нет пользовательских моделей.'); return
        if not messagebox.askyesno('Удалить', 'Удалить все пользовательские модели (%d шт.)?' % n): return
        self.model_list = [x for x in self.model_list if x[3] != 'custom']
        for p in self.providers.values():
            p['models'] = {k: v for k, v in p['models'].items() if v.get('source') != 'custom'}
        self.providers = {k: v for k, v in self.providers.items() if v['models']}
        self._rebuild_provider_filter(); self._refresh_table()
        self._save_providers()
        self._log('Пользовательские модели удалены')

    def _show_providers_dialog(self):
        dlg = tk.Toplevel(self.root); dlg.title('Управление провайдерами (ключи / URL)')
        dlg.geometry('720x520'); dlg.transient(self.root); dlg.grab_set()
        f = ttk.Frame(dlg, padding=10); f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text='Настройка API-ключей и URL для каждого провайдера:', font=('', 9, 'bold')).pack(anchor=tk.W)
        cv = tk.Canvas(f, highlightthickness=0)
        sb = ttk.Scrollbar(f, orient=tk.VERTICAL, command=cv.yview)
        sf = ttk.Frame(cv)
        sf.bind('<Configure>', lambda e: cv.configure(scrollregion=cv.bbox('all')))
        cv.create_window((0, 0), window=sf, anchor='nw')
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); sb.pack(side=tk.RIGHT, fill=tk.Y)
        def mw(e): cv.yview_scroll(int(-1*(e.delta/120)), 'units')
        cv.bind_all('<MouseWheel>', mw)
        dlg.bind('<Destroy>', lambda e: cv.unbind_all('<MouseWheel>'))
        entries = {}; row = 0
        for pn in sorted(self.providers.keys()):
            p = self.providers[pn]; mc = len(p['models'])
            # Заголовок провайдера
            ttk.Label(sf, text=pn, font=('', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(10, 0))
            ttk.Label(sf, text='%d моделей' % mc, foreground='gray').grid(row=row, column=1, sticky=tk.W, pady=(10, 0)); row += 1
            # URL
            ttk.Label(sf, text='URL:', font=('', 8)).grid(row=row, column=0, sticky=tk.W, padx=(15, 0))
            uv = tk.StringVar(value=p.get('base_url', ''))
            ttk.Entry(sf, textvariable=uv, width=58).grid(row=row, column=1, sticky=tk.EW, padx=5, pady=1); row += 1
            # Ключи — красивый выпадающий список
            ttk.Label(sf, text='\u041a\u043b\u044e\u0447\u0438:', font=('', 8)).grid(row=row, column=0, sticky=tk.NW, padx=(15, 5), pady=(6, 0))
            kf = ttk.Frame(sf)
            kf.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=2)
            key_list = p.get('api_keys', [p.get('api_key', '')] if p.get('api_key') else [])
            # Выпадающий список ключей
            kv = tk.StringVar(value=key_list[0] if key_list else '')
            key_combo = ttk.Combobox(kf, textvariable=kv, values=key_list, state='readonly', width=55)
            key_combo.pack(fill=tk.X)
            key_combo.bind('<<ComboboxSelected>>', lambda e, c=key_combo, l=key_list: None)
            # Панель управления ключами
            ctl = ttk.Frame(kf)
            ctl.pack(fill=tk.X, pady=(3, 0))
            new_key_var = tk.StringVar()
            entry_key = ttk.Entry(ctl, textvariable=new_key_var, width=35, show='*')
            entry_key.pack(side=tk.LEFT, padx=(0, 3))
            show_kvar = tk.BooleanVar()
            ttk.Checkbutton(ctl, text='\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c', variable=show_kvar,
                            command=lambda e=entry_key, v=show_kvar: e.configure(show='' if v.get() else '*')).pack(side=tk.LEFT)
            def add_key(cb=key_combo, ek=entry_key, nkv=new_key_var):
                k = nkv.get().strip()
                if k:
                    vals = list(cb['values']) if cb['values'] else []
                    if k not in vals:
                        vals.append(k)
                        cb['values'] = vals
                    cb.set(k)
                    nkv.set('')
                    ek.delete(0, tk.END)
            def remove_key(cb=key_combo):
                cur = cb.get()
                vals = list(cb['values']) if cb['values'] else []
                if cur in vals:
                    vals.remove(cur)
                    cb['values'] = vals
                    cb.set(vals[0] if vals else '')
            ttk.Button(ctl, text='+', width=3, command=add_key).pack(side=tk.LEFT, padx=2)
            ttk.Button(ctl, text='\u2212', width=3, command=remove_key).pack(side=tk.LEFT)
            ttk.Button(ctl, text='\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c', width=10,
                       command=lambda pn=pn, cb=key_combo: self._test_provider_keys(pn, cb)).pack(side=tk.LEFT, padx=5)
            row += 1
            entries[pn] = (uv, key_combo)
        sf.grid_columnconfigure(1, weight=1)
        def save():
            for pn, (uv, cb) in entries.items():
                self.providers[pn]['base_url'] = uv.get().strip()
                keys = list(cb['values']) if cb['values'] else []
                self.providers[pn]['api_keys'] = keys
                self.providers[pn]['api_key'] = cb.get() or (keys[0] if keys else '')
            self._save_providers()
            self._log('Настройки провайдеров сохранены'); dlg.destroy()
        bf = ttk.Frame(f); bf.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(bf, text='Сохранить', command=save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bf, text='Отмена', command=dlg.destroy).pack(side=tk.RIGHT)

    def _test_provider_keys(self, provider_name, key_combo):
        """Проверяет все ключи провайдера на валидность и отмечает рабочий."""
        p = self.providers.get(provider_name)
        if not p or not p.get('models'):
            self._log('\u041d\u0435\u0442 \u043c\u043e\u0434\u0435\u043b\u0435\u0439 \u0434\u043b\u044f \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438 \u043a\u043b\u044e\u0447\u0435\u0439: %s' % provider_name)
            return
        keys = list(key_combo['values']) if key_combo['values'] else []
        if not keys:
            self._log('\u041d\u0435\u0442 \u043a\u043b\u044e\u0447\u0435\u0439 \u0434\u043b\u044f \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438: %s' % provider_name)
            return
        base_url = p.get('base_url', '').rstrip('/') + '/chat/completions'
        model_id = p['models'][0] if isinstance(p['models'][0], str) else p['models'][0].get('model', '')
        self._log('\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u043a\u043b\u044e\u0447\u0435\u0439 %s (\u0447\u0435\u0440\u0435\u0437 %s)...' % (provider_name, model_id))
        import threading
        results = {}
        def test_single(key):
            try:
                body = json.dumps({
                    'model': model_id,
                    'messages': [{'role': 'user', 'content': 'say ok'}],
                    'max_tokens': 5,
                })
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + key,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Origin': 'https://opencode.ai',
                    'Referer': 'https://opencode.ai/',
                }
                code, resp_text = http_post(base_url, body, headers, timeout=15)
                try:
                    data = json.loads(resp_text)
                except Exception:
                    raw = resp_text.strip()[:100]
                    reason = 'Cloudflare/блокировка' if code == 403 else ('HTTP %d' % code)
                    results[key] = (False, raw or reason)
                    return
                if code == 200:
                    results[key] = (True, '\u0420\u0430\u0431\u043e\u0442\u0430\u0435\u0442')
                    return
                err = data.get('error', {}).get('message', '') or ''
                desc = ERR_DESC.get(code, '')
                tag = 'HTTP %d' % code
                if code == 429:
                    tag = 'RATE'
                    if ('limit' in err.lower() or 'quota' in err.lower()) and err:
                        results[key] = (False, '%s: %s' % (tag, err[:60]))
                        return
                results[key] = (False, '%s: %s' % (tag, (desc or err)[:60]))
            except Exception as e:
                results[key] = (False, '\u041e\u0448\u0438\u0431\u043a\u0430: %s' % str(e)[:60])
        threads = []
        for k in keys:
            t = threading.Thread(target=test_single, args=(k,))
            t.start(); threads.append(t)
        for t in threads:
            t.join(timeout=20)
        # Выбираем первый рабочий ключ, иначе первый не-429, иначе первый
        working = [k for k, (ok, _) in results.items() if ok]
        non_rate = [k for k, (ok, msg) in results.items() if not ok and not msg.startswith('RATE')]
        chosen = working[0] if working else (non_rate[0] if non_rate else keys[0])
        key_combo.set(chosen)
        # Лог результатов
        for k in keys:
            ok, msg = results.get(k, (False, '\u043d\u0435\u0442 \u043e\u0442\u0432\u0435\u0442\u0430'))
            status = '\u2713' if ok else '\u2717'
            note = ' \u2190 \u0432\u044b\u0431\u0440\u0430\u043d' if k == chosen and ok else ''
            self._log('%s %s: %s%s' % (status, k[:48], msg, note))
        if working:
            self._log('\u041a\u043b\u044e\u0447 \u0432\u044b\u0431\u0440\u0430\u043d: %s' % chosen[:48])
        else:
            self._log('\u041d\u0435\u0442 \u0440\u0430\u0431\u043e\u0447\u0438\u0445 \u043a\u043b\u044e\u0447\u0435\u0439, \u0432\u044b\u0431\u0440\u0430\u043d: %s' % chosen[:48])

    def _show_settings(self):
        dlg = tk.Toplevel(self.root); dlg.title('Настройки'); dlg.geometry('350x180')
        dlg.transient(self.root); dlg.grab_set()
        f = ttk.Frame(dlg, padding=15); f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text='Таймаут (сек):').grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(f, from_=5, to=120, textvariable=self.timeout_val, width=8).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(f, text='Повторов:').grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(f, from_=0, to=5, textvariable=self.retries_val, width=8).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(f, text='Задержка (сек):').grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(f, from_=0.0, to=5.0, increment=0.1, textvariable=self.delay_val, width=8).grid(row=2, column=1, sticky=tk.W, padx=5)
        def save_set():
            self._save_settings(); dlg.destroy()
        ttk.Button(f, text='OK', command=save_set).grid(row=3, column=0, columnspan=2, pady=12)

    # ── Save / Load provider settings ──────────────────────────────

    def _save_providers(self):
        data = {}
        for pn, p in self.providers.items():
            data[pn] = {
                'base_url': p.get('base_url', ''),
                'api_key': p.get('api_key', ''),
                'api_keys': p.get('api_keys', []),
            }
        try:
            with open(PROVIDERS_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_providers(self):
        cfg = None
        try:
            cfg = read_jsonc(os.path.expanduser('~/.config/opencode/opencode.jsonc'))
        except Exception:
            try:
                cfg = read_jsonc(os.path.expanduser('~/.config/opencode/opencode.json'))
            except Exception:
                try:
                    cfg = read_jsonc(r'C:\Users\msi\.config\opencode\opencode.jsonc')
                except Exception:
                    pass
        if cfg:
            total = 0
            for pn, pc in cfg.get('provider', {}).items():
                opts = pc.get('options', {})
                base_url = (opts.get('baseURL') or '').rstrip('/')
                api_keys = opts.get('apiKeys', [])
                api_key = opts.get('apiKey', '')
                if not api_keys and api_key:
                    api_keys = [api_key]
                if not api_keys:
                    continue
                if pn not in self.providers:
                    self.providers[pn] = {}
                self.providers[pn] = {
                    'base_url': base_url,
                    'api_key': api_keys[0] if api_keys else api_key,
                    'api_keys': api_keys,
                    'models': {},
                }
                for mid, mc in pc.get('models', {}).items():
                    mn = mc.get('name', mid)
                    is_free = 'free' in mid.lower() or 'free' in mn.lower()
                    self.providers[pn]['models'][mid] = {
                        'name': mn,
                        'source': 'opencode',
                        'free': is_free,
                    }
                    self.model_list.append((pn, mid, mn, 'opencode', is_free))
                    total += 1
            self._log('Загружено из opencode.jsonc: %d моделей' % total)
        else:
            self._log('Не удалось загрузить opencode.jsonc')

    def _save_settings(self):
        data = {
            'timeout': self.timeout_val.get(),
            'retries': self.retries_val.get(),
            'delay': self.delay_val.get(),
            'dark_mode': self.dark_mode.get(),
            'geometry': self.geometry_val.get(),
            'log_height': self.log_height_val.get(),
            'auto_save_config': self.auto_save_config.get(),
            'auto_start_ollama': self.auto_start_ollama.get(),
            'hide_ollama_window': self.hide_ollama_window.get(),
        }
        try:
            with open(SETTINGS_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_settings(self):
        if not os.path.isfile(SETTINGS_JSON):
            return
        try:
            with open(SETTINGS_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for key in ('timeout', 'retries', 'delay', 'dark_mode', 'geometry', 'log_height', 'auto_save_config', 'auto_start_ollama', 'hide_ollama_window'):
                if key in data:
                    getattr(self, key + '_val' if key in ('timeout', 'retries', 'delay', 'geometry', 'log_height') else key).set(data[key])
        except Exception:
            pass

    def _propagate_keys(self):
        """Копирует все ключи от провайдера с непустыми ключами на всех остальных
        с тем же base_url."""
        source_keys = []
        source_url = ''
        for p in self.providers.values():
            if p.get('api_keys'):
                source_keys = p['api_keys']
                source_url = p.get('base_url', '')
                break
        if not source_keys:
            return
        for p in self.providers.values():
            if not p.get('api_keys') and p.get('base_url') == source_url:
                p['api_keys'] = list(source_keys)
                if not p.get('api_key') and source_keys:
                    p['api_key'] = source_keys[0]

    def _check_server_online(self, pn, bu):
        try:
            parsed = urlparse(bu)
            host = parsed.hostname or 'localhost'
            port = parsed.port or 11434
            s = socket.create_connection((host, port), timeout=2)
            s.close()
            return True
        except Exception:
            return False

    def _ensure_ollama_running(self):
        import subprocess
        if not self.auto_start_ollama.get():
            return
        if self._check_server_online('Ollama', 'http://localhost:11434'):
            self._log('Ollama уже запущен')
            return
        self._log('Ollama не запущен, запускаю сервер скрыто...')
        print('[Ollama] сервер не запущен, запускаю сервер скрыто...')
        try:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen([r'C:\Users\msi\AppData\Local\Programs\Ollama\ollama.exe', 'serve'],
                             creationflags=subprocess.CREATE_BREAKAWAY_FROM_JOB | CREATE_NO_WINDOW)
        except Exception as e:
            self._log('Ошибка запуска Ollama: %s' % str(e)[:60])
            print('[Ollama] ошибка запуска: %s' % str(e)[:60])
            return
        for _ in range(30):
            time.sleep(1)
            if self._check_server_online('Ollama', 'http://localhost:11434'):
                self._log('Ollama успешно запущен')
                print('[Ollama] сервер запущен')
                return
        self._log('Ollama не удалось запустить (таймаут 30с)')
        print('[Ollama] не удалось запустить сервер')

    def _on_close(self):
        self.geometry_val.set(self.root.geometry())
        # Попытка сохранить высоту лога (из lauch lauch)
        try:
            # Для ttk.PanedWindow сложно получить точный размер sash, 
            # поэтому сохраняем общую геометрию окна.
            pass
        except: pass
        self._save_settings()
        self.root.destroy()

    def _auto_validate_keys(self):
        def _run():
            for pn, p in self.providers.items():
                keys = p.get('api_keys', [])
                if not keys:
                    continue
                bu = p.get('base_url', '').rstrip('/')
                if not bu:
                    continue
                cache_key = bu
                with VALID_KEYS_LOCK:
                    if cache_key in VALID_KEYS_CACHE:
                        continue
                if not self._check_server_online(pn, bu):
                    if 'localhost' in bu or '127.0.0.1' in bu:
                        self._log('  %s: сервер не запущен' % pn)
                        print('[%s] сервер не запущен' % pn)
                        with VALID_KEYS_LOCK:
                            VALID_KEYS_CACHE[cache_key] = []
                        continue
                self._log('Проверка ключей %s (%s)...' % (pn, _key_fmt(len(keys))))
                valid = validate_keys(bu, keys, provider_models=p['models'], provider_name=pn, timeout=10)
                with VALID_KEYS_LOCK:
                    VALID_KEYS_CACHE[cache_key] = valid
                if valid:
                    self._log('  %s: работает %s' % (pn, _key_fmt(len(valid), len(keys))))
                else:
                    self._log('  %s: нет рабочих ключей' % pn)
                self.root.after(0, self._refresh_table)
                if self.auto_save_config.get():
                    self._save_to_opencode_config()
        threading.Thread(target=_run, daemon=True).start()

    def _save_to_opencode_config(self):
        import shutil
        cfg_path = r'C:\Users\msi\.config\opencode\opencode.jsonc'
        if not os.path.isfile(cfg_path):
            self._log('Конфиг opencode.jsonc не найден')
            return
        try:
            cfg = read_jsonc(cfg_path)
        except Exception as e:
            self._log('Ошибка чтения opencode.jsonc: %s' % e)
            return
        changed = False
        for pn, p in self.providers.items():
            if pn not in cfg.get('provider', {}):
                continue
            cache_key = p.get('base_url', '')
            with VALID_KEYS_LOCK:
                valid = VALID_KEYS_CACHE.get(cache_key, [])
            if not valid:
                continue
            pc = cfg['provider'].get(pn, {})
            opts = pc.get('options', {})
            existing_keys = opts.get('apiKeys', [])
            need = [k for k in valid if k not in existing_keys]
            if need:
                cfg['provider'][pn]['options']['apiKeys'] = valid + [k for k in existing_keys if k not in valid]
                cfg['provider'][pn]['options']['apiKey'] = valid[0]
                changed = True
        if changed:
            backup = cfg_path + '.bak'
            if not os.path.isfile(backup):
                try:
                    shutil.copy2(cfg_path, backup)
                    self._log('Создан бэкап: opencode.jsonc.bak')
                except Exception:
                    pass
            save_jsonc(cfg_path, cfg)
            self._log('Конфиг opencode.jsonc обновлен валидными ключами')
        else:
            self._log('Обновление конфига не потребовалось (ключи уже актуальны)')

    def _sort_by(self, col):
        """Сортировка таблицы по клику на заголовок."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(key=lambda x: x[0].lower(), reverse=self.sort_rev if self.sort_col == col else False)
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, '', idx)
        if self.sort_col == col:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col = col
            self.sort_rev = False
        arrow = '\u25b2' if self.sort_rev else '\u25bc'
        for c, _w, h in self.cols:
            self.tree.heading(c, text=h + (' ' + arrow if c == col else ''))

    # ── Table operations ──────────────────────────────────────────

    def _refresh_table(self, *_):
        for i in self.tree.get_children():
            self.tree.delete(i)
        pf = self.filter_provider_s.get(); sf = self.filter_status.get(); fc = self.filter_source.get(); ff = self.filter_free.get()
        total = ok = fail = unt = 0
        for pn, mid, mn, src, fr in self.model_list:
            if pf != 'all' and pn != pf: continue
            if fc != 'all' and src != fc: continue
            if ff == 'free' and not fr: continue
            if ff == 'paid' and fr: continue
            r = self.results.get(pn, {}).get(mid)
            if r is None:
                if sf not in ('all', 'untested'): continue
                st, resp, el, tg = '\u2014', '', '', ('untested',); unt += 1
            elif r['ok']:
                if sf not in ('all', 'yes'): continue
                st, resp, el, tg = '\u0423\u0421\u041f\u0415\u0425', r['msg'], '%.1fs' % r['elapsed'], ('ok',); ok += 1
            else:
                if sf not in ('all', 'no'): continue
                st, resp, el, tg = '\u041d\u0415\u0423\u0414\u0410\u0427\u0410', r['msg'], '%.1fs' % r['elapsed'], ('fail',); fail += 1
            total += 1
            disp_name = mn + (' \U0001f193' if fr else '')
            self.tree.insert('', tk.END, values=(pn, disp_name, mid, src, st, resp, el), tags=tg)
        self.lbl_total.config(text='Всего: %d' % total)
        self.lbl_ok.config(text='Работает: %d' % ok)
        self.lbl_fail.config(text='Не работает: %d' % fail)
        self.lbl_untested.config(text='Не проверено: %d' % unt)

    def _on_double_click(self, e):
        sel = self.tree.selection()
        if sel:
            v = self.tree.item(sel[0], 'values')
            raw_name = v[1].replace(' \U0001f193', '')
            for pn, mid, mn, src, _fr in self.model_list:
                if pn == v[0] and mn == raw_name:
                    self.root.clipboard_clear(); self.root.clipboard_append(mid)
                    self._set_status('Скопировано: %s' % mid)
                    break

    def _on_right_click(self, e):
        iid = self.tree.identify_row(e.y)
        if not iid:
            return
        sel = self.tree.selection()
        if iid not in sel:
            self.tree.selection_set(iid)
            sel = (iid,)
        v = self.tree.item(sel[0], 'values')
        raw_name = v[1].replace(' \U0001f193', '')
        menu = tk.Menu(self.root, tearoff=0)
        cnt = len(sel)
        if cnt == 1:
            menu.add_command(label='\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u00ab' + raw_name[:40] + '\u00bb',
                             command=lambda: self._run_tests(self._items_from_sel(sel)))
            menu.add_command(label='\u041a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c ID \u043c\u043e\u0434\u0435\u043b\u0438',
                             command=lambda: self._copy_model_id(v, raw_name))
            resp = v[5]
            if resp:
                menu.add_command(label='\u041a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043e\u0442\u0432\u0435\u0442',
                                 command=lambda r=resp: self._copy_text(r, '\u041e\u0442\u0432\u0435\u0442 \u0441\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u043d'))
        else:
            menu.add_command(label='\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c %d \u0432\u044b\u0434\u0435\u043b\u0435\u043d\u043d\u044b\u0445' % cnt,
                             command=lambda: self._run_tests(self._items_from_sel(sel)))
            menu.add_command(label='\u041a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c ID %d \u043c\u043e\u0434\u0435\u043b\u0435\u0439' % cnt,
                             command=lambda: self._copy_ids_from_sel(sel))
            menu.add_command(label='\u041a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u043e\u0442\u0432\u0435\u0442\u044b %d \u043c\u043e\u0434\u0435\u043b\u0435\u0439' % cnt,
                             command=lambda: self._copy_responses_from_sel(sel))
        menu.add_separator()
        menu.add_command(label='\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u0432\u0441\u0435 \u043c\u043e\u0434\u0435\u043b\u0438 \u043f\u0440\u043e\u0432\u0430\u0439\u0434\u0435\u0440\u0430',
                         command=lambda: self._run_tests([x for x in self.model_list if x[0] == v[0]]))
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _items_from_sel(self, sel):
        out = []
        for iid in sel:
            v = self.tree.item(iid, 'values')
            rn = v[1].replace(' \U0001f193', '')
            for x in self.model_list:
                if x[0] == v[0] and x[2] == rn:
                    out.append(x); break
        return out

    def _copy_model_id(self, v, raw_name):
        for pn, mid, mn, _, _ in self.model_list:
            if pn == v[0] and mn == raw_name:
                self.root.clipboard_clear(); self.root.clipboard_append(mid)
                self._set_status('Скопировано: %s' % mid)
                break

    def _copy_ids_from_sel(self, sel):
        ids = []
        for iid in sel:
            v = self.tree.item(iid, 'values')
            rn = v[1].replace(' \U0001f193', '')
            for pn_, mid_, mn_, _, _ in self.model_list:
                if pn_ == v[0] and mn_ == rn:
                    ids.append(mid_); break
        txt = '\n'.join(ids)
        self.root.clipboard_clear(); self.root.clipboard_append(txt)
        self._set_status('\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u043d\u043e ID: %d \u043c\u043e\u0434\u0435\u043b\u0435\u0439' % len(ids))

    def _copy_text(self, text, status_msg):
        self.root.clipboard_clear(); self.root.clipboard_append(text)
        self._set_status(status_msg)

    def _copy_responses_from_sel(self, sel):
        lines = []
        for iid in sel:
            v = self.tree.item(iid, 'values')
            lines.append('%s | %s' % (v[1].replace(' \U0001f193', ''), v[5]))
        txt = '\n'.join(lines)
        self.root.clipboard_clear(); self.root.clipboard_append(txt)
        self._set_status('\u0421\u043a\u043e\u043f\u0438\u0440\u043e\u0432\u0430\u043d\u043e \u043e\u0442\u0432\u0435\u0442\u043e\u0432: %d' % len(lines))

    # ── Theme ──────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._apply_theme()
        self._refresh_table()
        self._save_settings()

    def _apply_theme(self):
        dark = self.dark_mode.get()
        style = ttk.Style()
        if dark:
            bg, fg, selbg, selfg = '#1e1e1e', '#e0e0e0', '#264f78', '#ffffff'
            entry_bg, entry_fg = '#2d2d2d', '#e0e0e0'
            tree_bg, tree_fg = '#252526', '#e0e0e0'
            text_bg, text_fg = '#1e1e1e', '#e0e0e0'
            select_bg = '#264f78'
            style.theme_use('clam')
            style.configure('.', background=bg, foreground=fg, fieldbackground=entry_bg,
                            selectbackground=selbg, selectforeground=selfg,
                            troughcolor='#3c3c3c', arrowcolor='#e0e0e0')
            style.configure('TLabel', background=bg, foreground=fg)
            style.configure('TFrame', background=bg)
            style.configure('TLabelframe', background=bg, foreground=fg)
            style.configure('TLabelframe.Label', background=bg, foreground=fg)
            style.configure('TButton', background='#3c3c3c', foreground=fg, bordercolor='#555')
            style.map('TButton', background=[('active', '#505050')])
            style.configure('Accent.TButton', font=('', 9, 'bold'), background='#0e639c', foreground='#ffffff')
            style.map('Accent.TButton', background=[('active', '#1177bb')])
            style.configure('TEntry', fieldbackground=entry_bg, foreground=entry_fg)
            style.configure('TSpinbox', fieldbackground=entry_bg, foreground=entry_fg)
            style.configure('TCombobox', fieldbackground=entry_bg, foreground=entry_fg, arrowcolor='#e0e0e0')
            style.map('TCombobox', fieldbackground=[('readonly', entry_bg)], foreground=[('readonly', entry_fg)])
            style.configure('Treeview', background=tree_bg, foreground=tree_fg, fieldbackground=tree_bg)
            style.map('Treeview', background=[('selected', select_bg)], foreground=[('selected', '#ffffff')])
            style.configure('Vertical.TScrollbar', background='#3c3c3c', troughcolor='#1e1e1e', arrowcolor='#e0e0e0')
            style.configure('Horizontal.TScrollbar', background='#3c3c3c', troughcolor='#1e1e1e', arrowcolor='#e0e0e0')
            style.configure('TProgressbar', background='#0e639c', troughcolor='#3c3c3c')
            style.configure('TSeparator', background='#3c3c3c')
            self.root.configure(bg=bg)
            self.log.configure(bg=text_bg, fg=text_fg, insertbackground=fg, selectbackground=selbg)
            self.statusbar.configure(background=bg, foreground=fg)
            self.root.option_add('*Menu.background', '#2d2d2d')
            self.root.option_add('*Menu.foreground', '#e0e0e0')
            self.root.option_add('*Menu.activeBackground', '#264f78')
            self.root.option_add('*Menu.activeForeground', '#ffffff')
        else:
            style.theme_use('vista' if 'vista' in style.theme_names() else 'clam')
            style.configure('TCombobox', padding=3, arrowsize=14)
            style.configure('Accent.TButton', font=('', 9, 'bold'))
            style.configure('Filter.TCombobox', arrowcolor='#555')
            self.root.configure(bg='SystemButtonFace')
            self.log.configure(bg='#ffffff', fg='#000000', insertbackground='#000000', selectbackground='#000080')
            self.statusbar.configure(background='SystemButtonFace', foreground='SystemWindowText')
            self.root.option_add('*Menu.background', 'SystemButtonFace')
            self.root.option_add('*Menu.foreground', 'SystemWindowText')
            self.root.option_add('*Menu.activeBackground', 'SystemHighlight')
            self.root.option_add('*Menu.activeForeground', 'SystemHighlightText')
        self.lbl_ok.config(foreground='#4ec94e' if dark else 'green')
        self.lbl_fail.config(foreground='#f44747' if dark else 'red')
        self.lbl_untested.config(foreground='#888888' if dark else 'gray')
        self.tree.tag_configure('ok', foreground='#4ec94e' if dark else 'green')
        self.tree.tag_configure('fail', foreground='#f44747' if dark else 'red')
        self.tree.tag_configure('untested', foreground='#888888' if dark else 'gray')

    # ── Testing ────────────────────────────────────────────────────

    def _start_all(self):
        pf = self.filter_provider_s.get()
        sf = self.filter_status.get()
        fc = self.filter_source.get()
        ff = self.filter_free.get()
        items = []
        for x in self.model_list:
            pn, mid, mn, src, fr = x
            if pf != 'all' and pn != pf: continue
            if fc != 'all' and src != fc: continue
            if ff == 'free' and not fr: continue
            if ff == 'paid' and fr: continue
            r = self.results.get(pn, {}).get(mid)
            if r is None:
                if sf not in ('all', 'untested'): continue
            elif r['ok']:
                if sf not in ('all', 'yes'): continue
            else:
                if sf not in ('all', 'no'): continue
            items.append(x)
        self._run_tests(items)

    def _start_selected(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo('Инфо', 'Выберите модели в таблице.'); return
        items = []
        for iid in sel:
            v = self.tree.item(iid, 'values')
            raw_name = v[1].replace(' \U0001f193', '')
            for pn, mid, mn, src, _fr in self.model_list:
                if pn == v[0] and mn == raw_name:
                    items.append((pn, mid, mn, src, _fr)); break
        self._run_tests(items)

    def _run_tests(self, items):
        if self.running or not items: return
        self.running = True; self.cancel_flag = False
        self.btn_all.config(state=tk.DISABLED); self.btn_sel.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.progress['maximum'] = len(items); self.progress['value'] = 0
        threading.Thread(target=self._worker, args=(items,), daemon=True).start()

    def _stop(self):
        if self.running: self.cancel_flag = True; self._log('Остановка...'); self._set_status('Остановка...')

    def _worker(self, items):
        to = self.timeout_val.get(); rt = self.retries_val.get(); dl = self.delay_val.get()
        batch_ok = 0
        for i, (pn, mid, mn, _, _) in enumerate(items):
            if self.cancel_flag: break
            p = self.providers.get(pn)
            if not p: continue
            keys = p.get('api_keys', [p['api_key']] if p.get('api_key') else [])
            if not keys:
                self._log('  \u041d\u0435\u0442 \u043a\u043b\u044e\u0447\u0435\u0439 \u0434\u043b\u044f %s' % pn)
                self.results.setdefault(pn, {})[mid] = {'ok': False, 'msg': '\u041d\u0435\u0442 API \u043a\u043b\u044e\u0447\u0435\u0439', 'elapsed': 0}
                continue
            self._log('  \u041a\u043b\u044e\u0447\u0435\u0439: %d, \u043f\u0440\u043e\u0431\u0443\u044e %s...' % (len(keys), pn))
            print('[WORK] %s / %s: keys=%d, url=%s' % (pn, mid, len(keys), p.get('base_url', '?')))
            ok_flag, msg, el = test_model(p['base_url'], keys, mid, timeout=to, retries=rt)
            self.results.setdefault(pn, {})[mid] = {'ok': ok_flag, 'msg': msg, 'elapsed': el}
            if ok_flag: batch_ok += 1
            self._log('  %s (%.1fs) %s' % ('\u0423\u0421\u041f\u0415\u0425' if ok_flag else '\u041d\u0415\u0423\u0414\u0410\u0427\u0410', el, msg))
            self.root.after(0, self._refresh_table)
            self.root.after(0, lambda v=i+1: self.progress.configure(value=v))
            if i < len(items)-1 and not self.cancel_flag: time.sleep(dl)
        self.root.after(0, lambda: self._on_done(batch_ok))

    def _on_done(self, batch_ok=0):
        self.running = False
        self.btn_all.config(state=tk.NORMAL); self.btn_sel.config(state=tk.NORMAL); self.btn_stop.config(state=tk.DISABLED)
        self._set_status('Готово')
        ok = fail = 0
        for pr in self.results.values():
            for r in pr.values():
                if r['ok']: ok += 1; continue
                fail += 1
        self._log('Завершено: %d УСПЕХ, %d НЕУДАЧА' % (ok, fail))
        if batch_ok > 0:
            def ask_save():
                if messagebox.askyesno('Сохранить конфиг',
                                       'Обнаружено %d работающих моделей.\n\nСохранить конфигурацию в opencode.jsonc\nтолько с работающими моделями?' % batch_ok):
                    self._export_dialog(preselect_ok_only=True)
            self.root.after(100, ask_save)

    # ── Export to opencode.jsonc ──────────────────────────────────

    def _export_dialog(self, preselect_ok_only=False):
        dlg = tk.Toplevel(self.root); dlg.title('\u042d\u043a\u0441\u043f\u043e\u0440\u0442 \u0432 opencode.jsonc')
        dlg.geometry('720x650'); dlg.transient(self.root); dlg.grab_set()
        f = ttk.Frame(dlg, padding=10); f.pack(fill=tk.BOTH, expand=True)

        # Путь
        pf = ttk.Frame(f); pf.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(pf, text='\u041f\u0443\u0442\u044c:').pack(side=tk.LEFT)
        path_v = tk.StringVar(value=os.path.join(SCRIPT_DIR, 'opencode.jsonc'))
        ttk.Entry(pf, textvariable=path_v, width=55).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(pf, text='\u041e\u0431\u0437\u043e\u0440', command=lambda: path_v.set(
            filedialog.asksaveasfilename(title='\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u043a\u043e\u043d\u0444\u0438\u0433',
                                         defaultextension='.jsonc',
                                         filetypes=[('JSONC', '*.jsonc'), ('JSON', '*.json'), ('All', '*.*')],
                                         initialfile=os.path.basename(path_v.get()),
                                         initialdir=os.path.dirname(path_v.get())) or path_v.get())
                  ).pack(side=tk.LEFT)
        # Бэкап
        bkup_v = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text='\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0431\u044d\u043a\u0430\u043f \u043e\u0440\u0438\u0433\u0438\u043d\u0430\u043b\u0430 \u0441 \u0434\u0430\u0442\u043e\u0439', variable=bkup_v).pack(anchor=tk.W)

        # Treeview с чекбоксами
        ttk.Label(f, text='\u041c\u043e\u0434\u0435\u043b\u0438 (\u043e\u0442\u043c\u0435\u0442\u044c\u0442\u0435 \u043d\u0443\u0436\u043d\u044b\u0435, \u0438\u0437\u043c\u0435\u043d\u0438\u0442\u0435 \u043f\u043e\u0440\u044f\u0434\u043e\u043a):', font=('', 9, 'bold')).pack(anchor=tk.W, pady=(5, 2))
        tvf = ttk.Frame(f); tvf.pack(fill=tk.BOTH, expand=True)
        tv = ttk.Treeview(tvf, columns=('chk', 'name', 'info'), show='tree', selectmode='browse', height=14)
        tv.heading('#0', text='')
        tv.column('#0', width=0, stretch=False)
        tv.column('chk', width=30, anchor=tk.CENTER)
        tv.column('name', width=300)
        tv.column('info', width=120)
        v_sb = ttk.Scrollbar(tvf, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=v_sb.set)
        tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); v_sb.pack(side=tk.RIGHT, fill=tk.Y)
        # Кнопки реордеринга
        rbf = ttk.Frame(f); rbf.pack(fill=tk.X, pady=3)
        def move_up():
            sel = tv.selection()
            if not sel: return
            iid = sel[0]
            parent = tv.parent(iid)
            siblings = tv.get_children(parent)
            idx = siblings.index(iid)
            if idx > 0:
                tv.move(iid, parent, idx - 1)
                tv.selection_set(iid)
                tv.focus(iid)
        def move_down():
            sel = tv.selection()
            if not sel: return
            iid = sel[0]
            parent = tv.parent(iid)
            siblings = tv.get_children(parent)
            idx = siblings.index(iid)
            if idx < len(siblings) - 1:
                tv.move(iid, parent, idx + 1)
                tv.selection_set(iid)
                tv.focus(iid)
        def move_top():
            sel = tv.selection()
            if not sel: return
            iid = sel[0]
            parent = tv.parent(iid)
            tv.move(iid, parent, 0)
            tv.selection_set(iid); tv.focus(iid)
        def move_bottom():
            sel = tv.selection()
            if not sel: return
            iid = sel[0]
            parent = tv.parent(iid)
            tv.move(iid, parent, len(tv.get_children(parent)))
            tv.selection_set(iid); tv.focus(iid)
        ttk.Label(rbf, text='\u041f\u043e\u0440\u044f\u0434\u043e\u043a:').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(rbf, text='\u25b2 \u0412\u0432\u0435\u0440\u0445', width=10, command=move_up).pack(side=tk.LEFT, padx=1)
        ttk.Button(rbf, text='\u25bc \u0412\u043d\u0438\u0437', width=10, command=move_down).pack(side=tk.LEFT, padx=1)
        ttk.Button(rbf, text='\u2b06 \u0412 \u043d\u0430\u0447\u0430\u043b\u043e', width=12, command=move_top).pack(side=tk.LEFT, padx=1)
        ttk.Button(rbf, text='\u2b07 \u0412 \u043a\u043e\u043d\u0435\u0446', width=12, command=move_bottom).pack(side=tk.LEFT, padx=1)

        # Заполнение дерева
        chk_state = {}  # iid -> bool
        prov_nodes = {}  # provider_name -> iid
        seen_provs = []
        prov_models = {}
        for pn, mid, mn, src, fr in self.model_list:
            if pn not in prov_models:
                prov_models[pn] = []; seen_provs.append(pn)
            prov_models[pn].append((mid, mn, src, fr))
        for pn in seen_provs:
            r = self.results.get(pn, {})
            piid = tv.insert('', tk.END, values=('', pn, ''), tags=('provider',))
            prov_nodes[pn] = piid
            chk_state[piid] = True
            tv.set(piid, 'chk', '\u2611')
            # Определяем, есть ли у моделей префикс [GROUP]
            raw = prov_models[pn]
            has_prefix = any(mn.startswith('[') for _, mn, _, _ in raw)
            if has_prefix:
                subgroups = {}
                for mid, mn, src, fr in raw:
                    close = mn.index(']')
                    grp = mn[1:close]
                    clean = mn[close+1:].strip()
                    subgroups.setdefault(grp, []).append((mid, clean, src, fr))
                for grp_name in sorted(subgroups.keys(), key=lambda x: ('z' if any(m[3] for m in subgroups[x]) else 'a') + x):
                    giid = tv.insert(piid, tk.END, values=('', grp_name, ''), tags=('subgroup',))
                    chk_state[giid] = True
                    tv.set(giid, 'chk', '\u2611')
                    for mid, clean_name, src, fr in subgroups[grp_name]:
                        res = r.get(mid)
                        if res is None:
                            info = '\u2014'
                        elif res['ok']:
                            info = '\u0423\u0421\u041f\u0415\u0425'
                        else:
                            info = '\u041d\u0415\u0423\u0414\u0410\u0427\u0410'
                        miid = tv.insert(giid, tk.END, values=('', clean_name, info), tags=('model',))
                        chk_state[miid] = True
                        tv.set(miid, 'chk', '\u2611')
                    tv.item(giid, open=True)
            else:
                # Плоские модели (без префикса) — сразу под провайдера
                for mid, mn, src, fr in raw:
                    res = r.get(mid)
                    if res is None:
                        info = '\u2014'
                    elif res['ok']:
                        info = '\u0423\u0421\u041f\u0415\u0425'
                    else:
                        info = '\u041d\u0415\u0423\u0414\u0410\u0427\u0410'
                    miid = tv.insert(piid, tk.END, values=('', mn, info), tags=('model',))
                    chk_state[miid] = True
                    tv.set(miid, 'chk', '\u2611')
            tv.item(piid, open=True)

        # Переключение чекбоксов (3 уровня: провайдер → подгруппа → модель)
        tv.tag_configure('dim', foreground='#888888')
        def _update_vis(iid):
            tags = list(tv.item(iid, 'tags'))
            if chk_state.get(iid, False):
                tags = [t for t in tags if t != 'dim']
            elif 'dim' not in tags:
                tags.append('dim')
            tv.item(iid, tags=tuple(tags))
        def _model_count(iid):
            """Рекурсивно считает сколько моделей-листьев отмечено из скольких."""
            kids = tv.get_children(iid)
            if not kids:
                return (1 if chk_state.get(iid, False) else 0, 1)
            ok, total = 0, 0
            for k in kids:
                c, t = _model_count(k)
                ok += c; total += t
            return ok, total
        def _set_tree_state(iid, checked):
            """Устанавливает состояние на iid и всех его потомках."""
            chk_state[iid] = checked
            tv.set(iid, 'chk', '\u2611' if checked else '\u2610')
            _update_vis(iid)
            for k in tv.get_children(iid):
                _set_tree_state(k, checked)
        def _update_up(iid):
            """Пересчитывает и обновляет родителя iid на основе моделей-листьев."""
            parent = tv.parent(iid)
            if parent:
                ok, total = _model_count(parent)
                if ok == 0:
                    tv.set(parent, 'chk', '\u2610'); chk_state[parent] = False
                elif ok == total:
                    tv.set(parent, 'chk', '\u2611'); chk_state[parent] = True
                else:
                    tv.set(parent, 'chk', '\u2612'); chk_state[parent] = True
                _update_vis(parent)
                _update_up(parent)
        def toggle_check(iid):
            cur = tv.set(iid, 'chk')
            checked = (cur != '\u2611')
            _set_tree_state(iid, checked)
            _update_up(iid)
        def on_tree_click(e):
            iid = tv.identify_row(e.y)
            if not iid: return
            col = tv.identify_column(e.x)
            if col in ('#0', '#1'):
                toggle_check(iid)
                return 'break'
        tv.bind('<Button-1>', on_tree_click, '+')

        # Выбор / снятие
        bf = ttk.Frame(f); bf.pack(fill=tk.X, pady=3)
        def _all_models():
            """Генератор всех (iid, info) моделей-листьев (2 или 3 уровня)."""
            for piid in tv.get_children():
                kids = tv.get_children(piid)
                if not kids: continue
                # 2 уровня: сразу модели
                if tv.item(kids[0], 'tags')[0] != 'subgroup':
                    for miid in kids:
                        yield miid, tv.set(miid, 'info')
                else:
                    # 3 уровня: провайдер → подгруппа → модель
                    for giid in kids:
                        for miid in tv.get_children(giid):
                            yield miid, tv.set(miid, 'info')
        def mark_valid():
            for miid, info in _all_models():
                checked = (info == '\u0423\u0421\u041f\u0415\u0425')
                chk_state[miid] = checked
                tv.set(miid, 'chk', '\u2611' if checked else '\u2610')
                _update_vis(miid)
            for piid in tv.get_children():
                _update_up(piid)
        def uncheck_all():
            for piid in tv.get_children():
                for ciid in tv.get_children(piid):
                    chk_state[ciid] = False
                    tv.set(ciid, 'chk', '\u2610')
                    _update_vis(ciid)
                    # Если есть вложенные модели (3 уровня) — снять и их
                    if tv.get_children(ciid):
                        for miid in tv.get_children(ciid):
                            chk_state[miid] = False
                            tv.set(miid, 'chk', '\u2610')
                            _update_vis(miid)
                chk_state[piid] = False
                tv.set(piid, 'chk', '\u2610')
                _update_vis(piid)
        ttk.Button(bf, text='\u2713 \u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0440\u0430\u0431\u043e\u0447\u0438\u0435', command=mark_valid).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text='\u2610 \u0421\u043d\u044f\u0442\u044c \u0432\u0441\u0435', command=uncheck_all).pack(side=tk.LEFT, padx=2)
        if preselect_ok_only:
            mark_valid()

        # Ключи для провайдеров
        ttk.Label(f, text='\u041a\u043b\u044e\u0447\u0438 \u043f\u0440\u043e\u0432\u0430\u0439\u0434\u0435\u0440\u043e\u0432 (\u0438\u0437\u043c\u0435\u043d\u0438\u0442\u0435 \u043f\u0440\u0438 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e\u0441\u0442\u0438):', font=('', 9, 'bold')).pack(anchor=tk.W, pady=(8, 2))
        kf = ttk.Frame(f); kf.pack(fill=tk.X)
        key_vars = {}  # provider_name -> StringVar
        key_entries = {}  # provider_name -> Entry
        kff = ttk.Frame(kf); kff.pack(fill=tk.X, pady=2)
        kff.columnconfigure(1, weight=1)
        for i, pn in enumerate(seen_provs):
            keys = self.providers.get(pn, {}).get('api_keys', [])
            key_str = keys[0] if keys else ''
            kv = tk.StringVar(value=key_str)
            key_vars[pn] = kv
            ttk.Label(kff, text=pn + ':', width=12, anchor=tk.E, font=('', 8)).grid(row=i, column=0, sticky=tk.W, padx=(0, 4), pady=1)
            ke = ttk.Entry(kff, textvariable=kv, width=50, show='*')
            ke.grid(row=i, column=1, sticky=tk.EW, padx=1, pady=1)
            key_entries[pn] = ke
            def toggle_show(pn=pn, ke=ke):
                if ke.cget('show') == '*':
                    ke.configure(show='')
                else:
                    ke.configure(show='*')
            ttk.Button(kff, text='\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c', width=8, command=toggle_show).grid(row=i, column=2, padx=2, pady=1)

        # Кнопки сохранения
        sbf = ttk.Frame(f); sbf.pack(fill=tk.X, pady=(10, 0))
        def do_save():
            p = path_v.get().strip()
            if not p:
                messagebox.showerror('\u041e\u0448\u0438\u0431\u043a\u0430', '\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u043f\u0443\u0442\u044c \u0434\u043b\u044f \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f')
                return
            # Бэкап
            if bkup_v.get() and os.path.isfile(p):
                from datetime import datetime
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                bak = p + '.bak_' + ts
                try:
                    import shutil
                    shutil.copy2(p, bak)
                except Exception as e:
                    if not messagebox.askyesno('\u0411\u044d\u043a\u0430\u043f', '\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0441\u043e\u0437\u0434\u0430\u0442\u044c \u0431\u044d\u043a\u0430\u043f:\n%s\n\n\u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c?' % e):
                        return
            # Сбор данных из дерева (2 или 3 уровня)
            provider_order = []
            models_by_prov = {}
            keys_by_prov = {}
            for piid in tv.get_children():
                pn = tv.item(piid, 'values')[1]
                if not chk_state.get(piid, False):
                    continue
                provider_order.append(pn)
                models_by_prov[pn] = []
                kids = tv.get_children(piid)
                if not kids: continue
                is_nested = tv.item(kids[0], 'tags')[0] == 'subgroup'
                if is_nested:
                    for giid in kids:
                        if not chk_state.get(giid, False):
                            continue
                        grp_name = tv.item(giid, 'values')[1]
                        for miid in tv.get_children(giid):
                            if not chk_state.get(miid, False):
                                continue
                            clean_name = tv.item(miid, 'values')[1]
                            full_name = '[%s] %s' % (grp_name, clean_name)
                            mid = full_name
                            src = 'opencode'
                            for x in self.model_list:
                                if x[0] == pn and x[2] == full_name:
                                    mid = x[1]; src = x[3]; break
                            models_by_prov[pn].append((mid, full_name, src))
                else:
                    for miid in kids:
                        if not chk_state.get(miid, False):
                            continue
                        mn = tv.item(miid, 'values')[1]
                        mid = mn
                        src = 'opencode'
                        for x in self.model_list:
                            if x[0] == pn and x[2] == mn:
                                mid = x[1]; src = x[3]; break
                        models_by_prov[pn].append((mid, mn, src))
                keys_by_prov[pn] = key_vars[pn].get().strip()
                keys_by_prov[pn] = key_vars[pn].get().strip()
            # Построение JSONC
            lines = ['{']
            lines.append('  "provider": {')
            for idx, pn in enumerate(provider_order):
                lines.append('    "%s": {' % pn)
                lines.append('      "name": "%s",' % pn)
                lines.append('      "options": {')
                bu = self.providers.get(pn, {}).get('base_url', '')
                if bu:
                    lines.append('        "baseURL": "%s",' % bu)
                k = keys_by_prov.get(pn, '')
                if k:
                    lines.append('        "apiKey": "%s"' % k)
                lines.append('      },')
                lines.append('      "models": {')
                for midx, (mid, mn, src) in enumerate(models_by_prov[pn]):
                    comma = ',' if midx < len(models_by_prov[pn]) - 1 else ''
                    lines.append('        "%s": { "name": "%s" }%s' % (mid, mn, comma))
                lines.append('      }')
                comma = ',' if idx < len(provider_order) - 1 else ''
                lines.append('    }%s' % comma)
            lines.append('  }')
            lines.append('}')
            try:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines) + '\n')
                self._log('\u042d\u043a\u0441\u043f\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043e: %s' % p)
                self._set_status('\u042d\u043a\u0441\u043f\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u043e: %s' % os.path.basename(p))
                dlg.destroy()
            except Exception as e:
                messagebox.showerror('\u041e\u0448\u0438\u0431\u043a\u0430', '\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c:\n%s' % e)
        ttk.Button(sbf, text='\U0001f4be \u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c', style='Accent.TButton', command=do_save).pack(side=tk.LEFT, padx=2)
        ttk.Button(sbf, text='\u041e\u0442\u043c\u0435\u043d\u0430', command=dlg.destroy).pack(side=tk.LEFT, padx=2)
        # Очистка при закрытии
        dlg.bind('<Destroy>', lambda e: None)

    # ── Export ─────────────────────────────────────────────────────

    def _export_results(self):
        p = filedialog.asksaveasfilename(title='Экспорт результатов', defaultextension='.json', filetypes=[('JSON', '*.json'), ('CSV', '*.csv'), ('All', '*.*')])
        if not p: return
        try:
            if p.endswith('.csv'): self._export_csv(p)
            else: self._export_json(p)
            self._log('Результаты экспортированы: %s' % p); self._set_status('Экспортировано: %s' % os.path.basename(p))
        except Exception as e: messagebox.showerror('Ошибка', 'Не удалось экспортировать:\n%s' % e)

    def _export_json(self, p):
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def _export_csv(self, p):
        with open(p, 'w', encoding='utf-8-sig') as f:
            f.write('Provider,Model,Source,Status,Response,Time\n')
            for pn, mid, mn, src, _fr in self.model_list:
                r = self.results.get(pn, {}).get(mid)
                if r is None:
                    f.write('"%s","%s","%s",-.,\n' % (pn, mn, src))
                elif r['ok']:
                    f.write('"%s","%s","%s",OK,"%s",%.1f\n' % (pn, mn, src, r['msg'].replace('"', '""'), r['elapsed']))
                else:
                    f.write('"%s","%s","%s",FAIL,"%s",%.1f\n' % (pn, mn, src, r['msg'].replace('"', '""'), r['elapsed']))

    # ── Misc ───────────────────────────────────────────────────────

    def _init_log_file(self):
        try:
            if not os.path.isdir(LOGS_DIR):
                os.makedirs(LOGS_DIR)
            log_name = time.strftime('%Y-%m-%d') + '.log'
            self.log_file = open(os.path.join(LOGS_DIR, log_name), 'a', encoding='utf-8')
        except Exception:
            self.log_file = None

    def _log(self, msg):
        self.log.config(state=tk.NORMAL)
        
        # Определение цвета
        tag = 'info'
        m_low = msg.lower()
        if any(word in m_low for word in ('ошибка', 'error', 'неудача', '403', '401', 'fail')):
            tag = 'error'
        elif any(word in m_low for word in ('успешно', 'валиден', 'работает', 'success', '200')):
            tag = 'success'
        elif any(word in m_low for word in ('предупреждение', 'warn', 'timeout', '429')):
            tag = 'warn'
        
        self.log.insert(tk.END, msg + '\n', tagS=tag)
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)
        
        if self.log_file:
            try:
                self.log_file.write('[%s] %s\n' % (time.strftime('%H:%M:%S'), msg))
                self.log_file.flush()
            except Exception:
                pass

    def _set_status(self, text):
        self.statusbar.config(text=text)

    def _show_log_browser(self):
        if not os.path.isdir(LOGS_DIR):
            messagebox.showinfo('Логи', 'Нет файлов логов')
            return
        logs = sorted([f for f in os.listdir(LOGS_DIR) if f.endswith('.log')], reverse=True)
        if not logs:
            messagebox.showinfo('Логи', 'Нет файлов логов')
            return
        dlg = tk.Toplevel(self.root)
        dlg.title('Просмотр логов')
        dlg.geometry('700x500')
        dlg.transient(self.root)
        f = ttk.Frame(dlg, padding=5)
        f.pack(fill=tk.BOTH, expand=True)
        left = ttk.Frame(f)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        ttk.Label(left, text='Файлы:').pack()
        lb = tk.Listbox(left, width=30, height=20)
        lb.pack(fill=tk.BOTH, expand=True)
        for log in logs:
            lb.insert(tk.END, log)
        right = ttk.Frame(f)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt = tk.Text(right, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(right, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        def load_log():
            sel = lb.curselection()
            if not sel:
                return
            log_name = lb.get(sel[0])
            txt.delete('1.0', tk.END)
            try:
                with open(os.path.join(LOGS_DIR, log_name), 'r', encoding='utf-8') as lf:
                    txt.insert(tk.END, lf.read())
            except Exception as e:
                txt.insert(tk.END, 'Ошибка загрузки: %s' % e)
        lb.bind('<<ListboxSelect>>', lambda e: load_log())
        if logs:
            lb.selection_set(0)
            load_log()

    def _about(self):
        messagebox.showinfo('О программе', 'AgentChecker v2.0\n\nПроверка доступности AI-моделей\nиз конфигурации opencode.\n\nPython: %s\nHTTP: %s' % (sys.version.split()[0], _HTTP))


# ── Entry ──────────────────────────────────────────────────────────

def _hide_ollama_window():
    """Сворачивает окна Ollama в трей при запуске, следит за новыми окнами 10 секунд."""
    import ctypes, time, threading
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    GetWindowText = user32.GetWindowTextW
    GetWindowTextLength = user32.GetWindowTextLengthW
    EnumWindows = user32.EnumWindows
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

    def _hide_or_minimize(hwnd, pid):
        """ollama.exe — SW_HIDE, ollama app.exe — SW_MINIMIZE."""
        proc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if proc:
            buf = ctypes.create_unicode_buffer(260)
            psapi.GetModuleBaseNameW(proc, None, buf, 260)
            kernel32.CloseHandle(proc)
            pname = buf.value.lower()
        else:
            pname = ''
        if 'ollama.exe' == pname or pname.endswith('ollama.exe'):
            user32.ShowWindowAsync(hwnd, 0)  # SW_HIDE
        else:
            user32.ShowWindowAsync(hwnd, 6)  # SW_MINIMIZE

    def _find_and_hide():
        found = []
        def callback(hwnd, _):
            length = GetWindowTextLength(hwnd) + 1
            buf = ctypes.create_unicode_buffer(length)
            GetWindowText(hwnd, buf, length)
            title = buf.value.lower()
            if 'ollama' in title or 'olama' in title:
                pid = ctypes.c_ulong()
                GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                found.append((hwnd, pid.value))
            return True
        EnumWindows(EnumWindowsProc(callback), 0)
        for hwnd, pid in found:
            _hide_or_minimize(hwnd, pid)
        return bool(found)

    # Первичная проверка
    _find_and_hide()
    # Фоновая проверка новых окон 10 секунд
    def _watcher():
        for _ in range(20):
            time.sleep(0.5)
            _find_and_hide()
    threading.Thread(target=_watcher, daemon=True).start()

def main():
    root = tk.Tk()
    AgentCheckerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
