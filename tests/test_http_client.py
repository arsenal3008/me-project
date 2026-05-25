import json
import unittest
from unittest import mock

from agent_checker import http_client as hc


def _silent(*_a, **_kw):
    pass


class CacheTests(unittest.TestCase):
    def setUp(self):
        hc.invalidate_cache()

    def test_invalidate_all(self):
        hc.VALID_KEYS_CACHE['http://a'] = ['k']
        hc.invalidate_cache()
        self.assertEqual(hc.VALID_KEYS_CACHE, {})

    def test_invalidate_one(self):
        hc.VALID_KEYS_CACHE['http://a'] = ['k']
        hc.VALID_KEYS_CACHE['http://b'] = ['k2']
        hc.invalidate_cache('http://a')
        self.assertNotIn('http://a', hc.VALID_KEYS_CACHE)
        self.assertIn('http://b', hc.VALID_KEYS_CACHE)


class CheckServerOnlineTests(unittest.TestCase):
    def test_uses_443_for_https(self):
        captured = {}

        def fake_create(addr, timeout):
            captured['addr'] = addr
            raise OSError('skip')

        with mock.patch('socket.create_connection', side_effect=fake_create):
            self.assertFalse(hc.check_server_online('https://api.example.com/v1'))
        self.assertEqual(captured['addr'][1], 443)

    def test_uses_80_for_http(self):
        captured = {}

        def fake_create(addr, timeout):
            captured['addr'] = addr

            class S:
                def close(self_inner):
                    pass

            return S()

        with mock.patch('socket.create_connection', side_effect=fake_create):
            self.assertTrue(hc.check_server_online('http://localhost/'))
        self.assertEqual(captured['addr'][1], 80)

    def test_uses_explicit_port(self):
        captured = {}

        def fake_create(addr, timeout):
            captured['addr'] = addr

            class S:
                def close(self_inner):
                    pass

            return S()

        with mock.patch('socket.create_connection', side_effect=fake_create):
            hc.check_server_online('http://localhost:11434')
        self.assertEqual(captured['addr'][1], 11434)


class ValidateKeysTests(unittest.TestCase):
    def setUp(self):
        hc.invalidate_cache()

    def test_uses_provider_first_model(self):
        captured = {}

        def fake_post(url, body, headers, timeout=10):
            captured['body'] = body
            return 200, '{"choices":[{"message":{"content":"ok"}}]}'

        with mock.patch.object(hc, 'http_post', side_effect=fake_post):
            keys = hc.validate_keys('http://x', ['K1'],
                                    provider_models={'real-model': {}},
                                    log=_silent)
        self.assertEqual(keys, ['K1'])
        self.assertEqual(captured['body']['model'], 'real-model')

    def test_falls_back_to_default_model(self):
        captured = {}

        def fake_post(url, body, headers, timeout=10):
            captured['body'] = body
            return 200, '{}'

        with mock.patch.object(hc, 'http_post', side_effect=fake_post):
            hc.validate_keys('http://x', ['K1'], log=_silent)
        self.assertEqual(captured['body']['model'], 'gpt-4o-mini')

    def test_skips_invalid_key(self):
        responses = iter([(401, json.dumps({'error': {'message': 'bad key'}})),
                           (200, '{}')])

        def fake_post(url, body, headers, timeout=10):
            return next(responses)

        with mock.patch.object(hc, 'http_post', side_effect=fake_post):
            keys = hc.validate_keys('http://x', ['BAD', 'GOOD'],
                                    provider_models={'m': {}}, log=_silent)
        self.assertEqual(keys, ['GOOD'])

    def test_model_not_found_still_valid_key(self):
        def fake_post(url, body, headers, timeout=10):
            return 401, json.dumps({'error': {'message': 'model not found'}})

        with mock.patch.object(hc, 'http_post', side_effect=fake_post):
            keys = hc.validate_keys('http://x', ['K'],
                                    provider_models={'m': {}}, log=_silent)
        self.assertEqual(keys, ['K'])

    def test_429_treated_as_valid(self):
        def fake_post(url, body, headers, timeout=10):
            return 429, ''

        with mock.patch.object(hc, 'http_post', side_effect=fake_post):
            keys = hc.validate_keys('http://x', ['K'],
                                    provider_models={'m': {}}, log=_silent)
        self.assertEqual(keys, ['K'])

    def test_no_keys(self):
        keys = hc.validate_keys('http://x', [], log=_silent)
        self.assertEqual(keys, [])


class TestModelTests(unittest.TestCase):
    def setUp(self):
        hc.invalidate_cache()

    def test_no_api_keys(self):
        ok, msg, _ = hc.test_model('http://x', [], 'm', log=_silent)
        self.assertFalse(ok)
        self.assertIn('Нет', msg)

    def test_success(self):
        # First call is validate_keys, second is the actual test
        responses = iter([
            (200, '{}'),
            (200, json.dumps({'choices': [{'message': {'content': 'ok'}}]})),
        ])

        def fake_post(url, body, headers, timeout=20):
            return next(responses)

        with mock.patch.object(hc, 'http_post', side_effect=fake_post):
            ok, msg, _ = hc.test_model('http://x', ['K'], 'm', timeout=5, retries=0,
                                       provider_models={'m': {}}, log=_silent)
        self.assertTrue(ok)
        self.assertEqual(msg, 'ok')


if __name__ == '__main__':
    unittest.main()
