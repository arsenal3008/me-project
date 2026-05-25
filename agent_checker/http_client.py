"""HTTP-клиент для OpenAI-совместимых API.

Содержит кэш валидных ключей, ``http_post``, ``validate_keys`` и
``test_model``. Все функции принимают callable ``log`` — это позволяет
тестировать модуль без GUI и без шумного ``print``.
"""

import json
import socket
import ssl
import threading
import time
import urllib.request as urllib2
from urllib.parse import urlparse

_ssl_ctx = None
try:
    _ssl_ctx = ssl.create_default_context()
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE
except Exception:
    _ssl_ctx = None

_HTTP = 'urllib'
try:
    import warnings
    warnings.filterwarnings('ignore')
    import requests as _requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    warnings.filterwarnings('ignore', category=InsecureRequestWarning)
    _HTTP = 'requests'
except ImportError:
    _requests = None

ERR_DESC = {
    400: 'Неизвестная модель',
    401: 'Неверный API ключ',
    403: 'Доступ запрещён (Cloudflare?)',
    429: 'Превышен лимит запросов',
    500: 'Внутренняя ошибка сервера',
    502: 'Шлюз недоступен',
    503: 'Провайдер не отвечает',
}

VALID_KEYS_CACHE = {}
VALID_KEYS_LOCK = threading.Lock()


def http_backend():
    return _HTTP


def invalidate_cache(base_url=None):
    """Сбросить кэш для конкретного ``base_url`` или весь."""
    with VALID_KEYS_LOCK:
        if base_url is None:
            VALID_KEYS_CACHE.clear()
        else:
            VALID_KEYS_CACHE.pop(base_url.rstrip('/'), None)


def http_post(url, body, headers, timeout=20):
    if _HTTP == 'requests':
        r = _requests.post(url, json=body, headers=headers, timeout=timeout, verify=False)
        return r.status_code, r.text
    req = urllib2.Request(url, json.dumps(body).encode('utf-8'), headers)
    if _ssl_ctx is not None:
        resp = urllib2.urlopen(req, timeout=timeout, context=_ssl_ctx)
    else:
        resp = urllib2.urlopen(req, timeout=timeout)
    data = resp.read()
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'replace')
    return resp.getcode(), data


def _short(k):
    return (k[:12] + '...') if k else ''


def _looks_like_model_error(msg):
    m = msg.lower()
    return 'model' in m and ('support' in m or 'not found' in m or 'not exist' in m)


def validate_keys(base_url, all_keys, provider_models=None, provider_name='', timeout=10, log=print):
    """Вернуть список из одного рабочего ключа или ``[]``.

    Используется первый ID модели из ``provider_models`` (dict), иначе
    fallback ``gpt-4o-mini``. Ключ считается рабочим при HTTP 200, при
    «модель не найдена» (401/403 с упоминанием модели), а также при
    429/5xx (проблема на стороне сервиса, не ключа).
    """
    url = base_url.rstrip('/') + '/chat/completions'
    tag = provider_name or url
    if provider_models:
        first_mid = next(iter(provider_models))
    else:
        first_mid = 'gpt-4o-mini'
    for k in all_keys:
        if not k:
            continue
        body = {'model': first_mid, 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 1}
        headers = {'Authorization': 'Bearer %s' % k, 'Content-Type': 'application/json'}
        try:
            code, text = http_post(url, body, headers, timeout=timeout)
        except Exception as e:
            log('[%s] %s -> %s' % (tag, _short(k), e))
            continue
        if code == 200:
            log('[%s] %s -> HTTP 200 (ключ работает)' % (tag, _short(k)))
            return [k]
        if code in (401, 403):
            try:
                err = (json.loads(text).get('error') or {}).get('message', '') or ''
            except Exception:
                err = (text or '')[:120]
            if _looks_like_model_error(err):
                log('[%s] %s -> HTTP %d модель не найдена, ключ работает' % (tag, _short(k), code))
                return [k]
            log('[%s] %s -> HTTP %d ключ НЕВЕРНЫЙ (%s)' % (tag, _short(k), code, err[:60]))
            continue
        # 429 / 5xx / другое — серверная проблема, ключ считаем рабочим
        log('[%s] %s -> HTTP %d (ключ считается рабочим)' % (tag, _short(k), code))
        return [k]
    log('[%s] URL=%s keys=%d valid=0' % (tag, url, len(all_keys)))
    return []


def test_model(base_url, api_keys, model_id, timeout=20, retries=2,
               provider_models=None, log=print):
    start = time.time()
    if not api_keys:
        return False, 'Нет API ключей', 0.0
    cache_key = base_url.rstrip('/')
    with VALID_KEYS_LOCK:
        valid = VALID_KEYS_CACHE.get(cache_key)
    if valid is None:
        valid = validate_keys(base_url, api_keys, provider_models=provider_models,
                              provider_name=cache_key, timeout=min(timeout, 10), log=log)
        with VALID_KEYS_LOCK:
            VALID_KEYS_CACHE[cache_key] = valid
    if not valid:
        return False, 'Ни один ключ не прошёл проверку', 0.0
    url = base_url.rstrip('/') + '/chat/completions'
    last_err = 'Все ключи не подошли'
    for key_idx, api_key in enumerate(valid):
        body = {
            'model': model_id,
            'messages': [{'role': 'user', 'content': 'say ok'}],
            'max_tokens': 5,
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 AgentChecker',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + api_key,
        }
        if 'localhost' not in url and '127.0.0.1' not in url:
            headers['Origin'] = 'https://opencode.ai'
            headers['Referer'] = 'https://opencode.ai/'
        for attempt in range(retries + 1):
            try:
                code, text = http_post(url, body, headers, timeout=timeout)
            except Exception as e:
                elapsed = time.time() - start
                last_err = 'Ошибка соединения: %s' % str(e)[:60]
                if key_idx < len(valid) - 1:
                    break
                return False, last_err, elapsed
            elapsed = time.time() - start
            log('[TEST] %s attempt=%d model=%s HTTP=%d %s' %
                (_short(api_key), attempt, model_id, code, (text or '').strip()[:120]))
            if code == 429 and attempt < retries:
                time.sleep(3 * (attempt + 1))
                continue
            try:
                data = json.loads(text)
            except Exception:
                raw = (text or '').strip()[:120]
                if raw:
                    return False, raw, elapsed
                reason = 'Cloudflare/блокировка' if code == 403 else 'пустой ответ'
                return False, 'HTTP %d: %s' % (code, reason), elapsed
            if code == 200 and data.get('choices'):
                content = (data['choices'][0].get('message') or {}).get('content', '') or ''
                return True, content.strip()[:80], elapsed
            err = (data.get('error') or {}).get('message', '') or ''
            label = 'RATE' if code == 429 else 'HTTP %d' % code
            return False, '%s: %s' % (label, ERR_DESC.get(code, '') or err), elapsed
    return False, last_err, time.time() - start


def check_server_online(url, timeout=2):
    """TCP-handshake до хоста, чтобы понять, поднят ли сервер.

    Для URL без явного порта подставляет 80/443 по схеме (а не 11434, как
    в исходной версии — это была ошибка).
    """
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port
        if port is None:
            port = 443 if parsed.scheme == 'https' else 80
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False
