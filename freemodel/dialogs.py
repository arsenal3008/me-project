"""Диалоги: AddAccount, EditAccount, Columns. Стадия 1: каркас."""

import threading
import tkinter as tk
from datetime import datetime, timezone
from tkinter import messagebox, scrolledtext, ttk

from . import browser_login
from . import themes as themes_mod
from .account import FreeModelAccount
from .widgets import ProgressDialog, ResizableDialog


def _pw_entry(parent, initial=""):
    fr = ttk.Frame(parent)
    var = tk.StringVar(value=initial)
    e = ttk.Entry(fr, textvariable=var, show="*")
    e.pack(side=tk.LEFT, fill=tk.X, expand=True)
    def t():
        e.config(show="" if e.cget("show") == "*" else "*")
        b.config(text="Hide" if e.cget("show") == "" else "Show")
    b = ttk.Button(fr, text="Show", width=6, command=t)
    b.pack(side=tk.RIGHT, padx=(4, 0))
    return fr, var


def _time_until(ts):
    """Текст 'сброс через Nд Mч' + абсолютное время окончания."""
    from .account import fmt_reset_dh, fmt_reset_abs
    dh = fmt_reset_dh(ts)
    if dh in ("—", ""):
        return ""
    if dh == "сброшен":
        return "сброс сейчас"
    abs_t = fmt_reset_abs(ts)
    return f"сброс через {dh}" + (f"  ({abs_t})" if abs_t else "")


def run_browser_login(parent, settings, save_cb, email="", password="",
                     method="auto", on_done=None):
    dlg = ProgressDialog(parent, settings=settings, save_cb=save_cb,
                          title="Получение cookie")
    dlg.append("info", "Подготовка...")

    def status(level, msg):
        try:
            parent.after(0, lambda: dlg.append(level, msg))
        except tk.TclError:
            pass

    def worker():
        cookie = browser_login.login(email=email, password=password,
                                      method=method, on_status=status)
        try:
            if cookie:
                parent.after(0, lambda: dlg.finish(True, "Cookie получены"))
            else:
                parent.after(0, lambda: dlg.finish(False, "Cookie не получены"))
            if on_done:
                parent.after(100, lambda: on_done(cookie))
        except tk.TclError:
            pass

    threading.Thread(target=worker, daemon=True).start()
    return dlg


ALL_COLUMNS = [
    ("name", "Имя"),
    ("email", "Email"),
    ("plan", "План"),
    ("sub_end", "Подписка до"),
    ("source", "Источник"),
    ("status", "Статус"),
    ("balance", "Баланс"),
    ("credit", "Кредиты"),
    ("used_5h_pct", "5ч %"),
    ("used_week_pct", "7д %"),
    ("reset_5h", "Сброс 5ч"),
    ("reset_week", "Сброс 7д"),
    ("requests", "Запросы"),
    ("keys", "Ключей"),
    ("last_check", "Проверка"),
    ("error", "Ошибка"),
]


