# -*- coding: utf-8 -*-
# PjOrion decrypted-code dumper v4 (Python 2.7 / World of Tanks / BigWorld).
# GAME-SAFE: no sys.settrace, no marshal/eval hooks.
#
# v4 goals:
#   * ALWAYS create the output files immediately at import (synchronous), so you can
#     find them even if background threads / clean-exit hooks don't fire.
#   * Print the ABSOLUTE output path loudly to the log so you know where to look.
#   * Keep updating via a background poller (in case the mod loads later).
#   * The report lists EVERY loaded module so we can identify the real module name.
#
# USE: put next to the mod, `import pjorion_dump4` anywhere. Play one battle.
# Files appear at the path printed in the log (also next to this script). Send BOTH:
#     pjorion_decrypted.marshal
#     pjorion_dump_report.txt

import sys, types, marshal, os, gc

HINTS = ('contourlook', 'mod_zj', 'zj_', 'contour')   # matched case-INSENSITIVELY

def _dir():
    cands = []
    try: cands.append(os.path.dirname(os.path.abspath(__file__)))
    except Exception: pass
    try: cands.append(os.getcwd())
    except Exception: pass
    cands.append('.')
    for d in cands:
        try:
            t = os.path.join(d, '_pjw_test.tmp')
            f = open(t, 'wb'); f.write(b'x'); f.close(); os.remove(t)
            return d
        except Exception:
            continue
    return '.'

_DIR = _dir()
_OUT = os.path.join(_DIR, 'pjorion_decrypted.marshal')
_REP = os.path.join(_DIR, 'pjorion_dump_report.txt')

def _hint(s):
    if not s: return False
    try: s = s.lower()
    except Exception: return False
    for h in HINTS:
        if h in s: return True
    return False

def _add(co, codes):
    try:
        if isinstance(co, types.CodeType) and id(co) not in codes:
            codes[id(co)] = co
            for k in co.co_consts:
                if isinstance(k, types.CodeType):
                    _add(k, codes)
    except Exception:
        pass

def _target_modules():
    out = []
    for name, m in list(sys.modules.items()):
        if m is None: continue
        try: f = getattr(m, '__file__', '') or ''
        except Exception: f = ''
        if _hint(name) or _hint(f):
            out.append((name, m))
    return out

def collect():
    codes = {}
    mods = _target_modules()
    moddicts = [getattr(m, '__dict__', None) for _, m in mods]
    moddicts = [d for d in moddicts if d is not None]

    def walk(d, depth=0, seen=None):
        if seen is None: seen = set()
        if depth > 6: return
        for v in list(d.values()):
            try:
                if isinstance(v, types.FunctionType):
                    _add(v.func_code, codes)
                elif isinstance(v, types.MethodType):
                    _add(v.im_func.func_code, codes)
                elif isinstance(v, (staticmethod, classmethod)):
                    fn = getattr(v, '__func__', None)
                    if fn is not None and hasattr(fn, 'func_code'):
                        _add(fn.func_code, codes)
                elif isinstance(v, type) and id(v) not in seen:
                    seen.add(id(v)); walk(v.__dict__, depth+1, seen)
            except Exception:
                pass
    for d in moddicts:
        walk(d)

    if moddicts:
        try:
            for obj in gc.get_objects():
                try:
                    if isinstance(obj, types.FunctionType):
                        g = obj.func_globals
                        for d in moddicts:
                            if g is d:
                                _add(obj.func_code, codes); break
                except Exception:
                    pass
        except Exception:
            pass
    return list(codes.values()), [n for n, _ in mods]

def write_report():
    try:
        lines = ['=== ALL loaded modules (name -> __file__) ===']
        for name in sorted(sys.modules.keys()):
            m = sys.modules.get(name)
            if m is None: continue
            try: f = getattr(m, '__file__', '') or ''
            except Exception: f = ''
            lines.append('%-50s %s' % (name, f))
        rep = open(_REP, 'wb')
        rep.write(('\n'.join(lines)).encode('utf-8', 'replace')); rep.write(b'\n')
        rep.close()
    except Exception:
        pass

def dump():
    objs, names = collect()
    try:
        f = open(_OUT, 'wb'); marshal.dump(objs, f); f.close()
        sys.stderr.write('[pjorion_dump4] OUT=%s modules=%r code_objects=%d\n' % (_OUT, names, len(objs)))
    except Exception as e:
        sys.stderr.write('[pjorion_dump4] dump failed: %s\n' % e)
    write_report()
    return len(objs)

# 1) synchronous dump RIGHT NOW so a file always exists + path is logged
try:
    dump()
except Exception as e:
    sys.stderr.write('[pjorion_dump4] init dump error: %s\n' % e)

# 2) background poller to keep updating once the mod loads (best effort)
try:
    import threading, time
    def _poll():
        for _ in range(300):
            try: dump()
            except Exception: pass
            time.sleep(2)
    t = threading.Thread(target=_poll); t.setDaemon(True); t.start()
except Exception:
    pass

# 3) dump on clean exit too
try:
    import atexit
    atexit.register(dump)
except Exception:
    pass
