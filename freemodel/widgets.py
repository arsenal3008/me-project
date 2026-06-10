"""Переиспользуемые виджеты: ToolTip, Toast, ResizableDialog, ProgressDialog."""

import tkinter as tk
from tkinter import ttk

from . import settings as settings_mod


# ─── ToolTip ──────────────────────────────────────────────────────────────────

class ToolTip:
    """Всплывающая подсказка при наведении."""
    _bg = "#ffffcc"
    _fg = "#333"

    @classmethod
    def set_theme(cls, bg, fg):
        cls._bg = bg
        cls._fg = fg

    def __init__(self, widget, text, delay=400):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip = None
        self._id = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<Motion>", self._move, add="+")

    def _schedule(self, event=None):
        self._hide()
        self._id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self.tip:
            return
        try:
            x = self.widget.winfo_pointerx() + 12
            y = self.widget.winfo_pointery() + 8
        except tk.TclError:
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self.tip, text=self.text, justify=tk.LEFT,
                       background=self._bg, foreground=self._fg,
                       relief=tk.SOLID, borderwidth=1,
                       padx=6, pady=3, font=("Segoe UI", 9))
        lbl.pack()

    def _move(self, event=None):
        if self.tip:
            try:
                x = self.widget.winfo_pointerx() + 12
                y = self.widget.winfo_pointery() + 8
                self.tip.wm_geometry(f"+{x}+{y}")
            except tk.TclError:
                pass

    def _hide(self, event=None):
        if self._id:
            try:
                self.widget.after_cancel(self._id)
            except (tk.TclError, ValueError):
                pass
            self._id = None
        if self.tip:
            try:
                self.tip.destroy()
            except tk.TclError:
                pass
            self.tip = None

    def update_text(self, text):
        self.text = text


# ─── Toast ────────────────────────────────────────────────────────────────────

class Toast:
    """Всплывающее уведомление в правом нижнем углу."""

    @staticmethod
    def show(root, message, duration=3000, fg="#ffffff", bg="#333333"):
        try:
            top = tk.Toplevel(root)
            top.wm_overrideredirect(True)
            top.attributes("-alpha", 0.0, "-topmost", True)
            lbl = tk.Label(top, text=message, foreground=fg, background=bg,
                           padx=16, pady=10, font=("Segoe UI", 10, "bold"),
                           wraplength=350)
            lbl.pack()
            top.update_idletasks()
            w, h = top.winfo_width(), top.winfo_height()
            sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
            top.geometry(f"+{sw - w - 20}+{sh - h - 60}")

            def fade_in(step=0):
                if step <= 10:
                    try:
                        top.attributes("-alpha", step / 10)
                        top.after(30, lambda: fade_in(step + 1))
                    except tk.TclError:
                        pass
                else:
                    top.after(duration, fade_out)

            def fade_out(step=10):
                if step >= 0:
                    try:
                        top.attributes("-alpha", step / 10)
                        top.after(30, lambda: fade_out(step - 1))
                    except tk.TclError:
                        pass
                else:
                    try:
                        top.destroy()
                    except tk.TclError:
                        pass

            fade_in()
        except tk.TclError:
            pass


# ─── ResizableDialog ──────────────────────────────────────────────────────────

class ResizableDialog(tk.Toplevel):
    """Базовый диалог с автоматическим сохранением/восстановлением геометрии.

    Параметры:
        parent     — окно-родитель
        key        — ключ для dialog_geometries в fm_settings.json
        title      — заголовок
        default    — геометрия по умолчанию ('WxH' или 'WxH+X+Y')
        min_size   — (min_w, min_h)
        modal      — grab_set + transient
        settings   — dict настроек (от FreeModelGUI)
        save_cb    — callable() для записи settings
    """

    def __init__(self, parent, key, title="", default="600x400",
                 min_size=(400, 300), modal=True,
                 settings=None, save_cb=None):
        super().__init__(parent)
        self.key = key
        self.settings = settings or {}
        self.save_cb = save_cb
        self.title(title)

        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
        except tk.TclError:
            sw, sh = 1920, 1080

        # Восстановить геометрию
        saved = (self.settings.get("dialog_geometries", {}) or {}).get(key)
        geom = settings_mod.safe_geometry(saved, sw, sh,
                                          min_w=min_size[0],
                                          min_h=min_size[1]) if saved else None
        if not geom:
            geom = settings_mod.safe_geometry(default, sw, sh,
                                              min_w=min_size[0],
                                              min_h=min_size[1]) or default
        try:
            self.geometry(geom)
        except tk.TclError:
            pass
        self.minsize(*min_size)

        if modal:
            self.transient(parent)
            try:
                self.grab_set()
            except tk.TclError:
                pass

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _capture_geometry(self):
        try:
            geom = self.geometry()
        except tk.TclError:
            return
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
        except tk.TclError:
            return
        safe = settings_mod.safe_geometry(geom, sw, sh, min_w=200, min_h=150)
        if safe:
            dg = self.settings.setdefault("dialog_geometries", {})
            dg[self.key] = safe
            if self.save_cb:
                try:
                    self.save_cb()
                except Exception:
                    pass

    def _on_close(self):
        self._capture_geometry()
        try:
            self.destroy()
        except tk.TclError:
            pass

    def close(self):
        self._on_close()


# ─── ProgressDialog ───────────────────────────────────────────────────────────

class ProgressDialog(ResizableDialog):
    """Окно с прогресс-баром и логом — для авто-логина браузера."""

    def __init__(self, parent, settings=None, save_cb=None,
                 title="Прогресс", default="560x340"):
        super().__init__(parent, key="progress", title=title,
                         default=default, min_size=(420, 240),
                         modal=True, settings=settings, save_cb=save_cb)
        body = ttk.Frame(self, padding=12)
        body.pack(fill=tk.BOTH, expand=True)

        self.status_lbl = ttk.Label(body, text="", font=("Segoe UI", 10, "bold"))
        self.status_lbl.pack(anchor=tk.W, pady=(0, 6))

        self.pb = ttk.Progressbar(body, mode="indeterminate", length=300)
        self.pb.pack(fill=tk.X, pady=(0, 8))
        self.pb.start(80)

        log_frame = ttk.Frame(body)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = tk.Text(log_frame, height=8, wrap=tk.WORD,
                           font=("Consolas", 9), bd=0, padx=4, pady=4)
        sb = ttk.Scrollbar(log_frame, orient=tk.VERTICAL,
                           command=self.log.yview)
        self.log.configure(yscrollcommand=sb.set)
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(body)
        btn_frame.pack(fill=tk.X, pady=(8, 0))
        self.cancel_btn = ttk.Button(btn_frame, text="Отмена",
                                      command=self._on_close)
        self.cancel_btn.pack(side=tk.RIGHT)

        self.cancelled = False

    def append(self, level, message):
        try:
            self.status_lbl.config(text=message)
            self.log.config(state=tk.NORMAL)
            prefix = {"info": "·", "success": "✓", "error": "✗"}.get(level, "·")
            self.log.insert(tk.END, f"{prefix} {message}\n")
            self.log.see(tk.END)
            self.log.config(state=tk.DISABLED)
        except tk.TclError:
            pass

    def finish(self, success, message):
        try:
            self.pb.stop()
            self.pb.configure(mode="determinate", value=100 if success else 0)
            self.status_lbl.config(text=message)
            self.cancel_btn.config(text="Закрыть")
        except tk.TclError:
            pass

    def _on_close(self):
        self.cancelled = True
        try:
            self.pb.stop()
        except tk.TclError:
            pass
        super()._on_close()