class AddAccountDialog(ResizableDialog):
    def __init__(self, parent, settings, save_cb, on_add):
        super().__init__(parent, key="add_account", title="Добавить аккаунт",
                         default="600x540", min_size=(460, 400),
                         settings=settings, save_cb=save_cb)
        self.on_add = on_add
        self._build()

    def _build(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)
        nb = ttk.Notebook(frame)
        nb.pack(fill=tk.BOTH, expand=True)

        tab_b = ttk.Frame(nb, padding=10); nb.add(tab_b, text="🌐 Браузер (auto)")
        ttk.Label(tab_b, text="Имя:").pack(anchor=tk.W)
        name_b = ttk.Entry(tab_b); name_b.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(tab_b,
                  text="Откроется окно браузера. Войдите в freemodel.dev —\n"
                       "cookie сохранятся автоматически.",
                  wraplength=520, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(tab_b, text="Метод:").pack(anchor=tk.W)
        method_var = tk.StringVar(value="auto")
        ttk.Combobox(tab_b, textvariable=method_var,
                     values=["auto", "chrome", "playwright"],
                     state="readonly").pack(fill=tk.X, pady=(0, 10))
        ttk.Label(tab_b, text="API-ключ (опц.):").pack(anchor=tk.W)
        af_b, av_b = _pw_entry(tab_b); af_b.pack(fill=tk.X)

        tab_p = ttk.Frame(nb, padding=10); nb.add(tab_p, text="Email + Пароль")
        ttk.Label(tab_p, text="Имя:").pack(anchor=tk.W)
        name_p = ttk.Entry(tab_p); name_p.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(tab_p, text="Email:").pack(anchor=tk.W)
        email_e = ttk.Entry(tab_p); email_e.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(tab_p, text="Пароль:").pack(anchor=tk.W)
        pf, pv = _pw_entry(tab_p); pf.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(tab_p, text="API-ключ (опц.):").pack(anchor=tk.W)
        af, av = _pw_entry(tab_p); af.pack(fill=tk.X)

        tab_c = ttk.Frame(nb, padding=10); nb.add(tab_c, text="Cookie вручную")
        ttk.Label(tab_c, text="Имя:").pack(anchor=tk.W)
        name_c = ttk.Entry(tab_c); name_c.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(tab_c,
                  text="Вставьте session cookie из DevTools "
                       "(Application → Cookies):",
                  wraplength=520).pack(anchor=tk.W, pady=(0, 4))
        cookie_txt = scrolledtext.ScrolledText(tab_c, height=6)
        themes_mod.style_text(cookie_txt, self.palette)
        cookie_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        ttk.Label(tab_c, text="API-ключ (опц.):").pack(anchor=tk.W)
        af2, av2 = _pw_entry(tab_c); af2.pack(fill=tk.X)

        tab_a = ttk.Frame(nb, padding=10); nb.add(tab_a, text="Только API-ключ")
        ttk.Label(tab_a, text="Имя:").pack(anchor=tk.W)
        name_a = ttk.Entry(tab_a); name_a.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(tab_a, text="API-ключ:").pack(anchor=tk.W)
        af3, av3 = _pw_entry(tab_a); af3.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(tab_a,
                  text="Без cookie доступна только проверка через /v1/models.\n"
                       "Баланс и лимиты не отобразятся.",
                  style="Muted.TLabel", wraplength=520).pack(
            anchor=tk.W, pady=(8, 0))

        btnf = ttk.Frame(frame); btnf.pack(fill=tk.X, pady=(10, 0))

        def on_ok():
            cur = nb.index(nb.select())
            if cur == 0:
                name = name_b.get().strip() or "Browser"
                acc = FreeModelAccount(name=name, api_key=av_b.get().strip())
                method = method_var.get()
                def done(cookie):
                    if cookie:
                        acc.cookie = cookie
                    self.on_add(acc)
                    self.close()
                run_browser_login(self, self.settings, self.save_cb,
                                  method=method, on_done=done)
                return
            elif cur == 1:
                email = email_e.get().strip()
                password = pv.get()
                if not email or not password:
                    messagebox.showwarning("Ошибка", "Email и пароль обязательны",
                                            parent=self)
                    return
                acc = FreeModelAccount(
                    email=email, password=password,
                    api_key=av.get().strip(),
                    name=name_p.get().strip() or email.split("@")[0])
            elif cur == 2:
                cookie = cookie_txt.get("1.0", tk.END).strip()
                if not cookie:
                    messagebox.showwarning("Ошибка", "Вставьте cookie", parent=self)
                    return
                acc = FreeModelAccount(
                    cookie=cookie, api_key=av2.get().strip(),
                    name=name_c.get().strip() or "Cookie Account")
            else:
                api_key = av3.get().strip()
                if not api_key:
                    messagebox.showwarning("Ошибка", "Введите API-ключ", parent=self)
                    return
                acc = FreeModelAccount(
                    api_key=api_key,
                    name=name_a.get().strip() or "API Key")

            self.on_add(acc)
            self.close()

        ttk.Button(btnf, text="OK", style="Accent.TButton",
                   command=on_ok).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btnf, text="Отмена",
                   command=self.close).pack(side=tk.RIGHT, padx=2)


