"""Класс FreeModelAccount + login/fetch_stats/check_all."""

from datetime import datetime, timezone
from typing import Optional

import requests

FREEMODEL_WEB = "https://freemodel.dev"
FREEMODEL_API = "https://api.freemodel.dev"
REQUEST_TIMEOUT = 20

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

KNOWN_MODELS = [
    "gpt-5.5", "gpt-5.4", "gpt-5.4-mini", "gpt-5.3-codex",
    "claude-sonnet-4-5", "claude-sonnet-4-6",
    "claude-opus-4-5", "claude-opus-4-8",
    "claude-code", "o3", "o4-mini",
]


def _normalize_ts(ts):
    """Возвращает epoch-секунды. Принимает секунды или миллисекунды."""
    if not ts:
        return None
    try:
        ts = float(ts)
    except (TypeError, ValueError):
        return None
    if ts > 1e12:  # похоже на миллисекунды
        ts /= 1000.0
    return ts


def fmt_reset_dh(ts, now=None):
    """Форматирует время до сброса как 'дней + часов'.

    >1 дня  -> '5д 12ч'
    <1 дня  -> '3ч 45м'
    <1 часа -> '12м'
    прошло  -> 'сброшен'
    нет     -> '—'
    """
    ts = _normalize_ts(ts)
    if ts is None:
        return "—"
    now = now if now is not None else datetime.now(timezone.utc).timestamp()
    remaining = int(ts - now)
    if remaining <= 0:
        return "сброшен"
    days, rem = divmod(remaining, 86400)
    hours, rem = divmod(rem, 3600)
    mins = rem // 60
    if days > 0:
        return f"{days}д {hours}ч"
    if hours > 0:
        return f"{hours}ч {mins}м"
    return f"{mins}м"


def fmt_reset_abs(ts):
    """Абсолютное время окончания таймера (локальное), напр. '14.06 09:30'."""
    ts = _normalize_ts(ts)
    if ts is None:
        return ""
    try:
        return datetime.fromtimestamp(ts).strftime("%d.%m %H:%M")
    except (OSError, OverflowError, ValueError):
        return ""


