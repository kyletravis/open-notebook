"""Tests for resolve_api_client_timeout (api/client.py).

Covers env parsing, clamping to the 30-3600s range, invalid-value fallback,
and that the chat path's higher default (600s) is preserved when the env var
is unset.
"""

import pytest

from api.client import (
    _MAX_API_CLIENT_TIMEOUT,
    _MIN_API_CLIENT_TIMEOUT,
    resolve_api_client_timeout,
)


def test_unset_returns_default(monkeypatch):
    monkeypatch.delenv("API_CLIENT_TIMEOUT", raising=False)
    assert resolve_api_client_timeout() == 300.0


def test_unset_preserves_chat_default(monkeypatch):
    # The chat path passes default=600.0 to keep its historical timeout.
    monkeypatch.delenv("API_CLIENT_TIMEOUT", raising=False)
    assert resolve_api_client_timeout(default=600.0) == 600.0


def test_valid_value_is_used(monkeypatch):
    monkeypatch.setenv("API_CLIENT_TIMEOUT", "900")
    assert resolve_api_client_timeout() == 900.0
    # An explicit env value overrides any caller default.
    assert resolve_api_client_timeout(default=600.0) == 900.0


def test_too_low_clamps_to_minimum(monkeypatch):
    monkeypatch.setenv("API_CLIENT_TIMEOUT", "5")
    assert resolve_api_client_timeout() == _MIN_API_CLIENT_TIMEOUT


def test_too_high_clamps_to_maximum(monkeypatch):
    monkeypatch.setenv("API_CLIENT_TIMEOUT", "100000")
    assert resolve_api_client_timeout() == _MAX_API_CLIENT_TIMEOUT


def test_invalid_value_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("API_CLIENT_TIMEOUT", "not-a-number")
    assert resolve_api_client_timeout(default=600.0) == 600.0


@pytest.mark.parametrize(
    "value,expected",
    [
        ("30", 30.0),
        ("3600", 3600.0),
        ("450.5", 450.5),
    ],
)
def test_boundary_and_float_values(monkeypatch, value, expected):
    monkeypatch.setenv("API_CLIENT_TIMEOUT", value)
    assert resolve_api_client_timeout() == expected
