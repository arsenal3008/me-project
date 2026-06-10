"""Авто-получение cookie с freemodel.dev.

Две стратегии:
1. system_browser_login — запускает системный Chrome/Edge с временным
   профилем, дожидается логина, читает cookie из SQLite браузера и
   расшифровывает через Windows DPAPI.
2. playwright_login — если установлен playwright, запускает Chromium
   и автоматизирует логин по email/password.

Публичный API:
    login(email, password, method='auto', on_status=None) -> str | None
"""

import base64
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time

# ctypes / ctypes.wintypes доступны только на Windows. Импортируем лениво
# внутри DPAPI-функций, чтобы пакет можно было импортировать на любой ОС
# (иначе всё приложение падало на старте под Linux/macOS).

FREEMODEL_HOST = "freemodel.dev"
FREEMODEL_LOGIN = "https://freemodel.dev/login"
FREEMODEL_DASHBOARD = "https://freemodel.dev/dashboard"


# ─── Поиск браузеров ─────────────────────────────────────────────────────────

def _find_browser_path():
    candidates = [
        (os.environ.get("ProgramFiles", r"C:\Program Files") +
         r"\Google\Chrome\Application\chrome.exe", "chrome"),
        (os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)") +
         r"\Google\Chrome\Application\chrome.exe", "chrome"),
        (os.environ.get("LOCALAPPDATA", "") +
         r"\Google\Chrome\Application\chrome.exe", "chrome"),
        (os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)") +
         r"\Microsoft\Edge\Application\msedge.exe", "edge"),
        (os.environ.get("ProgramFiles", r"C:\Program Files") +
         r"\Microsoft\Edge\Application\msedge.exe", "edge"),
    ]
    for path, kind in candidates:
        if path and os.path.isfile(path):
            return path, kind
    return None, None


# ─── DPAPI расшифровка cookie Chromium ───────────────────────────────────────

def _dpapi_unprotect(blob):
    if not sys.platform.startswith("win"):
        return None
    import ctypes
    import ctypes.wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", ctypes.wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_char))]

    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    in_blob = DATA_BLOB(len(blob), ctypes.cast(
        ctypes.create_string_buffer(blob, len(blob)),
        ctypes.POINTER(ctypes.c_char)))
    out_blob = DATA_BLOB()

    try:
        if not crypt32.CryptUnprotectData(ctypes.byref(in_blob), None,
                                          None, None, None, 0,
                                          ctypes.byref(out_blob)):
            return None
        result = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        kernel32.LocalFree(out_blob.pbData)
        return result
    except Exception:
        return None


def _aes_gcm_decrypt(key, nonce, ciphertext, tag):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM(key).decrypt(nonce, ciphertext + tag, None)
    except Exception:
        return None


def _get_local_state_key(profile_dir):
    local_state_path = os.path.join(os.path.dirname(profile_dir), "Local State")
    if not os.path.isfile(local_state_path):
        local_state_path = os.path.join(profile_dir, "Local State")
    if not os.path.isfile(local_state_path):
        return None
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        encrypted_key = base64.b64decode(data["os_crypt"]["encrypted_key"])
        if encrypted_key[:5] == b"DPAPI":
            encrypted_key = encrypted_key[5:]
        return _dpapi_unprotect(encrypted_key)
    except Exception:
        return None


def _decrypt_cookie_value(value, master_key):
    if not value:
        return ""
    if value[:3] in (b"v10", b"v11") and master_key:
        nonce = value[3:15]
        ciphertext = value[15:-16]
        tag = value[-16:]
        plain = _aes_gcm_decrypt(master_key, nonce, ciphertext, tag)
        if plain is not None:
            return plain.decode("utf-8", "replace")
        return None
    plain = _dpapi_unprotect(value)
    if plain is not None:
        return plain.decode("utf-8", "replace")
    return None


def _read_cookies_from_profile(profile_dir, host=FREEMODEL_HOST):
    cookies_db = os.path.join(profile_dir, "Default", "Network", "Cookies")
    if not os.path.isfile(cookies_db):
        cookies_db = os.path.join(profile_dir, "Network", "Cookies")
    if not os.path.isfile(cookies_db):
        cookies_db = os.path.join(profile_dir, "Cookies")
    if not os.path.isfile(cookies_db):
        return {}

    tmp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    try:
        shutil.copy2(cookies_db, tmp_db)
    except Exception:
        return {}

    master_key = _get_local_state_key(profile_dir)

    result = {}
    try:
        con = sqlite3.connect(tmp_db)
        cur = con.cursor()
        cur.execute(
            "SELECT name, value, encrypted_value, host_key "
            "FROM cookies WHERE host_key LIKE ?",
            (f"%{host}%",)
        )
        for name, value, encrypted_value, host_key in cur.fetchall():
            if value:
                result[name] = value
            elif encrypted_value:
                decrypted = _decrypt_cookie_value(encrypted_value, master_key)
                if decrypted is not None:
                    result[name] = decrypted
        con.close()
    except Exception:
        pass
    finally:
        try:
            os.unlink(tmp_db)
        except Exception:
            pass
    return result


