"""Темы оформления — 16 тёмных красочных палитр + менеджер стилей ttk.

Все темы тёмные и яркие. Каждая палитра — это словарь из 24 цветов; чтобы
добавить свою тему, просто скопируйте любой блок и поменяйте цвета. Менять
нужно только этот файл — остальная программа подхватит темы автоматически.
"""

import tkinter as tk
from tkinter import ttk


# ─── 16 тёмных красочных палитр ──────────────────────────────────────────────

THEMES = {
    "midnight": {
        "_name": "🌌 Midnight",
        "bg": "#1a1b26", "fg": "#c0caf5",
        "surface": "#24283b", "border": "#414868",
        "accent": "#7aa2f7", "success": "#9ece6a",
        "danger": "#f7768e", "warn": "#e0af68",
        "muted": "#565f89",
        "tree_bg": "#1a1b26", "tree_fg": "#c0caf5",
        "tree_odd": "#16161e", "tree_even": "#1a1b26",
        "tree_sel_bg": "#283457", "tree_sel_fg": "#c0caf5",
        "heading_bg": "#24283b", "heading_fg": "#7dcfff",
        "input_bg": "#24283b", "input_fg": "#c0caf5",
        "tooltip_bg": "#24283b", "tooltip_fg": "#c0caf5",
        "toast_bg": "#24283b", "toast_fg": "#c0caf5",
        "progress_bg": "#24283b",
    },
    "mocha": {
        "_name": "☕ Catppuccin Mocha",
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
    "dracula": {
        "_name": "🧛 Dracula",
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
    "nord": {
        "_name": "🏔️ Nord",
        "bg": "#2e3440", "fg": "#eceff4",
        "surface": "#3b4252", "border": "#4c566a",
        "accent": "#88c0d0", "success": "#a3be8c",
        "danger": "#bf616a", "warn": "#ebcb8b",
        "muted": "#6e7484",
        "tree_bg": "#2e3440", "tree_fg": "#eceff4",
        "tree_odd": "#272b35", "tree_even": "#2e3440",
        "tree_sel_bg": "#434c5e", "tree_sel_fg": "#8fbcbb",
        "heading_bg": "#3b4252", "heading_fg": "#81a1c1",
        "input_bg": "#3b4252", "input_fg": "#eceff4",
        "tooltip_bg": "#4c566a", "tooltip_fg": "#eceff4",
        "toast_bg": "#3b4252", "toast_fg": "#eceff4",
        "progress_bg": "#3b4252",
    },
    "synthwave": {
        "_name": "🌆 Synthwave '84",
        "bg": "#241b2f", "fg": "#f8f8f2",
        "surface": "#2a1f3d", "border": "#495495",
        "accent": "#ff7edb", "success": "#72f1b8",
        "danger": "#fe4450", "warn": "#fede5d",
        "muted": "#848bbd",
        "tree_bg": "#241b2f", "tree_fg": "#f8f8f2",
        "tree_odd": "#1e1729", "tree_even": "#241b2f",
        "tree_sel_bg": "#463465", "tree_sel_fg": "#ff7edb",
        "heading_bg": "#2a1f3d", "heading_fg": "#36f9f6",
        "input_bg": "#2a1f3d", "input_fg": "#f8f8f2",
        "tooltip_bg": "#463465", "tooltip_fg": "#ff7edb",
        "toast_bg": "#2a1f3d", "toast_fg": "#f8f8f2",
        "progress_bg": "#2a1f3d",
    },
    "cyberpunk": {
        "_name": "🤖 Cyberpunk",
        "bg": "#0a0e14", "fg": "#e6e1cf",
        "surface": "#131721", "border": "#2d3640",
        "accent": "#fee801", "success": "#00ff9c",
        "danger": "#ff003c", "warn": "#ffae00",
        "muted": "#5c6773",
        "tree_bg": "#0a0e14", "tree_fg": "#e6e1cf",
        "tree_odd": "#07090d", "tree_even": "#0a0e14",
        "tree_sel_bg": "#1f2733", "tree_sel_fg": "#fee801",
        "heading_bg": "#131721", "heading_fg": "#00e5ff",
        "input_bg": "#131721", "input_fg": "#e6e1cf",
        "tooltip_bg": "#1f2733", "tooltip_fg": "#fee801",
        "toast_bg": "#131721", "toast_fg": "#e6e1cf",
        "progress_bg": "#131721",
    },
    "tokyonight-storm": {
        "_name": "🗼 Tokyo Storm",
        "bg": "#24283b", "fg": "#c0caf5",
        "surface": "#1f2335", "border": "#3b4261",
        "accent": "#bb9af7", "success": "#9ece6a",
        "danger": "#f7768e", "warn": "#ff9e64",
        "muted": "#565f89",
        "tree_bg": "#24283b", "tree_fg": "#c0caf5",
        "tree_odd": "#1f2335", "tree_even": "#24283b",
        "tree_sel_bg": "#364a82", "tree_sel_fg": "#c0caf5",
        "heading_bg": "#1f2335", "heading_fg": "#2ac3de",
        "input_bg": "#1f2335", "input_fg": "#c0caf5",
        "tooltip_bg": "#364a82", "tooltip_fg": "#c0caf5",
        "toast_bg": "#1f2335", "toast_fg": "#c0caf5",
        "progress_bg": "#1f2335",
    },
    "forest": {
        "_name": "🌲 Emerald Forest",
        "bg": "#0f1a14", "fg": "#d3e8d8",
        "surface": "#16261d", "border": "#2c4636",
        "accent": "#34d399", "success": "#6ee7b7",
        "danger": "#f87171", "warn": "#fbbf24",
        "muted": "#5b7568",
        "tree_bg": "#0f1a14", "tree_fg": "#d3e8d8",
        "tree_odd": "#0b1410", "tree_even": "#0f1a14",
        "tree_sel_bg": "#234232", "tree_sel_fg": "#d3e8d8",
        "heading_bg": "#16261d", "heading_fg": "#4ade80",
        "input_bg": "#16261d", "input_fg": "#d3e8d8",
        "tooltip_bg": "#234232", "tooltip_fg": "#d3e8d8",
        "toast_bg": "#16261d", "toast_fg": "#d3e8d8",
        "progress_bg": "#16261d",
    },
    "ember": {
        "_name": "🔥 Ember Volcano",
        "bg": "#1a1212", "fg": "#f0dcd4",
        "surface": "#261917", "border": "#4a2f28",
        "accent": "#ff6b35", "success": "#b9e468",
        "danger": "#ff4040", "warn": "#ffb627",
        "muted": "#7a5f57",
        "tree_bg": "#1a1212", "tree_fg": "#f0dcd4",
        "tree_odd": "#140d0d", "tree_even": "#1a1212",
        "tree_sel_bg": "#43271f", "tree_sel_fg": "#ffb627",
        "heading_bg": "#261917", "heading_fg": "#ff8c42",
        "input_bg": "#261917", "input_fg": "#f0dcd4",
        "tooltip_bg": "#43271f", "tooltip_fg": "#ffb627",
        "toast_bg": "#261917", "toast_fg": "#f0dcd4",
        "progress_bg": "#261917",
    },
    "rose-pine": {
        "_name": "🌹 Rosé Pine Moon",
        "bg": "#232136", "fg": "#e0def4",
        "surface": "#2a273f", "border": "#44415a",
        "accent": "#c4a7e7", "success": "#9ccfd8",
        "danger": "#eb6f92", "warn": "#f6c177",
        "muted": "#6e6a86",
        "tree_bg": "#232136", "tree_fg": "#e0def4",
        "tree_odd": "#1f1d2e", "tree_even": "#232136",
        "tree_sel_bg": "#393552", "tree_sel_fg": "#e0def4",
        "heading_bg": "#2a273f", "heading_fg": "#ea9a97",
        "input_bg": "#2a273f", "input_fg": "#e0def4",
        "tooltip_bg": "#393552", "tooltip_fg": "#e0def4",
        "toast_bg": "#2a273f", "toast_fg": "#e0def4",
        "progress_bg": "#2a273f",
    },
    "gruvbox": {
        "_name": "🍂 Gruvbox Dark",
        "bg": "#282828", "fg": "#ebdbb2",
        "surface": "#3c3836", "border": "#504945",
        "accent": "#fabd2f", "success": "#b8bb26",
        "danger": "#fb4934", "warn": "#fe8019",
        "muted": "#928374",
        "tree_bg": "#282828", "tree_fg": "#ebdbb2",
        "tree_odd": "#1d2021", "tree_even": "#282828",
        "tree_sel_bg": "#504945", "tree_sel_fg": "#fbf1c7",
        "heading_bg": "#3c3836", "heading_fg": "#83a598",
        "input_bg": "#3c3836", "input_fg": "#ebdbb2",
        "tooltip_bg": "#504945", "tooltip_fg": "#fbf1c7",
        "toast_bg": "#3c3836", "toast_fg": "#ebdbb2",
        "progress_bg": "#3c3836",
    },
    "monokai-pro": {
        "_name": "🎨 Monokai Pro",
        "bg": "#2d2a2e", "fg": "#fcfcfa",
        "surface": "#363337", "border": "#5b595c",
        "accent": "#ffd866", "success": "#a9dc76",
        "danger": "#ff6188", "warn": "#fc9867",
        "muted": "#727072",
        "tree_bg": "#2d2a2e", "tree_fg": "#fcfcfa",
        "tree_odd": "#221f22", "tree_even": "#2d2a2e",
        "tree_sel_bg": "#423f43", "tree_sel_fg": "#fcfcfa",
        "heading_bg": "#363337", "heading_fg": "#78dce8",
        "input_bg": "#363337", "input_fg": "#fcfcfa",
        "tooltip_bg": "#423f43", "tooltip_fg": "#fcfcfa",
        "toast_bg": "#363337", "toast_fg": "#fcfcfa",
        "progress_bg": "#363337",
    },
    "oceanic": {
        "_name": "🌊 Deep Ocean",
        "bg": "#0b1e2d", "fg": "#c5e4f3",
        "surface": "#112a3d", "border": "#1f4a63",
        "accent": "#29b6f6", "success": "#26d0a0",
        "danger": "#ff5370", "warn": "#ffcb6b",
        "muted": "#4a6b7d",
        "tree_bg": "#0b1e2d", "tree_fg": "#c5e4f3",
        "tree_odd": "#08161f", "tree_even": "#0b1e2d",
        "tree_sel_bg": "#15384f", "tree_sel_fg": "#c5e4f3",
        "heading_bg": "#112a3d", "heading_fg": "#64ffda",
        "input_bg": "#112a3d", "input_fg": "#c5e4f3",
        "tooltip_bg": "#15384f", "tooltip_fg": "#c5e4f3",
        "toast_bg": "#112a3d", "toast_fg": "#c5e4f3",
        "progress_bg": "#112a3d",
    },
    "galaxy": {
        "_name": "🪐 Galaxy",
        "bg": "#13111c", "fg": "#e4def7",
        "surface": "#1d1830", "border": "#3a2f55",
        "accent": "#b388ff", "success": "#5cf2c2",
        "danger": "#ff5d8f", "warn": "#ffd166",
        "muted": "#6a5f87",
        "tree_bg": "#13111c", "tree_fg": "#e4def7",
        "tree_odd": "#0f0d17", "tree_even": "#13111c",
        "tree_sel_bg": "#2e2545", "tree_sel_fg": "#e4def7",
        "heading_bg": "#1d1830", "heading_fg": "#ff79c6",
        "input_bg": "#1d1830", "input_fg": "#e4def7",
        "tooltip_bg": "#2e2545", "tooltip_fg": "#e4def7",
        "toast_bg": "#1d1830", "toast_fg": "#e4def7",
        "progress_bg": "#1d1830",
    },
    "aurora": {
        "_name": "🌠 Aurora",
        "bg": "#11181c", "fg": "#d7f0e6",
        "surface": "#182428", "border": "#2c4248",
        "accent": "#00e5c0", "success": "#7fffd4",
        "danger": "#ff6e7f", "warn": "#ffd97d",
        "muted": "#557068",
        "tree_bg": "#11181c", "tree_fg": "#d7f0e6",
        "tree_odd": "#0c1216", "tree_even": "#11181c",
        "tree_sel_bg": "#1f343a", "tree_sel_fg": "#d7f0e6",
        "heading_bg": "#182428", "heading_fg": "#a78bfa",
        "input_bg": "#182428", "input_fg": "#d7f0e6",
        "tooltip_bg": "#1f343a", "tooltip_fg": "#d7f0e6",
        "toast_bg": "#182428", "toast_fg": "#d7f0e6",
        "progress_bg": "#182428",
    },
    "sunset": {
        "_name": "🌇 Sunset",
        "bg": "#1c1421", "fg": "#ffe6e0",
        "surface": "#281a30", "border": "#4a3050",
        "accent": "#ff7e9d", "success": "#8fe388",
        "danger": "#ff5252", "warn": "#ffb454",
        "muted": "#7a5f7d",
        "tree_bg": "#1c1421", "tree_fg": "#ffe6e0",
        "tree_odd": "#160f1a", "tree_even": "#1c1421",
        "tree_sel_bg": "#3a2640", "tree_sel_fg": "#ffe6e0",
        "heading_bg": "#281a30", "heading_fg": "#ffa45c",
        "input_bg": "#281a30", "input_fg": "#ffe6e0",
        "tooltip_bg": "#3a2640", "tooltip_fg": "#ffe6e0",
        "toast_bg": "#281a30", "toast_fg": "#ffe6e0",
        "progress_bg": "#281a30",
    },
}

# Тема по умолчанию (все темы тёмные). Старый ключ «light» из сохранённых
# настроек безопасно подменяется на неё через get_palette().
DEFAULT_THEME = "midnight"


def list_themes():
    """Возвращает [(ключ, имя), ...] для UI-селектора."""
    return [(k, v["_name"]) for k, v in THEMES.items()]


def get_palette(name):
    """Возвращает палитру по ключу. Падает в тему по умолчанию при неизвестном имени."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def apply_theme(name="midnight", root=None):
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
    style.configure("TLabelFrame.Label", background=c["bg"],
                    foreground=c["accent"])

    style.configure("TButton", padding=(10, 4), font=("Segoe UI", 10),
                    background=c["surface"], foreground=c["fg"],
                    bordercolor=c["border"], focuscolor=c["accent"])
    style.map("TButton",
              background=[("active", c["border"]), ("pressed", c["accent"])],
              foreground=[("active", c["fg"]), ("pressed", c["bg"])])

    style.configure("Accent.TButton", padding=(10, 4),
                    font=("Segoe UI", 10, "bold"),
                    background=c["accent"], foreground=c["bg"],
                    bordercolor=c["accent"])
    style.map("Accent.TButton",
              background=[("active", c["accent"]), ("pressed", c["accent"])],
              foreground=[("active", c["bg"]), ("pressed", c["bg"])])

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
                    foreground=c["accent"], font=("Segoe UI", 11, "bold"))

    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10),
                    borderwidth=0, background=c["tree_bg"],
                    foreground=c["tree_fg"], fieldbackground=c["tree_bg"])
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    padding=(8, 5), relief="flat",
                    background=c["heading_bg"], foreground=c["heading_fg"])
    style.map("Treeview.Heading",
              background=[("active", c["surface"])],
              foreground=[("active", c["accent"])])
    style.map("Treeview",
              background=[("selected", c["tree_sel_bg"])],
              foreground=[("selected", c["tree_sel_fg"])])

    style.configure("TNotebook", background=c["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", background=c["surface"],
                    foreground=c["muted"], padding=(12, 5),
                    bordercolor=c["border"])
    style.map("TNotebook.Tab",
              background=[("selected", c["bg"]), ("active", c["border"])],
              foreground=[("selected", c["accent"]), ("active", c["fg"])])

    style.configure("Horizontal.TProgressbar", background=c["accent"],
                    troughcolor=c["progress_bg"], borderwidth=0,
                    lightcolor=c["accent"], darkcolor=c["accent"])
    style.configure("TCheckbutton", background=c["bg"], foreground=c["fg"])
    style.map("TCheckbutton",
              background=[("active", c["bg"])],
              foreground=[("active", c["accent"])])

    if root is not None:
        try:
            root.configure(bg=c["bg"])
        except tk.TclError:
            pass

    return c
