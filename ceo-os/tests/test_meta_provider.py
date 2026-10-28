"""Tests for the Meta Model API provider — all offline, HTTP stubbed."""
from __future__ import annotations

import io
import json
import os
import sys
import urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ceo_os.meta_provider import MetaProvider, MissingKeyError, build_provider


def _fake_urlopen(payload: dict):
    class Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return json.dumps(payload).encode()
    return Resp()


def test_missing_key_raises():
    env = {k: v for k, v in os.environ.items() if k not in ("MODEL_API_KEY", "META_MODEL_API_KEY")}
    old = dict(os.environ)
    os.environ.clear(); os.environ.update(env)
    try:
        try:
            MetaProvider(api_key=None)
            raise AssertionError("should have raised")
        except MissingKeyError as e:
            assert "MODEL_API_KEY" in str(e)
    finally:
        os.environ.clear(); os.environ.update(old)
    print("ok: missing key raises MissingKeyError")


def test_complete_parses_openai_format(monkeypatch=None):
    import urllib.request
    payload = {
        "choices": [{"message": {"content": "  hello worker  "}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 120, "completion_tokens": 8},
    }
    orig = urllib.request.urlopen
    urllib.request.urlopen = lambda req, timeout=None: _fake_urlopen(payload)
    try:
        p = MetaProvider(api_key="test-key", base_url="https://example.invalid")
        out = p.complete("do the thing", max_tokens=50)
        assert out == "hello worker", out
        h = p.health()
        assert h["calls"] == 1 and h["prompt_tokens"] == 120 and h["completion_tokens"] == 8
        assert h["model"] == "muse-spark-1.3"
    finally:
        urllib.request.urlopen = orig
    print("ok: complete() parses OpenAI-compatible response + tracks tokens")


def test_api_error_raises():
    import urllib.request
    payload = {"error": {"message": "bad key", "type": "auth"}}
    orig = urllib.request.urlopen
    urllib.request.urlopen = lambda req, timeout=None: _fake_urlopen(payload)
    try:
        p = MetaProvider(api_key="bad", base_url="https://example.invalid", max_retries=1)
        try:
            p.complete("x")
            raise AssertionError("should have raised")
        except RuntimeError as e:
            assert "bad key" in str(e)
    finally:
        urllib.request.urlopen = orig
    print("ok: API error payload raises RuntimeError")


def test_retry_then_give_up():
    import urllib.request
    calls = {"n": 0}
    def boom(req, timeout=None):
        calls["n"] += 1
        raise urllib.error.URLError("down")
    orig = urllib.request.urlopen
    urllib.request.urlopen = boom
    try:
        p = MetaProvider(api_key="k", base_url="https://example.invalid", max_retries=2)
        try:
            p.complete("x")
            raise AssertionError("should have raised")
        except RuntimeError:
            pass
        assert calls["n"] == 2, calls
    finally:
        urllib.request.urlopen = orig
    print("ok: retries exhausted -> RuntimeError (no silent failure)")


def test_build_provider_falls_back_loud():
    env = {k: v for k, v in os.environ.items() if k not in ("MODEL_API_KEY", "META_MODEL_API_KEY")}
    old = dict(os.environ)
    os.environ.clear(); os.environ.update(env)
    try:
        buf = io.StringIO()
        old_out = sys.stdout; sys.stdout = buf
        try:
            prov = build_provider()
        finally:
            sys.stdout = old_out
        assert prov.name == "mock"
        assert "MOCK" in buf.getvalue().upper()
    finally:
        os.environ.clear(); os.environ.update(old)
    print("ok: build_provider() falls back to mock LOUDLY without a key")


def test_bad_reasoning_effort_rejected():
    try:
        MetaProvider(api_key="k", reasoning_effort="none")
        raise AssertionError("should have raised")
    except ValueError:
        pass
    print("ok: reasoning_effort='none' rejected (Muse Spark returns 400)")


if __name__ == "__main__":
    test_missing_key_raises()
    test_complete_parses_openai_format()
    test_api_error_raises()
    test_retry_then_give_up()
    test_build_provider_falls_back_loud()
    test_bad_reasoning_effort_rejected()
    print("\nAll 6 provider tests passed.")
