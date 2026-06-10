"""Загрузка и сохранение пользовательских настроек fm_settings.json.

Структура settings:
- theme: ключ темы (light/dark/mocha/nord/...)
- geometry: WxH+X+Y главного окна
- detail_visible: bool
- column_widths: {col: int}
- visible_columns: [col1, col2, ...]
- dialog_geometries: {dialog_key: WxH+X+Y}
- sort_column: str | None
- sort_reverse: bool
"""

import json
import os
import re


DEFAULTS = {
    "theme": "light",
    "geometry": "1200x700+100+100",
    "detail_visible": True,
    "column_widths": {
        "name": 130, "email": 200, "plan": 80, "sub_end": 110,
        "source": 80, "status": 90, "balance": 100, "credit": 90,
        "used_5h_pct": 75, "used_week_pct": 75,
        "reset_5h": 85, "reset_week": 85,
        "requests": 80, "keys": 60,
        "last_check": 150, "error": 200,
    },
    "visible_columns": [
        "name", "email", "plan", "source", "status", "balance",
        "used_5h_pct", "used_week_pct", "reset_5h", "reset_week",
        "requests", "last_check", "error",
    ],
    "dialog_geometries": {},
    "sort_column": None,
    "sort_reverse": False,
    "auto_check_on_start": False,
    "browser_login_method": "chrome",
    "reset_cols_added": False,
}


def _settings_path():
    here = os.path.dirname(os.path.abspath(__file__))
    project = os.path.dirname(here)
    return os.path.join(project, "fm_settings.json")


def load():
    """Загружает настройки, мерджит с DEFAULTS."""
    out = json.loads(json.dumps(DEFAULTS))
    path = _settings_path()
    if not os.path.isfile(path):
        return out
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return out
    if isinstance(data, dict):
        for k, v in data.items():
            if k in DEFAULTS:
                # Мерджим словари по ключам
                if isinstance(DEFAULTS[k], dict) and isinstance(v, dict):
                    merged = dict(DEFAULTS[k])
                    merged.update(v)
                    out[k] = merged
                else:
                    out[k] = v

    # Одноразовая миграция: добавляем новые колонки таймеров в уже
    # сохранённый список видимых колонок (чтобы они появились у тех,
    # кто запускал прежнюю версию).
    if not out.get("reset_cols_added"):
        vis = out.get("visible_columns") or []
        if vis:
            new_cols = [c for c in ("reset_5h", "reset_week") if c not in vis]
            if new_cols:
                if "used_week_pct" in vis:
                    pos = vis.index("used_week_pct") + 1
                else:
                    pos = len(vis)
                vis[pos:pos] = new_cols
            out["visible_columns"] = vis
        out["reset_cols_added"] = True

    return out


def save(data):
    """Сохраняет настройки, оставляя только известные ключи."""
    path = _settings_path()
    payload = {k: data[k] for k in DEFAULTS if k in data}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def secure_chmod(path):
    """Выставляет права 0600 (только владелец) — для файлов с секретами.

    На Windows os.chmod почти не влияет на ACL, но вызов безопасен.
    """
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


# ─── Геометрия окон ──────────────────────────────────────────────────────────

def parse_geometry(geom):
    """Парсит WxH[+X+Y] -> (w, h, pos_str).
    pos_str — '+X+Y' или '' если нет позиции.
    """
    if not geom:
        return None
    m = re.match(r"^(\d+)x(\d+)([+-]\d+[+-]\d+)?", str(geom))
    if not m:
        return None
    try:
        w, h = int(m.group(1)), int(m.group(2))
        pos = m.group(3) or ""
        return w, h, pos
    except ValueError:
        return None


def safe_geometry(geom, screen_w, screen_h, min_w=300, min_h=200):
    """Валидирует геометрию: размер в пределах экрана, позиция видна.
    Возвращает строку 'WxH+X+Y' или 'WxH' если позиция невалидна, None если совсем плохо.
    """
    parsed = parse_geometry(geom)
    if not parsed:
        return None
    w, h, pos = parsed
    if w < min_w or h < min_h:
        return None
    if w > screen_w or h > screen_h:
        return None
    if pos:
        pm = re.match(r"^([+-]\d+)([+-]\d+)$", pos)
        if pm:
            try:
                x_raw = int(pm.group(1))
                y_raw = int(pm.group(2))
                x_abs = screen_w - abs(x_raw) if x_raw < 0 else x_raw
                y_abs = screen_h - abs(y_raw) if y_raw < 0 else y_raw
                if x_abs + w < 40 or x_abs > screen_w - 20:
                    return f"{w}x{h}"
                if y_abs + h < 40 or y_abs > screen_h - 20:
                    return f"{w}x{h}"
                return f"{w}x{h}{pos}"
            except ValueError:
                return f"{w}x{h}"
    return f"{w}x{h}"