def _cookies_to_string(jar):
    return "; ".join(f"{k}={v}" for k, v in jar.items() if v)


def _has_session_cookie(jar):
    keys = [k.lower() for k in jar.keys()]
    return any(
        any(s in k for s in ("session", "token", "auth", "csrf-token"))
        for k in keys
    )


# ─── Стратегия 1: системный браузер ──────────────────────────────────────────

def system_browser_login(on_status=None, timeout_sec=300):
    """Запускает Chrome/Edge с временным профилем, ждёт логина,
    извлекает cookie через DPAPI. Возвращает строку cookie или None.
    """
    exe, kind = _find_browser_path()
    if not exe:
        if on_status:
            on_status("error", "Chrome/Edge не найден")
        return None

    profile_dir = tempfile.mkdtemp(prefix="freemodel-login-")
    if on_status:
        on_status("info", f"Запуск {kind}...")

    cmd = [
        exe,
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate,OptimizationHints",
        f"--app={FREEMODEL_LOGIN}",
    ]

    try:
        proc = subprocess.Popen(cmd, creationflags=getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    except Exception as e:
        if on_status:
            on_status("error", f"Не удалось запустить браузер: {e}")
        _safe_rmtree(profile_dir)
        return None

    if on_status:
        on_status("info", "Войдите в аккаунт. Окно закроется автоматически.")

    start_time = time.time()
    cookie_str = None
    last_check = 0.0

    try:
        while time.time() - start_time < timeout_sec:
            if proc.poll() is not None:
                # Пользователь закрыл окно — пробуем последнее чтение
                break
            # Раз в 2 секунды проверяем cookies
            if time.time() - last_check >= 2.0:
                last_check = time.time()
                jar = _read_cookies_from_profile(profile_dir)
                if jar and _has_session_cookie(jar):
                    cookie_str = _cookies_to_string(jar)
                    if on_status:
                        on_status("info",
                                  f"Cookie получены ({len(jar)} шт.). "
                                  "Закрываем браузер...")
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    break
            time.sleep(0.3)
        else:
            if on_status:
                on_status("error", "Таймаут логина")
            try:
                proc.terminate()
            except Exception:
                pass

        # Финальное чтение (если пользователь закрыл окно сам)
        if not cookie_str:
            jar = _read_cookies_from_profile(profile_dir)
            if jar and _has_session_cookie(jar):
                cookie_str = _cookies_to_string(jar)
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        _safe_rmtree(profile_dir)

    if cookie_str:
        if on_status:
            on_status("success", "Успех")
        return cookie_str
    if on_status:
        on_status("error", "Cookie не получены")
    return None


def _safe_rmtree(path, retries=3):
    for _ in range(retries):
        try:
            shutil.rmtree(path, ignore_errors=False)
            return
        except Exception:
            time.sleep(0.5)
    shutil.rmtree(path, ignore_errors=True)


# ─── Стратегия 2: Playwright (если установлен) ───────────────────────────────

def playwright_login(email, password, on_status=None, headless=False):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        if on_status:
            on_status("error", "Playwright не установлен")
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            page.goto(FREEMODEL_LOGIN, timeout=30000)

            if email and password:
                try:
                    page.wait_for_selector(
                        'input[type="email"], input[name="email"]',
                        timeout=10000)
                    page.fill('input[type="email"], input[name="email"]', email)
                    page.fill(
                        'input[type="password"], input[name="password"]',
                        password)
                    page.click(
                        'button[type="submit"], '
                        'button:has-text("Sign In"), '
                        'button:has-text("Login")')
                    page.wait_for_timeout(5000)
                except Exception:
                    pass

            # Ждём появления session cookie
            for _ in range(60):
                cookies = context.cookies()
                jar = {c["name"]: c["value"] for c in cookies
                       if FREEMODEL_HOST in c.get("domain", "")}
                if _has_session_cookie(jar):
                    cookie_str = _cookies_to_string(jar)
                    browser.close()
                    if on_status:
                        on_status("success", "Успех (playwright)")
                    return cookie_str
                time.sleep(1)

            browser.close()
            if on_status:
                on_status("error", "Не удалось получить session cookie")
            return None
    except Exception as e:
        if on_status:
            on_status("error", f"Playwright ошибка: {e}")
        return None


# ─── Публичный API ────────────────────────────────────────────────────────────

def login(email="", password="", method="auto", on_status=None):
    """Главный вход. method: 'auto' | 'chrome' | 'playwright'."""
    method = (method or "auto").lower()

    if method in ("auto", "chrome", "system", "edge"):
        cookie = system_browser_login(on_status=on_status)
        if cookie:
            return cookie
        if method != "auto":
            return None

    if method in ("auto", "playwright"):
        if email and password:
            cookie = playwright_login(email, password, on_status=on_status)
            if cookie:
                return cookie

    return None