class EditAccountDialog(ResizableDialog):
    def __init__(self, parent, settings, save_cb, account, on_save,
                 on_check=None):
        super().__init__(parent, key="edit_account",
                         title=f"Редактирование: {account.name}",
                         default="640x600", min_size=(500, 480),
                         settings=settings, save_cb=save_cb)
        self.account = account
        self.on_save = on_save
        self.on_check = on_check
        self._build()

    def _build(self):
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(outer, highlightthickness=0)
        themes_mod.style_canvas(canvas, self.palette)
        sb = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        frame = ttk.Frame(canvas)
        frame.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        cwin = canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(cwin, width=e.width))
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        acc = self.account

        ttk.Label(frame, text="Имя:").pack(anchor=tk.W, pady=(0, 2))
        name_e = ttk.Entry(frame); name_e.insert(0, acc.name)
        name_e.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(frame, text="Email:").pack(anchor=tk.W, pady=(0, 2))
        email_e = ttk.Entry(frame); email_e.insert(0, acc.email)
        email_e.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(frame, text="Пароль:").pack(anchor=tk.W, pady=(0, 2))
        pf, pv = _pw_entry(frame, acc.password)
        pf.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(frame, text="API-ключ:").pack(anchor=tk.W, pady=(0, 2))
        af, av = _pw_entry(frame, acc.api_key)
        af.pack(fill=tk.X, pady=(0, 8))

        head = ttk.Frame(frame); head.pack(fill=tk.X)
        ttk.Label(head, text="Cookie:").pack(side=tk.LEFT)
        ttk.Button(head, text="🌐 Войти через браузер",
                   command=self._do_browser_login).pack(side=tk.RIGHT)
        self.cookie_txt = scrolledtext.ScrolledText(frame, height=5)
        themes_mod.style_text(self.cookie_txt, self.palette)
        self.cookie_txt.insert("1.0", acc.cookie)
        self.cookie_txt.pack(fill=tk.X, pady=(2, 8))

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        stats = ttk.LabelFrame(frame, text="Последняя проверка", padding=8)
        stats.pack(fill=tk.X, pady=(0, 8))
        self._render_stats(stats)

        btn = ttk.Frame(outer); btn.pack(fill=tk.X, pady=(8, 0))

        def save():
            acc.name = name_e.get().strip()
            acc.email = email_e.get().strip()
            acc.password = pv.get()
            acc.api_key = av.get().strip()
            acc.cookie = self.cookie_txt.get("1.0", tk.END).strip()
            self.on_save(acc)
            self.close()

        ttk.Button(btn, text="Сохранить", style="Accent.TButton",
                   command=save).pack(side=tk.RIGHT, padx=2)
        if self.on_check:
            ttk.Button(btn, text="Проверить",
                       command=lambda: (save(), self.on_check(acc))).pack(
                side=tk.RIGHT, padx=2)
        ttk.Button(btn, text="Отмена",
                   command=self.close).pack(side=tk.RIGHT, padx=2)

        def _scroll(e):
            try:
                canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
            except tk.TclError:
                pass
        canvas.bind_all("<MouseWheel>", _scroll)

        original_close = self._on_close
        def cleanup_close():
            try:
                canvas.unbind_all("<MouseWheel>")
            except tk.TclError:
                pass
            original_close()
        self.protocol("WM_DELETE_WINDOW", cleanup_close)

    def _render_stats(self, container):
        acc = self.account
        bal = f"${acc.balance:.2f}" if acc.balance is not None else "—"
        credit = f"${acc.credit_cents / 100.0:.2f}" if acc.credit_cents else "$0.00"
        ttk.Label(container,
                  text=f"План: {acc.plan or '—'}  ({acc.plan_status or '—'})",
                  font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(container,
                  text=f"Баланс: {bal}  (кредиты: {credit})").pack(anchor=tk.W)
        ttk.Label(container,
                  text=f"Запросов: {acc.total_requests or '—'}  |  "
                       f"Токенов: {acc.total_tokens or '—'}",
                  font=("Segoe UI", 9)).pack(anchor=tk.W)

        if acc.limit_5h_cents:
            u5 = acc.used_5h_cents / 100.0
            l5 = acc.limit_5h_cents / 100.0
            p5 = u5 / l5 * 100 if l5 else 0
            row = ttk.Frame(container); row.pack(fill=tk.X, pady=(6, 2))
            ttk.Label(row, text="5ч:",
                      font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(row,
                      text=f"${u5:.2f} / ${l5:.2f}  ·  {p5:.0f}%").pack(
                side=tk.LEFT, padx=6)
            ttk.Label(row, text=_time_until(acc.resets_5h),
                      style="Muted.TLabel").pack(side=tk.LEFT, padx=6)
            ttk.Progressbar(container, length=400, mode="determinate",
                            value=p5).pack(fill=tk.X)

        if acc.limit_week_cents:
            uw = acc.used_week_cents / 100.0
            lw = acc.limit_week_cents / 100.0
            pw = uw / lw * 100 if lw else 0
            row = ttk.Frame(container); row.pack(fill=tk.X, pady=(6, 2))
            ttk.Label(row, text="7д:",
                      font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(row,
                      text=f"${uw:.2f} / ${lw:.2f}  ·  {pw:.0f}%").pack(
                side=tk.LEFT, padx=6)
            ttk.Label(row, text=_time_until(acc.resets_week),
                      style="Muted.TLabel").pack(side=tk.LEFT, padx=6)
            ttk.Progressbar(container, length=400, mode="determinate",
                            value=pw).pack(fill=tk.X)

        if acc.models:
            ttk.Label(container,
                      text=f"Модели ({len(acc.models)}): "
                           f"{', '.join(acc.models[:6])}"
                           f"{'…' if len(acc.models) > 6 else ''}",
                      font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(4, 0))
        ttk.Label(container,
                  text=f"Проверено: {acc.last_check or '—'}",
                  style="Muted.TLabel").pack(anchor=tk.W)
        if acc.error:
            ttk.Label(container, text=f"⚠ {acc.error}",
                      style="Danger.TLabel").pack(anchor=tk.W)

    def _do_browser_login(self):
        def done(cookie):
            if cookie:
                self.cookie_txt.delete("1.0", tk.END)
                self.cookie_txt.insert("1.0", cookie)
        run_browser_login(self, self.settings, self.save_cb,
                          email=self.account.email,
                          password=self.account.password,
                          method="auto", on_done=done)


class ColumnsDialog(ResizableDialog):
    def __init__(self, parent, settings, save_cb, on_apply):
        super().__init__(parent, key="columns", title="Колонки таблицы",
                         default="360x460", min_size=(300, 360),
                         settings=settings, save_cb=save_cb)
        self.on_apply = on_apply
        self._build()

    def _build(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Отметьте видимые колонки:",
                  font=("Segoe UI", 10, "bold")).pack(anchor=tk.W,
                                                       pady=(0, 8))

        visible = set(self.settings.get("visible_columns", []) or [])
        vars_map = {}

        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        for key, label in ALL_COLUMNS:
            v = tk.BooleanVar(value=(key in visible) or not visible)
            vars_map[key] = v
            ttk.Checkbutton(list_frame, text=label, variable=v).pack(
                anchor=tk.W, pady=1)

        btn = ttk.Frame(frame); btn.pack(fill=tk.X, pady=(10, 0))

        def apply_cb():
            new_cols = [k for k, _ in ALL_COLUMNS if vars_map[k].get()]
            if not new_cols:
                new_cols = ["name", "status"]
            self.settings["visible_columns"] = new_cols
            if self.save_cb:
                self.save_cb()
            self.on_apply(new_cols)
            self.close()

        def reset_default():
            from . import settings as smod
            defaults = smod.DEFAULTS.get("visible_columns", [])
            for k, v in vars_map.items():
                v.set(k in defaults)

        ttk.Button(btn, text="Применить", style="Accent.TButton",
                   command=apply_cb).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn, text="По умолчанию",
                   command=reset_default).pack(side=tk.RIGHT, padx=2)
        ttk.Button(btn, text="Отмена",
                   command=self.close).pack(side=tk.RIGHT, padx=2)
