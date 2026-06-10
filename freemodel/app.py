"""FreeModelGUI — главное окно."""

import json
import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from . import settings as settings_mod
from . import themes as themes_mod
from .account import FreeModelAccount, fmt_reset_abs, fmt_reset_dh
from .dialogs import ALL_COLUMNS, AddAccountDialog, ColumnsDialog, EditAccountDialog
from .widgets import Toast, ToolTip

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "fm_accounts.json"
)

STATUS_TEXTS = {
    "valid": "OK", "invalid": "Неверный ключ",
    "unavailable": "API недоступен", "timeout": "Таймаут",
    "error": "Ошибка", "pending": "Ожидание",
    "checking": "Проверка...",
}

SOURCE_LABELS = {
    "cookie": "🍪 Cookie", "password": "🔑 Пароль",
    "api": "🔧 API", "none": "—",
}


def _fmt_pct(v):
    return f"{v:.0f}%" if v is not None else "—"


def _fmt_balance(v):
    return f"${v:.2f}" if v is not None else "—"


def _fmt_sub_end(s):
    if not s:
        return "—"
    try:
        if "T" in str(s):
            return str(s)[:10]
        return str(s)
    except Exception:
        return str(s)[:20] if s else "—"


class FreeModelGUI:
    def __init__(self, root):
        self.root = root
        self.accounts = []
        self.checking = False
        self._save_pending = False

        self.settings = settings_mod.load()
        self.theme = self.settings.get("theme", "light")
        self._palette = themes_mod.apply_theme(self.theme, root)
        ToolTip.set_theme(self._palette["tooltip_bg"],
                          self._palette["tooltip_fg"])

        root.title("FreeModel.dev Manager")
        root.minsize(900, 500)

        self._row_acc = {}
        self._tick_job = None

        self._build_ui()
        self._load_accounts()
        self._restore_geometry()
        root.protocol("WM_DELETE_WINDOW", self._on_close)
        root.bind("<Configure>", self._on_resize, add="+")
        self._tick_resets()  # живой обратный отсчёт таймеров

    # ── UI ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = self.root

        tb = ttk.Frame(root); tb.pack(fill=tk.X, padx=8, pady=(6, 2))

        ttk.Button(tb, text="＋ Добавить",
                   command=self.add_account_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="✎ Правка",
                   command=self.edit_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="✕ Удалить",
                   command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Separator(tb, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Button(tb, text="⟳ Все",
                   command=self.check_all_accounts).pack(side=tk.LEFT, padx=2)
        ttk.Button(tb, text="⟳ Выбранные",
                   command=self.check_selected).pack(side=tk.LEFT, padx=2)
        ttk.Separator(tb, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Button(tb, text="☷ Колонки",
                   command=self.show_columns_dialog).pack(side=tk.LEFT, padx=2)

        # Селектор темы
        ttk.Separator(tb, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Label(tb, text="Тема:").pack(side=tk.LEFT, padx=(0, 4))
        self._theme_keys = [k for k, _ in themes_mod.list_themes()]
        theme_names = [n for _, n in themes_mod.list_themes()]
        self._theme_var = tk.StringVar(
            value=themes_mod.get_palette(self.theme)["_name"])
        cb = ttk.Combobox(tb, textvariable=self._theme_var,
                          values=theme_names, state="readonly", width=18)
        cb.pack(side=tk.LEFT, padx=2)
        def on_theme(_e=None):
            name = self._theme_var.get()
            for k, n in themes_mod.list_themes():
                if n == name:
                    self.change_theme(k)
                    break
        cb.bind("<<ComboboxSelected>>", on_theme)

        self.status_label = tk.Label(tb, text="Готов",
                                      bg=self._palette["bg"],
                                      fg=self._palette["fg"])
        self.status_label.pack(side=tk.RIGHT, padx=6)

        # Treeview
        tf = ttk.Frame(root)
        tf.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 0))
        all_cols = [k for k, _ in ALL_COLUMNS]
        self.tree = ttk.Treeview(tf, columns=all_cols, show="headings",
                                  selectmode="extended")
        self.tree_columns = all_cols
        self.tree.column("#0", width=0, stretch=False)

        vsb = ttk.Scrollbar(tf, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(tf, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.grid_rowconfigure(0, weight=1)
        tf.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.edit_account)
        self.tree.bind("<Delete>", lambda e: self.remove_selected())
        self.tree.bind("<ButtonRelease-1>", self._save_settings_throttled_event)

        self._build_columns()
        self._apply_theme_to_tree()

        # Bottom bar
        bf = ttk.Frame(root); bf.pack(fill=tk.X, padx=8, pady=(3, 5))
        self.summary_label = tk.Label(bf, text="",
                                        bg=self._palette["bg"],
                                        fg=self._palette["fg"],
                                        font=("Segoe UI", 9))
        self.summary_label.pack(side=tk.LEFT)
        self.status_bar = tk.Label(bf, text="", anchor=tk.W,
                                     bg=self._palette["bg"],
                                     fg=self._palette["muted"],
                                     font=("Segoe UI", 9), relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

    def _save_settings_throttled_event(self, _e=None):
        self._save_settings_throttled()

    def _tick_resets(self):
        """Раз в минуту обновляет колонки 'Сброс 5ч/7д' без перерисовки всей
        таблицы (сохраняет выделение и сортировку)."""
        try:
            for iid, acc in list(getattr(self, "_row_acc", {}).items()):
                if not self.tree.exists(iid):
                    continue
                if "reset_5h" in self._visible_cols:
                    self.tree.set(iid, "reset_5h", fmt_reset_dh(acc.resets_5h))
                if "reset_week" in self._visible_cols:
                    self.tree.set(iid, "reset_week",
                                  fmt_reset_dh(acc.resets_week))
        except (AttributeError, tk.TclError):
            pass
        try:
            self._tick_job = self.root.after(60000, self._tick_resets)
        except tk.TclError:
            pass

    def _refresh_table(self):
        try:
            for it in self.tree.get_children():
                self.tree.delete(it)
        except (AttributeError, tk.TclError):
            return

        self._row_acc = {}
        total_bal = 0.0
        ok = 0
        for i, acc in enumerate(self.accounts):
            status = STATUS_TEXTS.get(acc.status, acc.status)
            bal_v = acc.balance
            credit_v = acc.credit_cents / 100.0 if acc.credit_cents else 0.0
            if bal_v is not None:
                total_bal += bal_v
            if acc.status == "valid":
                ok += 1

            row = {
                "name": acc.name,
                "email": acc.email or "—",
                "plan": acc.plan or "—",
                "sub_end": _fmt_sub_end(acc.sub_end),
                "source": SOURCE_LABELS.get(acc.source, "—"),
                "status": status,
                "balance": _fmt_balance(bal_v),
                "credit": f"${credit_v:.2f}" if credit_v else "—",
                "used_5h_pct": _fmt_pct(acc.used_5h_pct),
                "used_week_pct": _fmt_pct(acc.used_week_pct),
                "reset_5h": fmt_reset_dh(acc.resets_5h),
                "reset_week": fmt_reset_dh(acc.resets_week),
                "requests": str(acc.total_requests) if acc.total_requests else "—",
                "keys": str(len(acc.raw_keys)) if acc.raw_keys else "—",
                "last_check": acc.last_check or "—",
                "error": (acc.error or "")[:80],
            }
            vals = tuple(row.get(c, "") for c in self.tree_columns)
            tags = ["oddrow" if i % 2 == 0 else "evenrow"]
            if acc.status in ("valid", "invalid", "unavailable",
                              "timeout", "error", "checking"):
                tags.append(acc.status)
            try:
                iid = self.tree.insert("", tk.END, values=vals, tags=tags)
                self._row_acc[iid] = acc
            except tk.TclError:
                pass

        try:
            self.summary_label.config(
                text=f"Аккаунтов: {len(self.accounts)}  ·  OK: {ok}  ·  "
                     f"Σ Баланс: ${total_bal:.2f}")
        except (AttributeError, tk.TclError):
            pass

    # ── Геометрия / настройки ────────────────────────────────────────────

    def _restore_geometry(self):
        try:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
        except tk.TclError:
            sw, sh = 1920, 1080
        geom = settings_mod.safe_geometry(self.settings.get("geometry"),
                                          sw, sh, min_w=860, min_h=500)
        if geom:
            try:
                self.root.geometry(geom)
            except tk.TclError:
                pass

    def _on_resize(self, event):
        if event.widget is self.root:
            self._save_settings_throttled()

    def _save_settings_throttled(self):
        if self._save_pending:
            return
        self._save_pending = True
        self.root.after(800, self._save_settings_apply)

    def _save_settings_apply(self):
        self._save_pending = False
        self._capture_state()
        settings_mod.save(self.settings)

    def save_settings(self):
        self._capture_state()
        settings_mod.save(self.settings)

    def _capture_state(self):
        try:
            geom = self.root.geometry()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            safe = settings_mod.safe_geometry(geom, sw, sh, min_w=860, min_h=500)
            if safe:
                self.settings["geometry"] = safe
        except tk.TclError:
            pass
        try:
            widths = self.settings.setdefault("column_widths", {})
            for col in getattr(self, "_visible_cols", []):
                try:
                    widths[col] = int(float(self.tree.column(col, "width")))
                except (tk.TclError, ValueError):
                    pass
        except (AttributeError, tk.TclError):
            pass
        self.settings["theme"] = self.theme

    # ── Аккаунты I/O ─────────────────────────────────────────────────────

    def _load_accounts(self):
        if not os.path.isfile(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.accounts = [FreeModelAccount.from_dict(d) for d in data]
            self._refresh_table()
        except Exception as e:
            try:
                self.status_bar.config(text=f"Ошибка загрузки: {e}")
            except (AttributeError, tk.TclError):
                pass

    def _save_accounts(self):
        try:
            data = [a.to_dict() for a in self.accounts]
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # Файл содержит пароли/cookie/ключи — ограничиваем доступ.
            settings_mod.secure_chmod(CONFIG_FILE)
        except Exception as e:
            try:
                self.status_bar.config(text=f"Ошибка сохранения: {e}")
            except (AttributeError, tk.TclError):
                pass

    # ── Действия ─────────────────────────────────────────────────────────

    def add_account_dialog(self):
        def on_add(acc):
            self.accounts.append(acc)
            self._refresh_table()
            self._save_accounts()
        AddAccountDialog(self.root, self.settings,
                          self.save_settings, on_add)

    def edit_account(self, event=None):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Инфо", "Выберите аккаунт")
            return
        idx = self.tree.index(sel[0])
        if idx >= len(self.accounts):
            return
        acc = self.accounts[idx]
        def on_save(a):
            self._refresh_table()
            self._save_accounts()
        def on_check(a):
            threading.Thread(
                target=lambda: self._check_one_thread(a),
                daemon=True).start()
        EditAccountDialog(self.root, self.settings, self.save_settings,
                           acc, on_save, on_check)

    def remove_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Удалить",
                                    f"Удалить {len(sel)} аккаунт(ов)?"):
            return
        indices = sorted((self.tree.index(it) for it in sel), reverse=True)
        for i in indices:
            if i < len(self.accounts):
                self.accounts.pop(i)
        self._refresh_table()
        self._save_accounts()

    def check_all_accounts(self):
        if self.checking:
            Toast.show(self.root, "Проверка уже идёт",
                       bg=self._palette["accent"])
            return
        if not self.accounts:
            Toast.show(self.root, "Нет аккаунтов",
                       bg=self._palette["warn"])
            return
        self.checking = True
        self.status_label.config(text="⏳ Проверка...")

        def worker():
            ok = fail = 0
            for i, acc in enumerate(self.accounts):
                if not self.checking:
                    break
                self.root.after(0, lambda a=acc, n=i:
                                self.status_bar.config(
                                    text=f"{n + 1}/{len(self.accounts)}: "
                                         f"{a.name}"))
                try:
                    acc.check_all()
                except Exception as e:
                    acc.status = "error"
                    acc.error = str(e)[:100]
                if acc.status == "valid":
                    ok += 1
                else:
                    fail += 1
                self.root.after(0, self._refresh_table)
            self.checking = False
            self.root.after(0, self._save_accounts)
            self.root.after(0, lambda: self.status_label.config(
                text=f"OK: {ok}  Ошибок: {fail}"))
            self.root.after(0, lambda: self.status_bar.config(text="Готов"))
            color = self._palette["success"] if fail == 0 else self._palette["danger"]
            self.root.after(100, lambda: Toast.show(
                self.root,
                f"Готов. OK: {ok}  Ошибок: {fail}", bg=color))

        threading.Thread(target=worker, daemon=True).start()

    def check_selected(self):
        sel = self.tree.selection()
        if not sel:
            Toast.show(self.root, "Выберите аккаунты",
                       bg=self._palette["warn"])
            return
        indices = [self.tree.index(it) for it in sel]
        self.checking = True
        self.status_label.config(text="⏳ Проверка выбранных...")

        def worker():
            ok = fail = 0
            for idx in indices:
                if idx >= len(self.accounts) or not self.checking:
                    break
                acc = self.accounts[idx]
                try:
                    acc.check_all()
                except Exception as e:
                    acc.status = "error"
                    acc.error = str(e)[:100]
                if acc.status == "valid":
                    ok += 1
                else:
                    fail += 1
                self.root.after(0, self._refresh_table)
            self.checking = False
            self.root.after(0, self._save_accounts)
            self.root.after(0, lambda: self.status_label.config(
                text=f"OK: {ok}  Ошибок: {fail}"))
            color = self._palette["success"] if fail == 0 else self._palette["danger"]
            self.root.after(100, lambda: Toast.show(
                self.root, f"OK: {ok}  Ошибок: {fail}", bg=color))

        threading.Thread(target=worker, daemon=True).start()

    def _check_one_thread(self, acc):
        try:
            acc.check_all()
        except Exception as e:
            acc.status = "error"
            acc.error = str(e)[:100]
        self.root.after(0, self._refresh_table)
        self.root.after(0, self._save_accounts)

    # ── Темы ─────────────────────────────────────────────────────────────

    def change_theme(self, theme_key):
        if theme_key == self.theme:
            return
        self.theme = theme_key
        self._palette = themes_mod.apply_theme(theme_key, self.root)
        ToolTip.set_theme(self._palette["tooltip_bg"],
                          self._palette["tooltip_fg"])
        self._apply_theme_to_tree()
        self.settings["theme"] = theme_key
        settings_mod.save(self.settings)
        Toast.show(self.root,
                   f"Тема: {themes_mod.get_palette(theme_key)['_name']}",
                   bg=self._palette["accent"])

    def _apply_theme_to_tree(self):
        try:
            c = self._palette
            self.tree.tag_configure("valid", foreground=c["success"])
            self.tree.tag_configure("invalid", foreground=c["danger"])
            self.tree.tag_configure("unavailable", foreground=c["warn"])
            self.tree.tag_configure("timeout", foreground=c["warn"])
            self.tree.tag_configure("error", foreground=c["danger"])
            self.tree.tag_configure("checking", foreground=c["accent"])
            self.tree.tag_configure("oddrow", background=c["tree_odd"])
            self.tree.tag_configure("evenrow", background=c["tree_even"])
            self.status_label.config(background=c["bg"], foreground=c["fg"])
            self.summary_label.config(background=c["bg"], foreground=c["fg"])
            self.status_bar.config(background=c["bg"], foreground=c["muted"])
        except (AttributeError, tk.TclError):
            pass

    def show_columns_dialog(self):
        def apply_cols(cols):
            self._build_columns()
            self._refresh_table()
        ColumnsDialog(self.root, self.settings,
                       self.save_settings, apply_cols)

    def _build_columns(self):
        cols = self.settings.get("visible_columns") or []
        if not cols:
            cols = [k for k, _ in ALL_COLUMNS]
        valid = {k for k, _ in ALL_COLUMNS}
        cols = [c for c in cols if c in valid]
        if not cols:
            cols = ["name", "status"]
        self._visible_cols = cols

        headings = dict(ALL_COLUMNS)
        widths = self.settings.get("column_widths", {}) or {}

        self.tree.configure(displaycolumns=cols)
        for col in cols:
            try:
                self.tree.heading(
                    col, text=headings.get(col, col),
                    command=lambda c=col: self._sort_by(c))
                w = widths.get(col, 100)
                self.tree.column(col, width=w, minwidth=50, anchor=tk.W)
            except tk.TclError:
                pass

    def _sort_by(self, col):
        try:
            items = [(self.tree.set(it, col), it)
                     for it in self.tree.get_children("")]
            reverse = (self.settings.get("sort_column") == col and
                       not self.settings.get("sort_reverse", False))
            items.sort(key=lambda x: x[0].lower(), reverse=reverse)
            for idx, (_, it) in enumerate(items):
                self.tree.move(it, "", idx)
            self.settings["sort_column"] = col
            self.settings["sort_reverse"] = reverse
            self.save_settings()
        except tk.TclError:
            pass

    # ── Закрытие ─────────────────────────────────────────────────────────

    def _on_close(self):
        self.checking = False
        if self._tick_job:
            try:
                self.root.after_cancel(self._tick_job)
            except (tk.TclError, ValueError):
                pass
        self.save_settings()
        self._save_accounts()
        try:
            self.root.destroy()
        except tk.TclError:
            pass
