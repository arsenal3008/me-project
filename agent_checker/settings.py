"""Загрузка и сохранение пользовательских настроек."""

import json
import os

from .paths import SETTINGS_JSON

DEFAULTS = {
    'timeout': 20,
    'retries': 2,
    'delay': 0.3,
    'dark_mode': False,
    'geometry': '1020x720',
    'log_height': 5,
    'auto_save_config': True,
    'auto_start_ollama': True,
    'hide_ollama_window': True,
}


def load(path=SETTINGS_JSON):
    out = dict(DEFAULTS)
    if not os.path.isfile(path):
        return out
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return out
    for k, v in data.items():
        if k in DEFAULTS:
            out[k] = v
    return out


def save(data, path=SETTINGS_JSON):
    payload = {k: data[k] for k in DEFAULTS if k in data}
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
