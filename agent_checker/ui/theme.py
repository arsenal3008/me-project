"""Применение тёмной/светлой темы к Tkinter-приложению."""

import tkinter as tk
from tkinter import ttk


def apply(app, dark):
    style = ttk.Style()
    if dark:
        bg, fg, selbg, selfg = '#1e1e1e', '#e0e0e0', '#264f78', '#ffffff'
        entry_bg, entry_fg = '#2d2d2d', '#e0e0e0'
        tree_bg, tree_fg = '#252526', '#e0e0e0'
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
        app.root.configure(bg=bg)
        app.log.configure(bg='#1e1e1e', fg=fg, insertbackground=fg, selectbackground=selbg)
        app.statusbar.configure(background=bg, foreground=fg)
        app.root.option_add('*Menu.background', '#2d2d2d')
        app.root.option_add('*Menu.foreground', '#e0e0e0')
        app.root.option_add('*Menu.activeBackground', '#264f78')
        app.root.option_add('*Menu.activeForeground', '#ffffff')
    else:
        themes = style.theme_names()
        style.theme_use('vista' if 'vista' in themes else 'clam')
        style.configure('TCombobox', padding=3, arrowsize=14)
        style.configure('Accent.TButton', font=('', 9, 'bold'))
        try:
            app.root.configure(bg='SystemButtonFace')
        except tk.TclError:
            app.root.configure(bg='#f0f0f0')
        try:
            app.log.configure(bg='#ffffff', fg='#000000',
                              insertbackground='#000000', selectbackground='#000080')
            app.statusbar.configure(background='SystemButtonFace', foreground='SystemWindowText')
        except tk.TclError:
            pass
        app.root.option_add('*Menu.background', 'SystemButtonFace')
        app.root.option_add('*Menu.foreground', 'SystemWindowText')
        app.root.option_add('*Menu.activeBackground', 'SystemHighlight')
        app.root.option_add('*Menu.activeForeground', 'SystemHighlightText')
    app.lbl_ok.config(foreground='#4ec94e' if dark else 'green')
    app.lbl_fail.config(foreground='#f44747' if dark else 'red')
    app.lbl_untested.config(foreground='#888888' if dark else 'gray')
    app.tree.tag_configure('ok', foreground='#4ec94e' if dark else 'green')
    app.tree.tag_configure('fail', foreground='#f44747' if dark else 'red')
    app.tree.tag_configure('untested', foreground='#888888' if dark else 'gray')
