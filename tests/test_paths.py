import os
import tempfile
import unittest
from unittest import mock

from agent_checker import paths


class PathsTests(unittest.TestCase):
    def test_constants(self):
        self.assertTrue(os.path.isabs(paths.REPO_DIR))
        self.assertTrue(paths.PROVIDERS_JSON.endswith('providers.json'))
        self.assertEqual(paths.SCRIPT_DIR, paths.REPO_DIR)

    def test_candidates_include_env(self):
        with mock.patch.dict(os.environ, {'OPENCODE_CONFIG': '/custom/path.jsonc'}, clear=False):
            cands = paths.opencode_config_candidates()
        self.assertIn('/custom/path.jsonc', cands)

    def test_existing_returns_none_when_missing(self):
        with mock.patch.object(paths, 'opencode_config_candidates',
                               return_value=['/nonexistent/x']):
            self.assertIsNone(paths.existing_opencode_config())

    def test_existing_returns_first_match(self):
        with tempfile.NamedTemporaryFile('w', suffix='.jsonc', delete=False) as f:
            f.write('{}')
            real = f.name
        try:
            with mock.patch.object(paths, 'opencode_config_candidates',
                                   return_value=['/nope', real]):
                self.assertEqual(paths.existing_opencode_config(), real)
        finally:
            os.unlink(real)


if __name__ == '__main__':
    unittest.main()
