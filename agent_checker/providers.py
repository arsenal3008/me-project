"""Загрузка/сохранение провайдеров и моделей."""

import json
import os

from .jsonc import read_jsonc
from .paths import PROVIDERS_JSON, existing_opencode_config


def is_free(model_id, model_name):
    return 'free' in (model_id or '').lower() or 'free' in (model_name or '').lower()


def _coerce_keys(opts):
    api_keys = list(opts.get('apiKeys', []) or [])
    api_key = opts.get('apiKey', '') or ''
    if api_key and api_key not in api_keys:
        api_keys.insert(0, api_key)
    return api_keys, api_key


def load_from_opencode(log=print):
    """Загрузить провайдеры и модели из существующего opencode-конфига.

    Возвращает кортеж ``(providers, model_list, path_or_none)``.
    """
    providers = {}
    model_list = []
    path = existing_opencode_config()
    if not path:
        log('Не удалось найти opencode.jsonc')
        return providers, model_list, None
    try:
        cfg = read_jsonc(path)
    except Exception as e:
        log('Ошибка чтения %s: %s' % (path, e))
        return providers, model_list, None
    total = 0
    for pn, pc in (cfg.get('provider') or {}).items():
        opts = pc.get('options', {}) or {}
        base_url = (opts.get('baseURL') or '').rstrip('/')
        api_keys, api_key = _coerce_keys(opts)
        if not api_keys:
            continue
        providers[pn] = {
            'base_url': base_url,
            'api_key': api_keys[0],
            'api_keys': api_keys,
            'models': {},
        }
        for mid, mc in (pc.get('models') or {}).items():
            mn = (mc or {}).get('name', mid)
            fr = is_free(mid, mn)
            providers[pn]['models'][mid] = {'name': mn, 'source': 'opencode', 'free': fr}
            model_list.append((pn, mid, mn, 'opencode', fr))
            total += 1
    log('Загружено из %s: %d моделей' % (os.path.basename(path), total))
    return providers, model_list, path


def merge_opencode_file(providers, model_list, path, log=print):
    """Догрузить модели из произвольного файла. Возвращает ``(added, ok)``."""
    try:
        cfg = read_jsonc(path)
    except Exception as e:
        log('Ошибка загрузки %s: %s' % (path, e))
        return 0, False
    added = 0
    for pn, pc in (cfg.get('provider') or {}).items():
        opts = pc.get('options', {}) or {}
        base_url = (opts.get('baseURL') or '').rstrip('/')
        api_keys, api_key = _coerce_keys(opts)
        if pn not in providers:
            providers[pn] = {
                'base_url': base_url,
                'api_key': api_keys[0] if api_keys else api_key,
                'api_keys': api_keys,
                'models': {},
            }
        else:
            if base_url:
                providers[pn]['base_url'] = base_url
            existing = providers[pn].setdefault('api_keys', [])
            for k in api_keys:
                if k and k not in existing:
                    existing.append(k)
            if not providers[pn].get('api_key') and existing:
                providers[pn]['api_key'] = existing[0]
        prov = providers[pn]
        for mid, mc in (pc.get('models') or {}).items():
            if mid in prov['models']:
                continue
            mn = (mc or {}).get('name', mid)
            fr = is_free(mid, mn)
            prov['models'][mid] = {'name': mn, 'source': 'opencode', 'free': fr}
            model_list.append((pn, mid, mn, 'opencode', fr))
            added += 1
    return added, True


def save_providers(providers, path=PROVIDERS_JSON):
    """Сохранить только базовый URL и ключи. Модели не дублируем."""
    data = {}
    for pn, p in providers.items():
        data[pn] = {
            'base_url': p.get('base_url', ''),
            'api_key': p.get('api_key', ''),
            'api_keys': list(p.get('api_keys', [])),
        }
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def purge_empty(providers):
    for pn in list(providers.keys()):
        if not providers[pn].get('models'):
            del providers[pn]


def propagate_keys(providers):
    """Скопировать ключи от первого провайдера с ключами на остальных с тем же base_url."""
    source_keys = []
    source_url = ''
    for p in providers.values():
        if p.get('api_keys'):
            source_keys = p['api_keys']
            source_url = p.get('base_url', '')
            break
    if not source_keys:
        return
    for p in providers.values():
        if not p.get('api_keys') and p.get('base_url') == source_url:
            p['api_keys'] = list(source_keys)
            if not p.get('api_key'):
                p['api_key'] = source_keys[0]
