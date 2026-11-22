"""Offline checks that m5_client sends and records the seed (no network)."""
import io
import json
import unittest
from unittest import mock

import m5_client


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _fake_urlopen(sent):
    def urlopen(req, timeout=None):
        sent.append(json.loads(req.data.decode()))
        body = {"choices": [{"message": {"content": "PONG"}, "finish_reason": "stop"}], "usage": {}}
        return _Resp(json.dumps(body).encode())
    return urlopen


class SeedTests(unittest.TestCase):
    def _chat(self, **kw):
        sent = []
        with mock.patch.object(m5_client, "_auth", return_value="Bearer x"), \
             mock.patch.object(m5_client.urllib.request, "urlopen", _fake_urlopen(sent)):
            r = m5_client.chat("m", [{"role": "user", "content": "hi"}], **kw)
        return r, sent[0]

    def test_no_seed_by_default(self):
        r, payload = self._chat()
        self.assertNotIn("seed", payload)
        self.assertEqual(r["sampling"], {"temperature": 0.2, "seed": None})

    def test_explicit_seed_is_sent_and_recorded(self):
        r, payload = self._chat(temperature=0.0, seed=7)
        self.assertEqual(payload["seed"], 7)
        self.assertEqual(r["sampling"], {"temperature": 0.0, "seed": 7})

    def test_rejects_bad_seed(self):
        for bad in (-1, 0xFFFFFFFF, True):
            with self.assertRaises(ValueError):
                m5_client.chat("m", [], seed=bad)

    def test_offset_seed_wraps_and_keeps_none(self):
        self.assertIsNone(m5_client.offset_seed(None, 3))
        self.assertEqual(m5_client.offset_seed(5, 2), 7)
        self.assertEqual(m5_client.offset_seed(m5_client.MAX_SEED, 1), 0)

    def test_seed_arg_validates(self):
        import argparse
        self.assertEqual(m5_client.seed_arg("3"), 3)
        for bad in ("-1", "x", str(0xFFFFFFFF)):
            with self.assertRaises(argparse.ArgumentTypeError):
                m5_client.seed_arg(bad)


if __name__ == "__main__":
    unittest.main()
