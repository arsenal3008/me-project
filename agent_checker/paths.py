"""Кросс-платформенные пути конфигурации и логов."""

import os
import sys

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(PKG_DIR)
SCRIPT_DIR = REPO_DIR

PROVIDERS_JSON = os.path.join(REPO_DIR, 'providers.json')
SETTINGS_JSON = os.path.join(REPO_DIR, 'settings.json')
LOGS_DIR = os.path.join(REPO_DIR, 'logs')


def opencode_config_candidates():
    """Список путей-кандидатов к ``opencode.jsonc``.

    Порядок: ``$OPENCODE_CONFIG`` → ``~/.config/opencode/`` →
    ``%APPDATA%/opencode/`` → рядом со скриптом.
    """
    home = os.path.expanduser('~')
    cands = []
    env = os.environ.get('OPENCODE_CONFIG')
    if env:
        cands.append(env)
    cands.extend([
        os.path.join(home, '.config', 'opencode', 'opencode.jsonc'),
        os.path.join(home, '.config', 'opencode', 'opencode.json'),
    ])
    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA')
        if appdata:
            cands.append(os.path.join(appdata, 'opencode', 'opencode.jsonc'))
    cands.append(os.path.join(REPO_DIR, 'opencode.jsonc'))
    return cands


def existing_opencode_config():
    """Первый существующий путь, либо ``None``."""
    for c in opencode_config_candidates():
        if os.path.isfile(c):
            return c
    return None
