import json
import os
import tempfile
import unittest

from agent_checker import settings


class SettingsTests(unittest.TestCase):
    def test_load_missing_returns_defaults(self):
        path = os.path.join(tempfile.gettempdir(), 'definitely-not-there.json')
        if os.path.isfile(path):
            os.unlink(path)
        out = settings.load(path)
        self.assertEqual(out, settings.DEFAULTS)

    def test_load_filters_unknown_keys(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump({'timeout': 99, 'evil': 'no'}, f)
            path = f.name
        try:
            out = settings.load(path)
            self.assertEqual(out['timeout'], 99)
            self.assertNotIn('evil', out)
        finally:
            os.unlink(path)

    def test_save_round_trip(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            path = f.name
        try:
            data = dict(settings.DEFAULTS, timeout=7, evil='ignore me')
            self.assertTrue(settings.save(data, path))
            with open(path, encoding='utf-8') as f:
                saved = json.load(f)
            self.assertEqual(saved['timeout'], 7)
            self.assertNotIn('evil', saved)
        finally:
            os.unlink(path)

    def test_load_bad_json_returns_defaults(self):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            f.write('{not json}')
            path = f.name
        try:
            self.assertEqual(settings.load(path), settings.DEFAULTS)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
