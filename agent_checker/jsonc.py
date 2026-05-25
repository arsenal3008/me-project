"""JSONC: JSON с поддержкой ``//`` и ``/* */`` комментариев."""

import json
import re


def _strip_comments(text):
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)
    out_lines = []
    for line in text.split('\n'):
        in_str = False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '"' and (i == 0 or line[i - 1] != '\\'):
                in_str = not in_str
            elif not in_str and ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                line = line[:i]
                break
            i += 1
        out_lines.append(line)
    return '\n'.join(out_lines)


def read_jsonc(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    return json.loads(_strip_comments(text))


def save_jsonc(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
