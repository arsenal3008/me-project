"""Диалог экспорта моделей в opencode.jsonc."""

import os
import shutil
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from ..exporter import build_jsonc
from ..paths import SCRIPT_DIR

OK = 'УСПЕХ'
FAIL = 'НЕУДАЧА'
DASH = '—'
CHK = '☑'
UNCHK = '☐'
PARTIAL = '☒'


def open_export_dialog(app, preselect_ok_only=False):
    root = app.root
    dlg = tk.Toplevel(root)
    dlg.title('Экспорт в opencode.jsonc')
    dlg.geometry('720x650')
    dlg.transient(root)
    dlg.grab_set()
    f = ttk.Frame(dlg, padding=10)
    f.pack(fill=tk.BOTH, expand=True)

    pf = ttk.Frame(f)
    pf.pack(fill=tk.X, pady=(0, 5))
    ttk.Label(pf, text='Путь:').pack(side=tk.LEFT)
    path_v = tk.StringVar(value=os.path.join(SCRIPT_DIR, 'opencode.jsonc'))
    ttk.Entry(pf, textvariable=path_v, width=55).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def browse():
        p = filedialog.asksaveasfilename(
            title='Сохранить конфиг',
            defaultextension='.jsonc',
            filetypes=[('JSONC', '*.jsonc'), ('JSON', '*.json'), ('All', '*.*')],
            initialfile=os.path.basename(path_v.get()),
            initialdir=os.path.dirname(path_v.get()))
        if p:
            path_v.set(p)

    ttk.Button(pf, text='Обзор', command=browse).pack(side=tk.LEFT)

    bkup_v = tk.BooleanVar(value=True)
    ttk.Checkbutton(
        f,
        text='Создать бэкап оригинала с датой',
        variable=bkup_v,
    ).pack(anchor=tk.W)

    ttk.Label(
        f,
        text='Модели (отметьте нужные, измените порядок):',
        font=('', 9, 'bold'),
    ).pack(anchor=tk.W, pady=(5, 2))
    tvf = ttk.Frame(f)
    tvf.pack(fill=tk.BOTH, expand=True)
    tv = ttk.Treeview(tvf, columns=('chk', 'name', 'info'), show='tree', selectmode='browse', height=14)
    tv.heading('#0', text='')
    tv.column('#0', width=0, stretch=False)
    tv.column('chk', width=30, anchor=tk.CENTER)
    tv.column('name', width=300)
    tv.column('info', width=120)
    v_sb = ttk.Scrollbar(tvf, orient=tk.VERTICAL, command=tv.yview)
    tv.configure(yscrollcommand=v_sb.set)
    tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    v_sb.pack(side=tk.RIGHT, fill=tk.Y)

    rbf = ttk.Frame(f)
    rbf.pack(fill=tk.X, pady=3)

    def _move(delta_to=None, to_pos=None):
        sel = tv.selection()
        if not sel:
            return
        iid = sel[0]
        parent = tv.parent(iid)
        siblings = tv.get_children(parent)
        idx = siblings.index(iid)
        if to_pos == 'top':
            tv.move(iid, parent, 0)
        elif to_pos == 'bottom':
            tv.move(iid, parent, len(siblings))
        elif delta_to is not None:
            new_idx = idx + delta_to
            if 0 <= new_idx < len(siblings):
                tv.move(iid, parent, new_idx)
        tv.selection_set(iid)
        tv.focus(iid)

    ttk.Label(rbf, text='Порядок:').pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(rbf, text='▲ Вверх', width=10, command=lambda: _move(delta_to=-1)).pack(side=tk.LEFT, padx=1)
    ttk.Button(rbf, text='▼ Вниз', width=10, command=lambda: _move(delta_to=1)).pack(side=tk.LEFT, padx=1)
    ttk.Button(rbf, text='⬆ В начало', width=12, command=lambda: _move(to_pos='top')).pack(side=tk.LEFT, padx=1)
    ttk.Button(rbf, text='⬇ В конец', width=12, command=lambda: _move(to_pos='bottom')).pack(side=tk.LEFT, padx=1)

    # Заполнение дерева
    chk_state = {}
    seen_provs = []
    prov_models = {}
    for pn, mid, mn, src, fr in app.model_list:
        if pn not in prov_models:
            prov_models[pn] = []
            seen_provs.append(pn)
        prov_models[pn].append((mid, mn, src, fr))

    for pn in seen_provs:
        r = app.results.get(pn, {})
        piid = tv.insert('', tk.END, values=('', pn, ''), tags=('provider',))
        chk_state[piid] = True
        tv.set(piid, 'chk', CHK)
        raw = prov_models[pn]
        has_prefix = any(mn.startswith('[') and ']' in mn for _, mn, _, _ in raw)
        if has_prefix:
            subgroups = {}
            for mid, mn, src, fr in raw:
                if mn.startswith('[') and ']' in mn:
                    close = mn.index(']')
                    grp = mn[1:close]
                    clean = mn[close + 1:].strip()
                else:
                    grp = ''
                    clean = mn
                subgroups.setdefault(grp, []).append((mid, clean, src, fr))
            for grp_name in sorted(subgroups.keys(),
                                   key=lambda x: ('z' if any(m[3] for m in subgroups[x]) else 'a') + x):
                giid = tv.insert(piid, tk.END, values=('', grp_name, ''), tags=('subgroup',))
                chk_state[giid] = True
                tv.set(giid, 'chk', CHK)
                for mid, clean_name, src, fr in subgroups[grp_name]:
                    res = r.get(mid)
                    info = DASH if res is None else (OK if res['ok'] else FAIL)
                    miid = tv.insert(giid, tk.END, values=('', clean_name, info), tags=('model',))
                    chk_state[miid] = True
                    tv.set(miid, 'chk', CHK)
                tv.item(giid, open=True)
        else:
            for mid, mn, src, fr in raw:
                res = r.get(mid)
                info = DASH if res is None else (OK if res['ok'] else FAIL)
                miid = tv.insert(piid, tk.END, values=('', mn, info), tags=('model',))
                chk_state[miid] = True
                tv.set(miid, 'chk', CHK)
        tv.item(piid, open=True)

    tv.tag_configure('dim', foreground='#888888')

    def _update_vis(iid):
        tags = list(tv.item(iid, 'tags'))
        if chk_state.get(iid, False):
            tags = [t for t in tags if t != 'dim']
        elif 'dim' not in tags:
            tags.append('dim')
        tv.item(iid, tags=tuple(tags))

    def _model_count(iid):
        kids = tv.get_children(iid)
        if not kids:
            return (1 if chk_state.get(iid, False) else 0, 1)
        ok, total = 0, 0
        for k in kids:
            c, t = _model_count(k)
            ok += c
            total += t
        return ok, total

    def _set_tree_state(iid, checked):
        chk_state[iid] = checked
        tv.set(iid, 'chk', CHK if checked else UNCHK)
        _update_vis(iid)
        for k in tv.get_children(iid):
            _set_tree_state(k, checked)

    def _update_up(iid):
        parent = tv.parent(iid)
        if not parent:
            return
        ok, total = _model_count(parent)
        if ok == 0:
            tv.set(parent, 'chk', UNCHK)
            chk_state[parent] = False
        elif ok == total:
            tv.set(parent, 'chk', CHK)
            chk_state[parent] = True
        else:
            tv.set(parent, 'chk', PARTIAL)
            chk_state[parent] = True
        _update_vis(parent)
        _update_up(parent)

    def toggle_check(iid):
        cur = tv.set(iid, 'chk')
        checked = (cur != CHK)
        _set_tree_state(iid, checked)
        _update_up(iid)

    def on_tree_click(e):
        iid = tv.identify_row(e.y)
        if not iid:
            return None
        col = tv.identify_column(e.x)
        if col in ('#0', '#1'):
            toggle_check(iid)
            return 'break'
        return None

    tv.bind('<Button-1>', on_tree_click, '+')

    bf = ttk.Frame(f)
    bf.pack(fill=tk.X, pady=3)

    def _all_models():
        for piid in tv.get_children():
            kids = tv.get_children(piid)
            if not kids:
                continue
            if tv.item(kids[0], 'tags')[0] != 'subgroup':
                for miid in kids:
                    yield miid, tv.set(miid, 'info')
            else:
                for giid in kids:
                    for miid in tv.get_children(giid):
                        yield miid, tv.set(miid, 'info')

    def mark_valid():
        for miid, info in _all_models():
            checked = (info == OK)
            chk_state[miid] = checked
            tv.set(miid, 'chk', CHK if checked else UNCHK)
            _update_vis(miid)
        for piid in tv.get_children():
            for ciid in tv.get_children(piid):
                _update_up(ciid) if not tv.get_children(ciid) else None
                for miid in tv.get_children(ciid):
                    _update_up(miid)

    def uncheck_all():
        for piid in tv.get_children():
            _set_tree_state(piid, False)

    ttk.Button(bf, text='✓ Выбрать рабочие', command=mark_valid).pack(side=tk.LEFT, padx=2)
    ttk.Button(bf, text='☐ Снять все', command=uncheck_all).pack(side=tk.LEFT, padx=2)
    if preselect_ok_only:
        mark_valid()

    ttk.Label(
        f,
        text='Ключи провайдеров (измените при необходимости):',
        font=('', 9, 'bold'),
    ).pack(anchor=tk.W, pady=(8, 2))
    kf = ttk.Frame(f)
    kf.pack(fill=tk.X)
    key_vars = {}
    kff = ttk.Frame(kf)
    kff.pack(fill=tk.X, pady=2)
    kff.columnconfigure(1, weight=1)
    for i, pn in enumerate(seen_provs):
        keys = app.providers.get(pn, {}).get('api_keys', [])
        key_str = keys[0] if keys else ''
        kv = tk.StringVar(value=key_str)
        key_vars[pn] = kv
        ttk.Label(kff, text=pn + ':', width=12, anchor=tk.E, font=('', 8)).grid(
            row=i, column=0, sticky=tk.W, padx=(0, 4), pady=1)
        ke = ttk.Entry(kff, textvariable=kv, width=50, show='*')
        ke.grid(row=i, column=1, sticky=tk.EW, padx=1, pady=1)

        def toggle_show(ke=ke):
            ke.configure(show='' if ke.cget('show') == '*' else '*')

        ttk.Button(kff, text='Показать', width=8, command=toggle_show).grid(
            row=i, column=2, padx=2, pady=1)

    sbf = ttk.Frame(f)
    sbf.pack(fill=tk.X, pady=(10, 0))

    def collect():
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
            if not kids:
                continue
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
                        full_name = '[%s] %s' % (grp_name, clean_name) if grp_name else clean_name
                        mid, src = full_name, 'opencode'
                        for x in app.model_list:
                            if x[0] == pn and x[2] == full_name:
                                mid, src = x[1], x[3]
                                break
                        models_by_prov[pn].append((mid, full_name, src))
            else:
                for miid in kids:
                    if not chk_state.get(miid, False):
                        continue
                    mn = tv.item(miid, 'values')[1]
                    mid, src = mn, 'opencode'
                    for x in app.model_list:
                        if x[0] == pn and x[2] == mn:
                            mid, src = x[1], x[3]
                            break
                    models_by_prov[pn].append((mid, mn, src))
            keys_by_prov[pn] = key_vars[pn].get().strip()
        return provider_order, models_by_prov, keys_by_prov

    def do_save():
        p = path_v.get().strip()
        if not p:
            messagebox.showerror('Ошибка',
                                 'Укажите путь для сохранения')
            return
        if bkup_v.get() and os.path.isfile(p):
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            bak = p + '.bak_' + ts
            try:
                shutil.copy2(p, bak)
            except Exception as e:
                if not messagebox.askyesno(
                        'Бэкап',
                        'Не удалось создать бэкап:\n%s\n\nПродолжить?' % e):
                    return
        provider_order, models_by_prov, keys_by_prov = collect()
        text = build_jsonc(provider_order, app.providers, models_by_prov, keys_by_prov)
        try:
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(text)
            app._log('Экспортировано: %s' % p)
            app._set_status('Экспортировано: %s' % os.path.basename(p))
            dlg.destroy()
        except Exception as e:
            messagebox.showerror('Ошибка',
                                 'Не удалось сохранить:\n%s' % e)

    ttk.Button(sbf, text='\U0001f4be Сохранить',
               style='Accent.TButton', command=do_save).pack(side=tk.LEFT, padx=2)
    ttk.Button(sbf, text='Отмена', command=dlg.destroy).pack(side=tk.LEFT, padx=2)
