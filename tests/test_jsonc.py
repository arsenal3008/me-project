import os
import tempfile
import unittest

from agent_checker.jsonc import _strip_comments, read_jsonc, save_jsonc


class StripCommentsTests(unittest.TestCase):
    def test_line_comment(self):
        out = _strip_comments('a // comment\nb')
        self.assertEqual([l.rstrip() for l in out.split('\n')], ['a', 'b'])

    def test_block_comment(self):
        self.assertEqual(_strip_comments('a /* b\nc */ d'), 'a  d')

    def test_keeps_line_slashes_in_strings(self):
        # Парсер построчных // умеет учитывать кавычки.
        src = '"http://x"// rem'
        self.assertEqual(_strip_comments(src).rstrip(), '"http://x"')


class RoundTripTests(unittest.TestCase):
    def test_read_with_comments(self):
        with tempfile.NamedTemporaryFile('w', suffix='.jsonc', delete=False, encoding='utf-8') as f:
            f.write('{\n  // greeting\n  "k": 1, /* trail */\n  "v": "x"\n}\n')
            path = f.name
        try:
            data = read_jsonc(path)
            self.assertEqual(data, {'k': 1, 'v': 'x'})
        finally:
            os.unlink(path)

    def test_save_jsonc(self):
        with tempfile.NamedTemporaryFile('w', suffix='.jsonc', delete=False) as f:
            path = f.name
        try:
            save_jsonc(path, {'a': [1, 2]})
            self.assertEqual(read_jsonc(path), {'a': [1, 2]})
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
