"""Главное окно AgentChecker."""

import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .. import http_client, ollama_manager, providers as providers_mod, settings as settings_mod
from ..jsonc import read_jsonc, save_jsonc
from ..paths import LOGS_DIR, existing_opencode_config
from . import theme

PROVIDER_KEY_WORDS = ('ключ', 'ключа', 'ключей')


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


def _keys_word(n, total=None):
    base = total if total is not None else n
    word = _plural(base, PROVIDER_KEY_WORDS)
    if total is not None:
        return '%d из %d %s' % (n, total, word)
    return '%d %s' % (n, word)


class AgentCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('AgentChecker — проверка AI-моделей')
        self.root.geometry('1020x720')
        self.root.minsize(860, 540)

        s = settings_mod.load()
        self.timeout_val = tk.IntVar(value=s['timeout'])
        self.retries_val = tk.IntVar(value=s['retries'])
        self.delay_val = tk.DoubleVar(value=s['delay'])
        self.dark_mode = tk.BooleanVar(value=s['dark_mode'])
        self.geometry_val = tk.StringVar(value=s['geometry'])
        self.log_height_val = tk.IntVar(value=s['log_height'])
        self.auto_save_config = tk.BooleanVar(value=s['auto_save_config'])
        self.auto_start_ollama = tk.BooleanVar(value=s['auto_start_ollama'])
        self.hide_ollama_window = tk.BooleanVar(value=s['hide_ollama_window'])

        self.filter_status = tk.StringVar(value='all')
        self.filter_provider_s = tk.StringVar(value='all')
        self.filter_source = tk.StringVar(value='all')
        self.filter_free = tk.StringVar(value='all')

        self.providers = {}
        self.results = {}
        self.model_list = []
        self.running = False
        self.cancel_flag = False
        self.sort_col = None
        self.sort_rev = False
        self.log_file = None
        self._init_log_file()

        self._build_ui()
        try:
            self.root.geometry(self.geometry_val.get())
        except tk.TclError:
            pass
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)

        self._load_providers_initial()
        providers_mod.purge_empty(self.providers)
        providers_mod.propagate_keys(self.providers)
        self._rebuild_provider_filter()
        theme.apply(self, self.dark_mode.get())
        self._refresh_table()
        self._ensure_ollama_running()
        self._auto_validate_keys()

    # ── UI ────────────────────────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style()
        themes = style.theme_names()
        style.theme_use('vista' if 'vista' in themes else 'clam')
        style.configure('TCombobox', padding=3, arrowsize=14)
        style.configure('Accent.TButton', font=('', 9, 'bold'))
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
        sm.add_checkbutton(label='Авто-сохранение в opencode.jsonc',
                           variable=self.auto_save_config, command=self._save_settings)
        sm.add_checkbutton(label='Авто-запуск Ollama',
                           variable=self.auto_start_ollama, command=self._save_settings)
        sm.add_checkbutton(label='Скрывать окно Ollama',
                           variable=self.hide_ollama_window, command=self._save_settings)
        mb.add_cascade(label='Настройки', menu=sm)

        vm = tk.Menu(mb, tearoff=0)
        vm.add_checkbutton(label='Тёмная тема', variable=self.dark_mode, command=self._toggle_theme)
        mb.add_cascade(label='Вид', menu=vm)

        hm = tk.Menu(mb, tearoff=0)
        hm.add_command(label='О программе', command=self._about)
        mb.add_cascade(label='Справка', menu=hm)

    def _build_toolbar(self):
        tb = ttk.Frame(self.root)
        tb.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(5, 0))
        self.btn_all = ttk.Button(tb, text='▶ Проверить все',
                                  style='Accent.TButton', command=self._start_all)
        self.btn_all.pack(side=tk.LEFT, padx=2)
        self.btn_sel = ttk.Button(tb, text='▶ Выбранные', command=self._start_selected)
        self.btn_sel.pack(side=tk.LEFT, padx=2)
        self.btn_stop = ttk.Button(tb, text='■ Стоп', command=self._stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text='⚙ Настройки', command=self._show_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(tb, text='🔑 Ключи', style='Accent.TButton',
                   command=self._show_providers_dialog).pack(side=tk.RIGHT, padx=5)
        ttk.Button(tb, text='📤 Экспорт', command=self._export_dialog).pack(side=tk.RIGHT, padx=2)

    def _build_main(self):
        mf = ttk.Frame(self.root)
        mf.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        left = ttk.Frame(mf, width=200)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left.pack_propagate(False)

        ttk.Label(left, text='Фильтры', font=('', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(left, text='Провайдер:', font=('', 8)).pack(anchor=tk.W)
        self.provider_combo = ttk.Combobox(left, textvariable=self.filter_provider_s,
                                           state='readonly', values=['all'])
        self.provider_combo.pack(fill=tk.X, pady=(0, 8))
        self.provider_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_table())
        ttk.Label(left, text='Статус:', font=('', 8)).pack(anchor=tk.W)
        ttk.Combobox(left, textvariable=self.filter_status, state='readonly',
                     values=['all', 'yes', 'no', 'untested']).pack(fill=tk.X, pady=(0, 8))
        self.filter_status.trace_add('write', lambda *a: self._refresh_table())
        ttk.Label(left, text='Источник:', font=('', 8)).pack(anchor=tk.W)
        ttk.Combobox(left, textvariable=self.filter_source, state='readonly',
                     values=['all', 'opencode', 'custom']).pack(fill=tk.X, pady=(0, 8))
        self.filter_source.trace_add('write', lambda *a: self._refresh_table())
        ttk.Label(left, text='Тип доступа:', font=('', 8)).pack(anchor=tk.W)
        ttk.Combobox(left, textvariable=self.filter_free, state='readonly',
                     values=['all', 'free', 'paid']).pack(fill=tk.X, pady=(0, 8))
        self.filter_free.trace_add('write', lambda *a: self._refresh_table())
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
        self.cols = [
            ('provider', 110, 'Провайдер'),
            ('model', 200, 'Модель'),
            ('id', 200, 'ID модели'),
            ('source', 70, 'Ист.'),
            ('status', 70, 'Статус'),
            ('response', 240, 'Ответ'),
            ('time', 65, 'Время'),
        ]
        col_keys = tuple(c[0] for c in self.cols)
        self.tree = ttk.Treeview(tf, columns=col_keys, show='headings', selectmode='extended')
        for c, w, h in self.cols:
            self.tree.heading(c, text=h, command=lambda col=c: self._sort_by(col))
            self.tree.column(c, width=w, minwidth=50)
        vsb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tf, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        tf.grid_rowconfigure(0, weight=1)
        tf.grid_columnconfigure(0, weight=1)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)
        self.progress = ttk.Progressbar(top_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(3, 0))
        pw.add(top_frame, weight=3)

        lf = ttk.LabelFrame(pw, text='Лог')
        pw.add(lf, weight=1)
        self.log = tk.Text(lf, height=self.log_height_val.get(), wrap=tk.WORD,
                           state=tk.DISABLED, font=('Consolas', 9))
        lsb = ttk.Scrollbar(lf, command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.tag_config('info', foreground='black')
        self.log.tag_config('success', foreground='green')
        self.log.tag_config('warn', foreground='orange')
        self.log.tag_config('error', foreground='red')

    def _build_statusbar(self):
        self.statusbar = ttk.Label(self.root, text='Готов', relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ── Загрузка ──────────────────────────────────────────────────────

    def _load_providers_initial(self):
        provs, model_list, path = providers_mod.load_from_opencode(log=self._log)
        if provs:
            self.providers = provs
            self.model_list = list(model_list)

    def _rebuild_provider_filter(self):
        names = ['all'] + sorted(self.providers.keys())
        self.provider_combo['values'] = names

    def _load_opencode_file(self):
        p = filedialog.askopenfilename(title='Выберите opencode.jsonc',
                                       filetypes=[('JSONC', '*.jsonc'), ('JSON', '*.json'), ('All', '*.*')])
        if not p:
            return
        added, ok = providers_mod.merge_opencode_file(self.providers, self.model_list, p, log=self._log)
        if not ok:
            messagebox.showerror('Ошибка', 'Не удалось загрузить конфиг (см. лог)')
            return
        providers_mod.purge_empty(self.providers)
        self._rebuild_provider_filter()
        providers_mod.save_providers(self.providers)
        self._refresh_table()
        self._log('Загружен %s: %d новых моделей' % (os.path.basename(p), added))
        self._set_status('Конфиг загружен')

    def _add_custom_model(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('Добавить пользовательскую модель')
        dlg.geometry('460x240')
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()
        f = ttk.Frame(dlg, padding=18)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text='Провайдер (выберите или введите новый):',
                  font=('', 9)).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        pv = tk.StringVar()
        prov_vals = sorted(self.providers.keys())
        pc = ttk.Combobox(f, textvariable=pv, values=prov_vals, state='normal')
        pc.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 8))
        if prov_vals:
            pc.set(prov_vals[0])
        ttk.Label(f, text='ID модели:').grid(row=2, column=0, sticky=tk.W, pady=3)
        mv = tk.StringVar()
        ttk.Entry(f, textvariable=mv, width=35).grid(row=2, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
        ttk.Label(f, text='Имя (опционально):').grid(row=3, column=0, sticky=tk.W, pady=3)
        nv = tk.StringVar()
        ttk.Entry(f, textvariable=nv, width=35).grid(row=3, column=1, sticky=tk.EW, padx=(8, 0), pady=3)
        f.grid_columnconfigure(1, weight=1)

        def do():
            pr = pv.get().strip()
            mi = mv.get().strip()
            nm = nv.get().strip() or mi
            if not pr or not mi:
                messagebox.showwarning('Ошибка', 'Провайдер и ID обязательны.')
                return
            if pr not in self.providers:
                self.providers[pr] = {'base_url': '', 'api_key': '', 'api_keys': [], 'models': {}}
            if mi in self.providers[pr]['models']:
                messagebox.showwarning('Ошибка', 'Модель уже существует.')
                return
            fr = providers_mod.is_free(mi, nm)
            self.providers[pr]['models'][mi] = {'name': nm, 'source': 'custom', 'free': fr}
            self.model_list.append((pr, mi, nm, 'custom', fr))
            self._rebuild_provider_filter()
            self._refresh_table()
            providers_mod.save_providers(self.providers)
            self._log('Добавлена модель: %s / %s' % (pr, mi))
            dlg.destroy()

        bf = ttk.Frame(f)
        bf.grid(row=4, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(bf, text='Добавить', style='Accent.TButton', command=do).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text='Отмена', command=dlg.destroy).pack(side=tk.LEFT)

    def _remove_custom_models(self):
        n = sum(1 for x in self.model_list if x[3] == 'custom')
        if n == 0:
            messagebox.showinfo('Инфо', 'Нет пользовательских моделей.')
            return
        if not messagebox.askyesno('Удалить', 'Удалить все пользовательские модели (%d шт.)?' % n):
            return
        self.model_list = [x for x in self.model_list if x[3] != 'custom']
        for p in self.providers.values():
            p['models'] = {k: v for k, v in p['models'].items() if v.get('source') != 'custom'}
        self.providers = {k: v for k, v in self.providers.items() if v['models']}
        self._rebuild_provider_filter()
        self._refresh_table()
        providers_mod.save_providers(self.providers)
        self._log('Пользовательские модели удалены')

    # ── Управление провайдерами ───────────────────────────────────────

    def _show_providers_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('Управление провайдерами (ключи / URL)')
        dlg.geometry('720x520')
        dlg.transient(self.root)
        dlg.grab_set()
        f = ttk.Frame(dlg, padding=10)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text='Настройка API-ключей и URL для каждого провайдера:',
                  font=('', 9, 'bold')).pack(anchor=tk.W)
        cv = tk.Canvas(f, highlightthickness=0)
        sb = ttk.Scrollbar(f, orient=tk.VERTICAL, command=cv.yview)
        sf = ttk.Frame(cv)
        sf.bind('<Configure>', lambda e: cv.configure(scrollregion=cv.bbox('all')))
        cv.create_window((0, 0), window=sf, anchor='nw')
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        def mw(e):
            cv.yview_scroll(int(-1 * (e.delta / 120)), 'units')

        cv.bind_all('<MouseWheel>', mw)
        dlg.bind('<Destroy>', lambda e: cv.unbind_all('<MouseWheel>'))

        entries = {}
        row = 0
        for pn in sorted(self.providers.keys()):
            p = self.providers[pn]
            mc = len(p['models'])
            ttk.Label(sf, text=pn, font=('', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(10, 0))
            ttk.Label(sf, text='%d моделей' % mc, foreground='gray').grid(row=row, column=1, sticky=tk.W, pady=(10, 0))
            row += 1
            ttk.Label(sf, text='URL:', font=('', 8)).grid(row=row, column=0, sticky=tk.W, padx=(15, 0))
            uv = tk.StringVar(value=p.get('base_url', ''))
            ttk.Entry(sf, textvariable=uv, width=58).grid(row=row, column=1, sticky=tk.EW, padx=5, pady=1)
            row += 1
            ttk.Label(sf, text='Ключи:', font=('', 8)).grid(row=row, column=0, sticky=tk.NW, padx=(15, 5), pady=(6, 0))
            kf = ttk.Frame(sf)
            kf.grid(row=row, column=1, sticky=tk.EW, padx=5, pady=2)
            key_list = list(p.get('api_keys', []) or ([p.get('api_key')] if p.get('api_key') else []))
            kv = tk.StringVar(value=key_list[0] if key_list else '')
            key_combo = ttk.Combobox(kf, textvariable=kv, values=key_list, state='readonly', width=55)
            key_combo.pack(fill=tk.X)
            ctl = ttk.Frame(kf)
            ctl.pack(fill=tk.X, pady=(3, 0))
            new_key_var = tk.StringVar()
            entry_key = ttk.Entry(ctl, textvariable=new_key_var, width=35, show='*')
            entry_key.pack(side=tk.LEFT, padx=(0, 3))
            show_kvar = tk.BooleanVar()
            ttk.Checkbutton(ctl, text='Показать', variable=show_kvar,
                            command=lambda e=entry_key, v=show_kvar: e.configure(show='' if v.get() else '*')).pack(side=tk.LEFT)

            def add_key(cb=key_combo, ek=entry_key, nkv=new_key_var, pn=pn):
                k = nkv.get().strip()
                if not k:
                    return
                vals = list(cb['values'] or [])
                if k not in vals:
                    vals.append(k)
                    cb['values'] = vals
                cb.set(k)
                nkv.set('')
                ek.delete(0, tk.END)
                http_client.invalidate_cache(self.providers[pn].get('base_url', ''))

            def remove_key(cb=key_combo, pn=pn):
                cur = cb.get()
                vals = list(cb['values'] or [])
                if cur in vals:
                    vals.remove(cur)
                    cb['values'] = vals
                    cb.set(vals[0] if vals else '')
                    http_client.invalidate_cache(self.providers[pn].get('base_url', ''))

            ttk.Button(ctl, text='+', width=3, command=add_key).pack(side=tk.LEFT, padx=2)
            ttk.Button(ctl, text='−', width=3, command=remove_key).pack(side=tk.LEFT)
            ttk.Button(ctl, text='Проверить', width=10,
                       command=lambda pn=pn, cb=key_combo: self._test_provider_keys(pn, cb)).pack(side=tk.LEFT, padx=5)
            row += 1
            entries[pn] = (uv, key_combo)
        sf.grid_columnconfigure(1, weight=1)

        def save():
            for pn, (uv, cb) in entries.items():
                new_url = uv.get().strip()
                if new_url != self.providers[pn].get('base_url'):
                    http_client.invalidate_cache(self.providers[pn].get('base_url', ''))
                    self.providers[pn]['base_url'] = new_url
                keys = list(cb['values'] or [])
                self.providers[pn]['api_keys'] = keys
                self.providers[pn]['api_key'] = cb.get() or (keys[0] if keys else '')
            providers_mod.save_providers(self.providers)
            self._log('Настройки провайдеров сохранены')
            dlg.destroy()

        bf = ttk.Frame(f)
        bf.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(bf, text='Сохранить', command=save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bf, text='Отмена', command=dlg.destroy).pack(side=tk.RIGHT)

    def _test_provider_keys(self, provider_name, key_combo):
        p = self.providers.get(provider_name)
        if not p or not p.get('models'):
            self._log('Нет моделей для проверки ключей: %s' % provider_name)
            return
        keys = list(key_combo['values'] or [])
        if not keys:
            self._log('Нет ключей для проверки: %s' % provider_name)
            return
        model_id = next(iter(p['models']))
        base_url = (p.get('base_url') or '').rstrip('/') + '/chat/completions'
        self._log('Проверка ключей %s (через %s)...' % (provider_name, model_id))
        results = {}

        def test_single(key):
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + key,
                    'User-Agent': 'Mozilla/5.0 AgentChecker',
                    'Accept': 'application/json',
                    'Origin': 'https://opencode.ai',
                    'Referer': 'https://opencode.ai/',
                }
                code, resp_text = http_client.http_post(
                    base_url,
                    {'model': model_id, 'messages': [{'role': 'user', 'content': 'say ok'}], 'max_tokens': 5},
                    headers, timeout=15)
                if code == 200:
                    results[key] = (True, 'Работает')
                    return
                try:
                    err = (json.loads(resp_text).get('error') or {}).get('message', '') or ''
                except Exception:
                    err = (resp_text or '').strip()[:100]
                label = 'RATE' if code == 429 else 'HTTP %d' % code
                desc = http_client.ERR_DESC.get(code, '')
                results[key] = (False, '%s: %s' % (label, (desc or err)[:60]))
            except Exception as e:
                results[key] = (False, 'Ошибка: %s' % str(e)[:60])

        threads = [threading.Thread(target=test_single, args=(k,)) for k in keys]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=20)
        working = [k for k, (ok, _) in results.items() if ok]
        non_rate = [k for k, (ok, m) in results.items() if not ok and not m.startswith('RATE')]
        chosen = working[0] if working else (non_rate[0] if non_rate else keys[0])
        key_combo.set(chosen)
        for k in keys:
            ok, msg = results.get(k, (False, 'нет ответа'))
            note = ' ← выбран' if k == chosen and ok else ''
            self._log('%s %s: %s%s' % ('✓' if ok else '✗', k[:48], msg, note))
        http_client.invalidate_cache(p.get('base_url', ''))

    # ── Настройки ─────────────────────────────────────────────────────

    def _show_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('Настройки')
        dlg.geometry('350x180')
        dlg.transient(self.root)
        dlg.grab_set()
        f = ttk.Frame(dlg, padding=15)
        f.pack(fill=tk.BOTH, expand=True)
        ttk.Label(f, text='Таймаут (сек):').grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(f, from_=5, to=120, textvariable=self.timeout_val, width=8).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Label(f, text='Повторов:').grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(f, from_=0, to=5, textvariable=self.retries_val, width=8).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(f, text='Задержка (сек):').grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Spinbox(f, from_=0.0, to=5.0, increment=0.1, textvariable=self.delay_val, width=8).grid(row=2, column=1, sticky=tk.W, padx=5)

        def save_set():
            self._save_settings()
            dlg.destroy()

        ttk.Button(f, text='OK', command=save_set).grid(row=3, column=0, columnspan=2, pady=12)

    def _save_settings(self):
        settings_mod.save({
            'timeout': self.timeout_val.get(),
            'retries': self.retries_val.get(),
            'delay': self.delay_val.get(),
            'dark_mode': self.dark_mode.get(),
            'geometry': self.geometry_val.get(),
            'log_height': self.log_height_val.get(),
            'auto_save_config': self.auto_save_config.get(),
            'auto_start_ollama': self.auto_start_ollama.get(),
            'hide_ollama_window': self.hide_ollama_window.get(),
        })

    # ── Авто-валидация ────────────────────────────────────────────────

    def _ensure_ollama_running(self):
        if not self.auto_start_ollama.get():
            return

        def _run():
            ollama_manager.ensure_running(log=self._safe_log)
            if self.hide_ollama_window.get():
                ollama_manager.hide_windows()

        threading.Thread(target=_run, daemon=True).start()

    def _auto_validate_keys(self):
        def _run():
            for pn, p in list(self.providers.items()):
                keys = p.get('api_keys', [])
                if not keys:
                    continue
                bu = (p.get('base_url') or '').rstrip('/')
                if not bu:
                    continue
                with http_client.VALID_KEYS_LOCK:
                    if bu in http_client.VALID_KEYS_CACHE:
                        continue
                if not http_client.check_server_online(bu):
                    if 'localhost' in bu or '127.0.0.1' in bu:
                        self._safe_log('  %s: сервер не запущен' % pn)
                        with http_client.VALID_KEYS_LOCK:
                            http_client.VALID_KEYS_CACHE[bu] = []
                        continue
                self._safe_log('Проверка ключей %s (%s)...' % (pn, _keys_word(len(keys))))
                valid = http_client.validate_keys(bu, keys, provider_models=p.get('models'),
                                                  provider_name=pn, timeout=10, log=self._safe_log)
                with http_client.VALID_KEYS_LOCK:
                    http_client.VALID_KEYS_CACHE[bu] = valid
                if valid:
                    self._safe_log('  %s: работает %s' % (pn, _keys_word(len(valid), len(keys))))
                else:
                    self._safe_log('  %s: нет рабочих ключей' % pn)
                self.root.after(0, self._refresh_table)
                if self.auto_save_config.get():
                    self._save_to_opencode_config()

        threading.Thread(target=_run, daemon=True).start()

    def _save_to_opencode_config(self):
        import shutil
        cfg_path = existing_opencode_config()
        if not cfg_path:
            return
        try:
            cfg = read_jsonc(cfg_path)
        except Exception as e:
            self._safe_log('Ошибка чтения opencode.jsonc: %s' % e)
            return
        changed = False
        for pn, p in self.providers.items():
            if pn not in cfg.get('provider', {}):
                continue
            with http_client.VALID_KEYS_LOCK:
                valid = http_client.VALID_KEYS_CACHE.get((p.get('base_url') or '').rstrip('/'), [])
            if not valid:
                continue
            opts = cfg['provider'][pn].setdefault('options', {})
            existing = opts.get('apiKeys', []) or []
            if not all(k in existing for k in valid):
                opts['apiKeys'] = valid + [k for k in existing if k not in valid]
                opts['apiKey'] = valid[0]
                changed = True
        if not changed:
            return
        backup = cfg_path + '.bak'
        if not os.path.isfile(backup):
            try:
                shutil.copy2(cfg_path, backup)
            except Exception:
                pass
        save_jsonc(cfg_path, cfg)
        self._safe_log('Конфиг opencode.jsonc обновлён валидными ключами')

    # ── Таблица ───────────────────────────────────────────────────────

    def _sort_by(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(key=lambda x: x[0].lower(),
                   reverse=self.sort_rev if self.sort_col == col else False)
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, '', idx)
        if self.sort_col == col:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col = col
            self.sort_rev = False
        arrow = '▲' if self.sort_rev else '▼'
        for c, _w, h in self.cols:
            self.tree.heading(c, text=h + (' ' + arrow if c == col else ''))

    def _refresh_table(self, *_):
        for i in self.tree.get_children():
            self.tree.delete(i)
        pf = self.filter_provider_s.get()
        sf = self.filter_status.get()
        fc = self.filter_source.get()
        ff = self.filter_free.get()
        total = ok = fail = unt = 0
        for pn, mid, mn, src, fr in self.model_list:
            if pf != 'all' and pn != pf:
                continue
            if fc != 'all' and src != fc:
                continue
            if ff == 'free' and not fr:
                continue
            if ff == 'paid' and fr:
                continue
            r = self.results.get(pn, {}).get(mid)
            if r is None:
                if sf not in ('all', 'untested'):
                    continue
                st, resp, el, tg = '—', '', '', ('untested',)
                unt += 1
            elif r['ok']:
                if sf not in ('all', 'yes'):
                    continue
                st, resp, el, tg = 'УСПЕХ', r['msg'], '%.1fs' % r['elapsed'], ('ok',)
                ok += 1
            else:
                if sf not in ('all', 'no'):
                    continue
                st, resp, el, tg = 'НЕУДАЧА', r['msg'], '%.1fs' % r['elapsed'], ('fail',)
                fail += 1
            total += 1
            disp_name = mn + (' 🆓' if fr else '')
            self.tree.insert('', tk.END, values=(pn, disp_name, mid, src, st, resp, el), tags=tg)
        self.lbl_total.config(text='Всего: %d' % total)
        self.lbl_ok.config(text='Работает: %d' % ok)
        self.lbl_fail.config(text='Не работает: %d' % fail)
        self.lbl_untested.config(text='Не проверено: %d' % unt)

    def _on_double_click(self, e):
        sel = self.tree.selection()
        if not sel:
            return
        v = self.tree.item(sel[0], 'values')
        self.root.clipboard_clear()
        self.root.clipboard_append(v[2])
        self._set_status('Скопировано: %s' % v[2])

    def _on_right_click(self, e):
        iid = self.tree.identify_row(e.y)
        if not iid:
            return
        sel = self.tree.selection()
        if iid not in sel:
            self.tree.selection_set(iid)
            sel = (iid,)
        v = self.tree.item(sel[0], 'values')
        menu = tk.Menu(self.root, tearoff=0)
        cnt = len(sel)
        if cnt == 1:
            menu.add_command(label='Проверить «%s»' % v[1][:40],
                             command=lambda: self._run_tests(self._items_from_sel(sel)))
            menu.add_command(label='Копировать ID модели',
                             command=lambda: self._copy_to_clipboard(v[2], 'Скопирован ID'))
            resp = v[5]
            if resp:
                menu.add_command(label='Копировать ответ',
                                 command=lambda r=resp: self._copy_to_clipboard(r, 'Ответ скопирован'))
        else:
            menu.add_command(label='Проверить %d выделенных' % cnt,
                             command=lambda: self._run_tests(self._items_from_sel(sel)))
            menu.add_command(label='Копировать ID %d моделей' % cnt,
                             command=lambda: self._copy_ids_from_sel(sel))
        menu.add_separator()
        menu.add_command(label='Проверить все модели провайдера',
                         command=lambda: self._run_tests([x for x in self.model_list if x[0] == v[0]]))
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _items_from_sel(self, sel):
        out = []
        for iid in sel:
            v = self.tree.item(iid, 'values')
            for x in self.model_list:
                if x[0] == v[0] and x[1] == v[2]:
                    out.append(x)
                    break
        return out

    def _copy_to_clipboard(self, text, status_msg):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._set_status(status_msg)

    def _copy_ids_from_sel(self, sel):
        ids = [self.tree.item(iid, 'values')[2] for iid in sel]
        self._copy_to_clipboard('\n'.join(ids), 'Скопировано ID: %d' % len(ids))

    # ── Тестирование ──────────────────────────────────────────────────

    def _start_all(self):
        pf = self.filter_provider_s.get()
        sf = self.filter_status.get()
        fc = self.filter_source.get()
        ff = self.filter_free.get()
        items = []
        for x in self.model_list:
            pn, mid, mn, src, fr = x
            if pf != 'all' and pn != pf:
                continue
            if fc != 'all' and src != fc:
                continue
            if ff == 'free' and not fr:
                continue
            if ff == 'paid' and fr:
                continue
            r = self.results.get(pn, {}).get(mid)
            if r is None and sf not in ('all', 'untested'):
                continue
            if r is not None:
                if r['ok'] and sf not in ('all', 'yes'):
                    continue
                if not r['ok'] and sf not in ('all', 'no'):
                    continue
            items.append(x)
        self._run_tests(items)

    def _start_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('Инфо', 'Выберите модели в таблице.')
            return
        self._run_tests(self._items_from_sel(sel))

    def _run_tests(self, items):
        if self.running:
            messagebox.showinfo('Инфо', 'Уже идёт проверка. Остановите её.')
            return
        if not items:
            return
        self.running = True
        self.cancel_flag = False
        self.btn_all.config(state=tk.DISABLED)
        self.btn_sel.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.progress['maximum'] = len(items)
        self.progress['value'] = 0
        threading.Thread(target=self._worker, args=(items,), daemon=True).start()

    def _stop(self):
        if self.running:
            self.cancel_flag = True
            self._log('Остановка...')
            self._set_status('Остановка...')

    def _worker(self, items):
        to = self.timeout_val.get()
        rt = self.retries_val.get()
        dl = self.delay_val.get()
        batch_ok = 0
        try:
            for i, (pn, mid, mn, _src, _fr) in enumerate(items):
                if self.cancel_flag:
                    break
                p = self.providers.get(pn)
                if not p:
                    continue
                keys = list(p.get('api_keys') or ([p['api_key']] if p.get('api_key') else []))
                if not keys:
                    self._safe_log('  Нет ключей для %s' % pn)
                    self.results.setdefault(pn, {})[mid] = {'ok': False, 'msg': 'Нет API ключей', 'elapsed': 0}
                    continue
                self._safe_log('  Ключей: %d, пробую %s...' % (len(keys), pn))
                ok_flag, msg, el = http_client.test_model(
                    p['base_url'], keys, mid, timeout=to, retries=rt,
                    provider_models=p.get('models'), log=self._safe_log)
                self.results.setdefault(pn, {})[mid] = {'ok': ok_flag, 'msg': msg, 'elapsed': el}
                if ok_flag:
                    batch_ok += 1
                self._safe_log('  %s (%.1fs) %s' % ('УСПЕХ' if ok_flag else 'НЕУДАЧА', el, msg))
                self.root.after(0, self._refresh_table)
                self.root.after(0, lambda v=i + 1: self.progress.configure(value=v))
                if i < len(items) - 1 and not self.cancel_flag:
                    time.sleep(dl)
        finally:
            self.root.after(0, lambda: self._on_done(batch_ok))

    def _on_done(self, batch_ok=0):
        self.running = False
        self.btn_all.config(state=tk.NORMAL)
        self.btn_sel.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self._set_status('Готово')
        ok = fail = 0
        for pr in self.results.values():
            for r in pr.values():
                if r['ok']:
                    ok += 1
                else:
                    fail += 1
        self._log('Завершено: %d УСПЕХ, %d НЕУДАЧА' % (ok, fail))
        if batch_ok > 0:
            def ask_save():
                if messagebox.askyesno('Сохранить конфиг',
                                       'Обнаружено %d работающих моделей.\n\nСохранить конфигурацию в opencode.jsonc\nтолько с работающими моделями?' % batch_ok):
                    self._export_dialog(preselect_ok_only=True)
            self.root.after(100, ask_save)

    # ── Экспорт ───────────────────────────────────────────────────────

    def _export_dialog(self, preselect_ok_only=False):
        from .export_dialog import open_export_dialog
        open_export_dialog(self, preselect_ok_only)

    def _export_results(self):
        p = filedialog.asksaveasfilename(title='Экспорт результатов', defaultextension='.json',
                                         filetypes=[('JSON', '*.json'), ('CSV', '*.csv'), ('All', '*.*')])
        if not p:
            return
        try:
            if p.endswith('.csv'):
                self._export_csv(p)
            else:
                self._export_json(p)
            self._log('Результаты экспортированы: %s' % p)
            self._set_status('Экспортировано: %s' % os.path.basename(p))
        except Exception as e:
            messagebox.showerror('Ошибка', 'Не удалось экспортировать:\n%s' % e)

    def _export_json(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def _export_csv(self, path):
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write('Provider,Model,Source,Status,Response,Time\n')
            for pn, mid, mn, src, _fr in self.model_list:
                r = self.results.get(pn, {}).get(mid)
                if r is None:
                    f.write('"%s","%s","%s",NA,,\n' % (pn, mn, src))
                else:
                    status = 'OK' if r['ok'] else 'FAIL'
                    f.write('"%s","%s","%s",%s,"%s",%.1f\n' %
                            (pn, mn, src, status, r['msg'].replace('"', '""'), r['elapsed']))

    # ── Лог / статус ──────────────────────────────────────────────────

    def _init_log_file(self):
        try:
            os.makedirs(LOGS_DIR, exist_ok=True)
            log_name = time.strftime('%Y-%m-%d') + '.log'
            self.log_file = open(os.path.join(LOGS_DIR, log_name), 'a', encoding='utf-8')
        except Exception:
            self.log_file = None

    def _close_log_file(self):
        if self.log_file:
            try:
                self.log_file.close()
            except Exception:
                pass
            self.log_file = None

    def _classify(self, msg):
        m = msg.lower()
        if any(w in m for w in ('ошибка', 'error', 'неудача', 'fail', ' 401', ' 403')):
            return 'error'
        if any(w in m for w in ('успешно', 'успех', 'валиден', 'работает', 'success', ' 200')):
            return 'success'
        if any(w in m for w in ('предупреждение', 'warn', 'timeout', ' 429')):
            return 'warn'
        return 'info'

    def _log(self, msg, level=None):
        tag = level or self._classify(msg)
        try:
            self.log.config(state=tk.NORMAL)
            self.log.insert(tk.END, msg + '\n', tag)
            self.log.see(tk.END)
            self.log.config(state=tk.DISABLED)
        except tk.TclError:
            pass
        if self.log_file:
            try:
                self.log_file.write('[%s] %s\n' % (time.strftime('%H:%M:%S'), msg))
                self.log_file.flush()
            except Exception:
                pass

    def _safe_log(self, msg, level=None):
        """Потокобезопасная обёртка над ``_log`` (через ``after``)."""
        self.root.after(0, lambda: self._log(msg, level))

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

    def _toggle_theme(self):
        theme.apply(self, self.dark_mode.get())
        self._refresh_table()
        self._save_settings()

    def _about(self):
        from .. import __version__
        messagebox.showinfo('О программе',
                            'AgentChecker v%s\n\nПроверка доступности AI-моделей\nиз конфигурации opencode.\n\n'
                            'Python: %s\nПлатформа: %s\nHTTP: %s' %
                            (__version__, sys.version.split()[0], sys.platform, http_client.http_backend()))

    def _on_close(self):
        try:
            self.geometry_val.set(self.root.geometry())
        except tk.TclError:
            pass
        self._save_settings()
        self._close_log_file()
        self.root.destroy()


def main():
    root = tk.Tk()
    AgentCheckerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
