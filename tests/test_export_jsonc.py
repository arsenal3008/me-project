"""Тестируем чистую функцию построения JSONC без Tk."""

import json
import unittest

from agent_checker.exporter import build_jsonc as _build_jsonc


class BuildJsoncTests(unittest.TestCase):
    def test_round_trip(self):
        providers = {'p': {'base_url': 'http://x'}}
        models = {'p': [('m1', 'Model One', 'opencode')]}
        keys = {'p': 'KEY'}
        out = _build_jsonc(['p'], providers, models, keys)
        data = json.loads(out)
        self.assertEqual(data['provider']['p']['name'], 'p')
        self.assertEqual(data['provider']['p']['options']['baseURL'], 'http://x')
        self.assertEqual(data['provider']['p']['options']['apiKey'], 'KEY')
        self.assertEqual(data['provider']['p']['models']['m1']['name'], 'Model One')

    def test_escapes_special_chars(self):
        # Это главный смысл рефакторинга: имя с кавычкой не должно ломать JSON
        providers = {'p': {'base_url': ''}}
        models = {'p': [('m"x', 'has "quote"', 'opencode')]}
        keys = {'p': ''}
        out = _build_jsonc(['p'], providers, models, keys)
        data = json.loads(out)  # Должно распарситься без ошибок
        self.assertIn('m"x', data['provider']['p']['models'])

    def test_skips_empty_base_url_and_key(self):
        providers = {'p': {'base_url': ''}}
        models = {'p': [('m', 'Model', 'opencode')]}
        keys = {'p': ''}
        out = _build_jsonc(['p'], providers, models, keys)
        data = json.loads(out)
        self.assertNotIn('baseURL', data['provider']['p']['options'])
        self.assertNotIn('apiKey', data['provider']['p']['options'])

    def test_provider_order_preserved(self):
        providers = {'a': {'base_url': ''}, 'b': {'base_url': ''}, 'c': {'base_url': ''}}
        models = {n: [] for n in 'abc'}
        keys = {n: '' for n in 'abc'}
        out = _build_jsonc(['b', 'c', 'a'], providers, models, keys)
        self.assertLess(out.index('"b"'), out.index('"c"'))
        self.assertLess(out.index('"c"'), out.index('"a"'))


if __name__ == '__main__':
    unittest.main()
