import json
import os
import tempfile
import unittest

from agent_checker import providers


def _silent(*_a, **_kw):
    pass


class IsFreeTests(unittest.TestCase):
    def test_free_in_id(self):
        self.assertTrue(providers.is_free('foo:free', 'Foo'))

    def test_free_in_name(self):
        self.assertTrue(providers.is_free('foo', 'Foo (free)'))

    def test_not_free(self):
        self.assertFalse(providers.is_free('foo', 'Foo'))

    def test_handles_none(self):
        self.assertFalse(providers.is_free(None, None))


class CoerceKeysTests(unittest.TestCase):
    def test_only_apikey(self):
        keys, primary = providers._coerce_keys({'apiKey': 'X'})
        self.assertEqual(keys, ['X'])
        self.assertEqual(primary, 'X')

    def test_apikeys_list(self):
        keys, _ = providers._coerce_keys({'apiKeys': ['A', 'B']})
        self.assertEqual(keys, ['A', 'B'])

    def test_apikey_promoted_to_front(self):
        keys, _ = providers._coerce_keys({'apiKey': 'X', 'apiKeys': ['Y']})
        self.assertEqual(keys[0], 'X')
        self.assertIn('Y', keys)


class SaveProvidersTests(unittest.TestCase):
    def test_save_skips_models(self):
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            path = f.name
        try:
            data = {'p1': {'base_url': 'http://x', 'api_key': 'k',
                           'api_keys': ['k'], 'models': {'m1': {}}}}
            self.assertTrue(providers.save_providers(data, path))
            with open(path) as f:
                saved = json.load(f)
            self.assertNotIn('models', saved['p1'])
            self.assertEqual(saved['p1']['api_keys'], ['k'])
        finally:
            os.unlink(path)


class PropagateKeysTests(unittest.TestCase):
    def test_propagates_within_same_base_url(self):
        provs = {
            'a': {'base_url': 'http://x', 'api_keys': ['K1'], 'api_key': 'K1'},
            'b': {'base_url': 'http://x', 'api_keys': [], 'api_key': ''},
            'c': {'base_url': 'http://y', 'api_keys': [], 'api_key': ''},
        }
        providers.propagate_keys(provs)
        self.assertEqual(provs['b']['api_keys'], ['K1'])
        self.assertEqual(provs['c']['api_keys'], [])

    def test_no_source_keys_is_noop(self):
        provs = {'a': {'base_url': 'http://x', 'api_keys': [], 'api_key': ''}}
        providers.propagate_keys(provs)
        self.assertEqual(provs['a']['api_keys'], [])


class PurgeEmptyTests(unittest.TestCase):
    def test_drops_providers_without_models(self):
        provs = {'a': {'models': {}}, 'b': {'models': {'x': {}}}}
        providers.purge_empty(provs)
        self.assertNotIn('a', provs)
        self.assertIn('b', provs)


class LoadFromOpencodeTests(unittest.TestCase):
    def test_loads_models(self):
        cfg = {
            'provider': {
                'p1': {
                    'options': {'baseURL': 'http://x', 'apiKey': 'KKK'},
                    'models': {'m1': {'name': 'Model One'},
                               'free-m': {'name': 'Free Model'}},
                }
            }
        }
        with tempfile.NamedTemporaryFile('w', suffix='.jsonc', delete=False, encoding='utf-8') as f:
            json.dump(cfg, f)
            path = f.name
        # Patch existing_opencode_config to return our path
        from agent_checker import providers as P

        with tempfile.TemporaryDirectory() as _td:
            import unittest.mock as mock
            with mock.patch.object(P, 'existing_opencode_config', return_value=path):
                provs, mlist, used = P.load_from_opencode(log=_silent)
        try:
            self.assertEqual(used, path)
            self.assertIn('p1', provs)
            self.assertEqual(provs['p1']['base_url'], 'http://x')
            self.assertEqual(provs['p1']['api_keys'], ['KKK'])
            self.assertEqual(len(mlist), 2)
            free_entries = [m for m in mlist if m[4]]
            self.assertEqual(len(free_entries), 1)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
