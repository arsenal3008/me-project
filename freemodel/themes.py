"""Темы оформления — 8 палитр + менеджер применения стилей ttk."""

import tkinter as tk
from tkinter import ttk


# ─── 8 палитр ────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "_name": "Light",
        "bg": "#f5f5f5", "fg": "#1a1a1a",
        "surface": "#ffffff", "border": "#d1d5db",
        "accent": "#2563eb", "success": "#16a34a",
        "danger": "#dc2626", "warn": "#d97706",
        "muted": "#888888",
        "tree_bg": "#ffffff", "tree_fg": "#1a1a1a",
        "tree_odd": "#f9fafb", "tree_even": "#ffffff",
        "tree_sel_bg": "#bfdbfe", "tree_sel_fg": "#1e3a5f",
        "heading_bg": "#e5e7eb", "heading_fg": "#1a1a1a",
        "input_bg": "#ffffff", "input_fg": "#1a1a1a",
        "tooltip_bg": "#ffffcc", "tooltip_fg": "#333333",
        "toast_bg": "#333333", "toast_fg": "#ffffff",
        "progress_bg": "#e5e7eb",
    },
    "dark": {
        "_name": "Dark",
        "bg": "#1e1e2e", "fg": "#cdd6f4",
        "surface": "#313244", "border": "#45475a",
        "accent": "#89b4fa", "success": "#a6e3a1",
        "danger": "#f38ba8", "warn": "#f9e2af",
        "muted": "#6c7086",
        "tree_bg": "#1e1e2e", "tree_fg": "#cdd6f4",
        "tree_odd": "#181825", "tree_even": "#1e1e2e",
        "tree_sel_bg": "#45475a", "tree_sel_fg": "#cdd6f4",
        "heading_bg": "#313244", "heading_fg": "#cdd6f4",
        "input_bg": "#313244", "input_fg": "#cdd6f4",
        "tooltip_bg": "#45475a", "tooltip_fg": "#cdd6f4",
        "toast_bg": "#313244", "toast_fg": "#cdd6f4",
        "progress_bg": "#45475a",
    },
    "mocha": {
        "_name": "Catppuccin Mocha",
        "bg": "#1e1e2e", "fg": "#cdd6f4",
        "surface": "#181825", "border": "#585b70",
        "accent": "#cba6f7", "success": "#a6e3a1",
        "danger": "#f38ba8", "warn": "#fab387",
        "muted": "#7f849c",
        "tree_bg": "#181825", "tree_fg": "#cdd6f4",
        "tree_odd": "#11111b", "tree_even": "#181825",
        "tree_sel_bg": "#585b70", "tree_sel_fg": "#f5e0dc",
        "heading_bg": "#1e1e2e", "heading_fg": "#cba6f7",
        "input_bg": "#313244", "input_fg": "#cdd6f4",
        "tooltip_bg": "#585b70", "tooltip_fg": "#f5e0dc",
        "toast_bg": "#313244", "toast_fg": "#cdd6f4",
        "progress_bg": "#313244",
    },
    "nord": {
        "_name": "Nord",
        "bg": "#2e3440", "fg": "#eceff4",
        "surface": "#3b4252", "border": "#4c566a",
        "accent": "#88c0d0", "success": "#a3be8c",
        "danger": "#bf616a", "warn": "#ebcb8b",
        "muted": "#6e7484",
        "tree_bg": "#2e3440", "tree_fg": "#eceff4",
        "tree_odd": "#272b35", "tree_even": "#2e3440",
        "tree_sel_bg": "#4c566a", "tree_sel_fg": "#eceff4",
        "heading_bg": "#3b4252", "heading_fg": "#88c0d0",
        "input_bg": "#3b4252", "input_fg": "#eceff4",
        "tooltip_bg": "#4c566a", "tooltip_fg": "#eceff4",
        "toast_bg": "#3b4252", "toast_fg": "#eceff4",
        "progress_bg": "#3b4252",
    },
    "solarized-dark": {
        "_name": "Solarized Dark",
        "bg": "#002b36", "fg": "#93a1a1",
        "surface": "#073642", "border": "#586e75",
        "accent": "#268bd2", "success": "#859900",
        "danger": "#dc322f", "warn": "#b58900",
        "muted": "#586e75",
        "tree_bg": "#002b36", "tree_fg": "#93a1a1",
        "tree_odd": "#073642", "tree_even": "#002b36",
        "tree_sel_bg": "#586e75", "tree_sel_fg": "#eee8d5",
        "heading_bg": "#073642", "heading_fg": "#93a1a1",
        "input_bg": "#073642", "input_fg": "#93a1a1",
        "tooltip_bg": "#073642", "tooltip_fg": "#93a1a1",
        "toast_bg": "#073642", "toast_fg": "#eee8d5",
        "progress_bg": "#073642",
    },
    "solarized-light": {
        "_name": "Solarized Light",
        "bg": "#fdf6e3", "fg": "#586e75",
        "surface": "#eee8d5", "border": "#93a1a1",
        "accent": "#268bd2", "success": "#859900",
        "danger": "#dc322f", "warn": "#b58900",
        "muted": "#93a1a1",
        "tree_bg": "#fdf6e3", "tree_fg": "#586e75",
        "tree_odd": "#eee8d5", "tree_even": "#fdf6e3",
        "tree_sel_bg": "#93a1a1", "tree_sel_fg": "#fdf6e3",
        "heading_bg": "#eee8d5", "heading_fg": "#586e75",
        "input_bg": "#fdf6e3", "input_fg": "#586e75",
        "tooltip_bg": "#eee8d5", "tooltip_fg": "#586e75",
        "toast_bg": "#073642", "toast_fg": "#eee8d5",
        "progress_bg": "#eee8d5",
    },
    "dracula": {
        "_name": "Dracula",
        "bg": "#282a36", "fg": "#f8f8f2",
        "surface": "#44475a", "border": "#6272a4",
        "accent": "#bd93f9", "success": "#50fa7b",
        "danger": "#ff5555", "warn": "#f1fa8c",
        "muted": "#6272a4",
        "tree_bg": "#282a36", "tree_fg": "#f8f8f2",
        "tree_odd": "#21222c", "tree_even": "#282a36",
        "tree_sel_bg": "#44475a", "tree_sel_fg": "#f8f8f2",
        "heading_bg": "#44475a", "heading_fg": "#ff79c6",
        "input_bg": "#44475a", "input_fg": "#f8f8f2",
        "tooltip_bg": "#44475a", "tooltip_fg": "#f8f8f2",
        "toast_bg": "#44475a", "toast_fg": "#f8f8f2",
        "progress_bg": "#44475a",
    },
    "github-light": {
        "_name": "GitHub Light",
        "bg": "#ffffff", "fg": "#24292f",
        "surface": "#f6f8fa", "border": "#d0d7de",
        "accent": "#0969da", "success": "#1a7f37",
        "danger": "#cf222e", "warn": "#9a6700",
        "muted": "#656d76",
        "tree_bg": "#ffffff", "tree_fg": "#24292f",
        "tree_odd": "#f6f8fa", "tree_even": "#ffffff",
        "tree_sel_bg": "#ddf4ff", "tree_sel_fg": "#0969da",
        "heading_bg": "#f6f8fa", "heading_fg": "#24292f",
        "input_bg": "#ffffff", "input_fg": "#24292f",
        "tooltip_bg": "#24292f", "tooltip_fg": "#ffffff",
        "toast_bg": "#24292f", "toast_fg": "#ffffff",
        "progress_bg": "#eaeef2",
    },
}