def _parse_cookie(raw):
    """Парсит cookie из строк 'a=b; c=d', DevTools-таблицы или построчно."""
    jar = {}
    raw = (raw or "").strip()
    if not raw:
        return jar
    if "\t" in raw:
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("name"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                name, value = parts[0].strip(), parts[1].strip()
                if name and value:
                    jar[name] = value
    elif ";" in raw or "=" in raw:
        for pair in raw.replace(";", "\n").splitlines():
            pair = pair.strip()
            if "=" in pair:
                k, v = pair.split("=", 1)
                jar[k.strip()] = v.strip()
    return jar


class FreeModelAccount:
    def __init__(self, email="", password="", cookie="", api_key="", name=""):
        self.email = email
        self.password = password
        self.cookie = cookie
        self.api_key = api_key or ""
        self.name = name or (email.split("@")[0] if email else "Account")
        self.status = "pending"
        self.balance: Optional[float] = None
        self.credit_limit: Optional[float] = None
        self.used_today: Optional[float] = None
        self.total_used: Optional[float] = None
        self.models = []
        self.error: Optional[str] = None
        self.last_check: Optional[str] = None
        self.plan = ""
        self.plan_status = ""
        self.sub_end = ""
        self.total_requests = 0
        self.total_tokens = 0
        self.used_5h_cents = 0
        self.limit_5h_cents = 0
        self.used_week_cents = 0
        self.limit_week_cents = 0
        self.balance_5h: Optional[float] = None
        self.resets_5h: Optional[int] = None
        self.resets_week = 0
        self.credit_cents = 0
        self.raw_keys = []

    @property
    def source(self):
        """Источник аутентификации: 'cookie', 'password', 'api', 'none'."""
        if self.cookie:
            return "cookie"
        if self.email and self.password:
            return "password"
        if self.api_key:
            return "api"
        return "none"

    @property
    def used_5h_pct(self):
        if not self.limit_5h_cents:
            return None
        return self.used_5h_cents / self.limit_5h_cents * 100

    @property
    def used_week_pct(self):
        if not self.limit_week_cents:
            return None
        return self.used_week_cents / self.limit_week_cents * 100

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "cookie": self.cookie,
            "api_key": self.api_key,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            email=d.get("email", ""),
            password=d.get("password", ""),
            cookie=d.get("cookie", ""),
            api_key=d.get("api_key", ""),
            name=d.get("name", ""),
        )

    # ── Получение статистики через dashboard ────────────────────────────────

    def fetch_stats(self):
        """Тянет /api/billing, /api/usage, /api/keys через cookie."""
        if not self.cookie:
            return False
        jar = _parse_cookie(self.cookie)
        headers = {"User-Agent": UA, "Accept": "application/json"}

        got_data = False
        auth_failed = False
        last_error = None
        for path in ("/api/billing", "/api/usage", "/api/keys"):
            try:
                r = requests.get(f"{FREEMODEL_WEB}{path}", cookies=jar,
                                 headers=headers, timeout=REQUEST_TIMEOUT)
                if r.status_code in (401, 403):
                    auth_failed = True
                    continue
                if r.status_code != 200:
                    last_error = f"{path}: HTTP {r.status_code}"
                    continue
                data = r.json()
                if not isinstance(data, dict):
                    continue
                got_data = True

                if path == "/api/billing":
                    self.credit_cents = data.get("creditCents", 0)
                    sub = data.get("subscription", {}) or {}
                    self.credit_limit = sub.get("limit5hCents") or sub.get("limitWeekCents")
                    self.plan = sub.get("planId", "")
                    self.plan_status = sub.get("status", "")
                    self.sub_end = sub.get("currentPeriodEnd", "")
                elif path == "/api/usage":
                    self.total_requests = data.get("totalRequests", 0)
                    self.total_tokens = data.get("totalTokens", 0)
                    w5 = data.get("window5h", {}) or {}
                    ww = data.get("windowWeek", {}) or {}
                    self.used_5h_cents = w5.get("usedCents", 0)
                    self.limit_5h_cents = w5.get("limitCents", 0)
                    self.resets_5h = w5.get("resetsAt")
                    self.used_week_cents = ww.get("usedCents", 0)
                    self.limit_week_cents = ww.get("limitCents", 0)
                    self.resets_week = ww.get("resetsAt", 0)
                    if self.limit_5h_cents:
                        self.balance_5h = (self.limit_5h_cents - self.used_5h_cents) / 100.0
                elif path == "/api/keys":
                    self.raw_keys = data.get("keys", []) or []
            except requests.exceptions.Timeout:
                last_error = f"{path}: таймаут"
                continue
            except requests.exceptions.RequestException as e:
                last_error = f"{path}: {str(e)[:60]}"
                continue
            except (ValueError, KeyError) as e:
                last_error = f"{path}: формат ответа ({str(e)[:40]})"
                continue

        remaining_5h = max(0, self.limit_5h_cents - self.used_5h_cents)
        self.balance = (self.credit_cents + remaining_5h) / 100.0

        # Помечаем valid только если хотя бы один эндпоинт вернул данные.
        if got_data:
            self.status = "valid"
            return True
        if auth_failed:
            self.status = "invalid"
            self.error = "Cookie истекли или недействительны"
        else:
            self.status = "error"
            self.error = last_error or "Не удалось получить данные"
        return False

    # ── Модели ──────────────────────────────────────────────────────────────

    def fetch_models(self):
        """Список моделей с /v1/models + KNOWN_MODELS."""
        api_models = []
        try:
            headers = {"Accept": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            r = requests.get(f"{FREEMODEL_API}/v1/models",
                             headers=headers, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                api_models = [m["id"] for m in data.get("data", []) if "id" in m]
                for h, val in r.headers.items():
                    hl = h.lower()
                    if "balance" in hl or "credit" in hl:
                        try:
                            self.balance = float(val)
                        except ValueError:
                            pass
        except Exception:
            pass
        seen, out = set(), []
        for m in api_models + KNOWN_MODELS:
            if m not in seen:
                seen.add(m)
                out.append(m)
        return out

    def check_models_endpoint(self):
        """Проверяет API-ключ. True если валиден."""
        if not self.api_key:
            self.models = self.fetch_models()
            return False
        try:
            r = requests.get(f"{FREEMODEL_API}/v1/models",
                             headers={"Authorization": f"Bearer {self.api_key}",
                                      "Accept": "application/json"},
                             timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                self.models = self.fetch_models()
                for h, val in r.headers.items():
                    hl = h.lower()
                    if "balance" in hl or "credit" in hl:
                        try:
                            self.balance = float(val)
                        except ValueError:
                            pass
                self.status = "valid"
                return True
            if r.status_code in (401, 403):
                self.status = "invalid"
                self.error = "Неверный API-ключ"
                return False
            if r.status_code == 503:
                self.status = "unavailable"
                self.error = "API временно недоступен"
                return False
        except requests.exceptions.Timeout:
            self.status = "timeout"
            self.error = "Таймаут"
            return False
        except requests.exceptions.ConnectionError:
            self.status = "error"
            self.error = "Ошибка соединения"
            return False
        self.models = self.fetch_models()
        return False

    # ── Полная проверка ─────────────────────────────────────────────────────

    def check_all(self, progress_cb=None):
        self.last_check = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        self.status = "checking"
        if progress_cb:
            progress_cb()

        if self.cookie:
            self.fetch_stats()

        # Если cookie не дали валидного статуса, пробуем API-ключ как запасной путь.
        if self.api_key and self.status != "valid":
            self.check_models_endpoint()
        elif not self.models and self.status in ("pending", "checking", "valid"):
            self.models = self.fetch_models()

        if self.status in ("pending", "checking"):
            if self.api_key:
                self.status = "error"
                self.error = "API-ключ не работает"
            elif self.email and self.password:
                self.status = "error"
                self.error = "Нет cookie. Войдите через браузер."
            else:
                self.status = "error"
                self.error = "Нет данных для входа"

        if progress_cb:
            progress_cb()
