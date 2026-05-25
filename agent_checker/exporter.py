"""Чистые функции построения JSONC-конфига opencode (без UI)."""

import json


def build_jsonc(provider_order, providers, models_by_prov, keys_by_prov):
    """Собрать JSONC-строку для opencode-конфига.

    Использует ``json.dumps`` — это надёжнее, чем ручная конкатенация
    строк (никаких проблем с кавычками/спецсимволами в именах моделей).
    """
    out = {'provider': {}}
    for pn in provider_order:
        opts = {}
        bu = providers.get(pn, {}).get('base_url', '')
        if bu:
            opts['baseURL'] = bu
        k = keys_by_prov.get(pn, '')
        if k:
            opts['apiKey'] = k
        models = {}
        for mid, mn, _src in models_by_prov.get(pn, []):
            models[mid] = {'name': mn}
        out['provider'][pn] = {'name': pn, 'options': opts, 'models': models}
    return json.dumps(out, ensure_ascii=False, indent=2) + '\n'