DEFAULT_THEME = "light"


def list_themes():
    """Возвращает [(ключ, имя), ...] для UI-селектора."""
    return [(k, v["_name"]) for k, v in THEMES.items()]


def get_palette(name):
    """Возвращает палитру по ключу. Падает в light при неизвестном имени."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def apply_theme(name="light", root=None):
    """Применяет ttk стили согласно палитре. Возвращает словарь цветов."""
    c = get_palette(name)

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        try:
            style.theme_use("alt")
        except tk.TclError:
            pass

    style.configure(".", font=("Segoe UI", 10),
                    background=c["bg"], foreground=c["fg"])
    style.configure("TFrame", background=c["bg"])
    style.configure("TLabel", background=c["bg"], foreground=c["fg"])
    style.configure("TLabelFrame", background=c["bg"], foreground=c["fg"],
                    bordercolor=c["border"], lightcolor=c["border"],
                    darkcolor=c["border"])
    style.configure("TLabelFrame.Label", background=c["bg"], foreground=c["fg"])

    style.configure("TButton", padding=(10, 4), font=("Segoe UI", 10),
                    background=c["surface"], foreground=c["fg"],
                    bordercolor=c["border"], focuscolor=c["accent"])
    style.map("TButton",
              background=[("active", c["border"]), ("pressed", c["accent"])],
              foreground=[("active", c["fg"]), ("pressed", c["fg"])])

    style.configure("Accent.TButton", padding=(10, 4),
                    font=("Segoe UI", 10, "bold"),
                    background=c["accent"], foreground=c["surface"])
    style.map("Accent.TButton",
              background=[("active", c["accent"]), ("pressed", c["accent"])])

    style.configure("TEntry", fieldbackground=c["input_bg"],
                    foreground=c["input_fg"], bordercolor=c["border"],
                    insertcolor=c["fg"])
    style.configure("TCombobox", fieldbackground=c["input_bg"],
                    foreground=c["input_fg"], bordercolor=c["border"])
    style.configure("TSeparator", background=c["border"])

    style.configure("Success.TLabel", background=c["bg"],
                    foreground=c["success"], font=("Segoe UI", 10, "bold"))
    style.configure("Danger.TLabel", background=c["bg"],
                    foreground=c["danger"], font=("Segoe UI", 10, "bold"))
    style.configure("Warn.TLabel", background=c["bg"],
                    foreground=c["warn"], font=("Segoe UI", 10, "bold"))
    style.configure("Muted.TLabel", background=c["bg"],
                    foreground=c["muted"], font=("Segoe UI", 9))
    style.configure("Heading.TLabel", background=c["bg"],
                    foreground=c["fg"], font=("Segoe UI", 11, "bold"))

    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10),
                    borderwidth=0, background=c["tree_bg"],
                    foreground=c["tree_fg"], fieldbackground=c["tree_bg"])
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    padding=(8, 5), relief="flat",
                    background=c["heading_bg"], foreground=c["heading_fg"])
    style.map("Treeview",
              background=[("selected", c["tree_sel_bg"])],
              foreground=[("selected", c["tree_sel_fg"])])

    style.configure("TNotebook", background=c["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=c["surface"],
                    foreground=c["fg"], padding=(10, 4),
                    bordercolor=c["border"])
    style.map("TNotebook.Tab",
              background=[("selected", c["bg"])],
              foreground=[("selected", c["accent"])])

    style.configure("Horizontal.TProgressbar", background=c["accent"],
                    troughcolor=c["progress_bg"], borderwidth=0)
    style.configure("TCheckbutton", background=c["bg"], foreground=c["fg"])
    style.map("TCheckbutton", background=[("active", c["bg"])])

    if root is not None:
        try:
            root.configure(bg=c["bg"])
        except tk.TclError:
            pass

    return c
