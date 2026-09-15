#!/usr/bin/env python3
"""Offline tests for local_explainer helpers — no Grok, no Kokoro."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD_PATH = ROOT / "scripts" / "local_explainer.py"


def load_mod():
    spec = importlib.util.spec_from_file_location("local_explainer", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class TestLocalExplainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load_mod()

    def test_slugify(self):
        self.assertEqual(self.m.slugify("The Line That Goes Both Ways"), "the-line-that-goes-both-ways")
        self.assertEqual(self.m.slugify("!!!"), "untitled")

    def test_extract_json_fence(self):
        obj = self.m.extract_json('```json\n{"vo": "Hello world.", "slides": []}\n```')
        self.assertEqual(obj["vo"], "Hello world.")

    def test_extract_json_missing_vo(self):
        with self.assertRaises(SystemExit):
            self.m.extract_json('{"title": "x"}')

    def test_synth_does_not_call_generate_from_tokens(self):
        src = Path(self.m.synth_kokoro.__code__.co_filename).read_text()
        # The module may mention the forbidden name in docs; the function body must not call it.
        import inspect

        body = inspect.getsource(self.m.synth_kokoro)
        self.assertNotIn("generate_from_tokens(", body)
        self.assertIn("pipeline(", body)

    def test_parse_script_only(self):
        ns = self.m.parse_args(["--script", "/tmp/x.json"])
        self.assertEqual(str(ns.script), "/tmp/x.json")
        self.assertEqual(ns.voice, "af_heart")
        self.assertEqual(ns.speed, 0.85)

    def test_writer_prompt_asks_json(self):
        self.assertIn("Return ONLY valid JSON", self.m.WRITER_SYSTEM)
        self.assertEqual(self.m.WRITER_MODEL, "grok-4.6")
        self.assertEqual(self.m.KOKORO_VOICE, "af_heart")


if __name__ == "__main__":
    unittest.main()
