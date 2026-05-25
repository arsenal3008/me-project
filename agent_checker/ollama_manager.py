"""Авто-запуск Ollama. Кросс-платформенно."""

import os
import shutil
import subprocess
import sys
import time

from .http_client import check_server_online

DEFAULT_URL = 'http://localhost:11434'


def find_binary():
    """Найти исполняемый ``ollama`` в PATH, ``$OLLAMA_BIN`` или системных каталогах."""
    env = os.environ.get('OLLAMA_BIN')
    if env and os.path.isfile(env):
        return env
    which = shutil.which('ollama')
    if which:
        return which
    if sys.platform == 'win32':
        for c in (
            os.path.expandvars(r'%LOCALAPPDATA%\Programs\Ollama\ollama.exe'),
            os.path.expandvars(r'%ProgramFiles%\Ollama\ollama.exe'),
        ):
            if os.path.isfile(c):
                return c
    if sys.platform == 'darwin':
        for c in ('/Applications/Ollama.app/Contents/Resources/ollama', '/usr/local/bin/ollama'):
            if os.path.isfile(c):
                return c
    return None


def is_running(url=DEFAULT_URL):
    return check_server_online(url)


def ensure_running(url=DEFAULT_URL, log=print, wait_seconds=30):
    """Запустить ``ollama serve``, если не запущен. Возвращает ``True``, если поднят."""
    if is_running(url):
        log('Ollama уже запущен')
        return True
    binary = find_binary()
    if not binary:
        log('Ollama не найден (установите ollama или задайте переменную OLLAMA_BIN)')
        return False
    log('Запуск Ollama: %s' % binary)
    kwargs = {'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
    if sys.platform == 'win32':
        CREATE_NO_WINDOW = 0x08000000
        flags = CREATE_NO_WINDOW
        breakaway = getattr(subprocess, 'CREATE_BREAKAWAY_FROM_JOB', None)
        if breakaway is not None:
            flags |= breakaway
        kwargs['creationflags'] = flags
    else:
        kwargs['start_new_session'] = True
    try:
        subprocess.Popen([binary, 'serve'], **kwargs)
    except Exception as e:
        log('Ошибка запуска Ollama: %s' % e)
        return False
    for _ in range(wait_seconds):
        time.sleep(1)
        if is_running(url):
            log('Ollama успешно запущен')
            return True
    log('Ollama не удалось запустить (таймаут)')
    return False


def hide_windows():
    """Скрыть/свернуть окна Ollama. No-op кроме Windows."""
    if sys.platform != 'win32':
        return
    try:
        _hide_windows_impl()
    except Exception:
        pass


def _hide_windows_impl():
    import ctypes
    import threading

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    GetWindowText = user32.GetWindowTextW
    GetWindowTextLength = user32.GetWindowTextLengthW
    EnumWindows = user32.EnumWindows
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010

    def _hide_or_minimize(hwnd, pid):
        proc = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if proc:
            buf = ctypes.create_unicode_buffer(260)
            psapi.GetModuleBaseNameW(proc, None, buf, 260)
            kernel32.CloseHandle(proc)
            pname = buf.value.lower()
        else:
            pname = ''
        if pname.endswith('ollama.exe'):
            user32.ShowWindowAsync(hwnd, 0)  # SW_HIDE
        else:
            user32.ShowWindowAsync(hwnd, 6)  # SW_MINIMIZE

    def _find_and_hide():
        found = []

        def callback(hwnd, _):
            length = GetWindowTextLength(hwnd) + 1
            buf = ctypes.create_unicode_buffer(length)
            GetWindowText(hwnd, buf, length)
            title = buf.value.lower()
            if 'ollama' in title:
                pid = ctypes.c_ulong()
                GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                found.append((hwnd, pid.value))
            return True

        EnumWindows(EnumWindowsProc(callback), 0)
        for hwnd, pid in found:
            _hide_or_minimize(hwnd, pid)

    _find_and_hide()

    def _watcher():
        for _ in range(20):
            time.sleep(0.5)
            _find_and_hide()

    threading.Thread(target=_watcher, daemon=True).start()
