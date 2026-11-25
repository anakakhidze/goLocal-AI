"""Each test gets isolated audit logs; no real provider or source is contacted."""
import socket

import pytest


@pytest.fixture(autouse=True)
def isolate_runtime(tmp_path, monkeypatch):
    monkeypatch.setenv("GOLOCAL_TOOL_LOG", str(tmp_path / "tools.jsonl"))
    monkeypatch.setenv("GOLOCAL_USAGE_LOG", str(tmp_path / "usage.jsonl"))
    monkeypatch.delenv("GOLOCAL_CALLER", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    original_connect = socket.socket.connect

    def blocked(sock, address):
        # Windows asyncio builds its internal socketpair over loopback.
        # Real sources and paid provider hosts remain unreachable in all tests.
        if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original_connect(sock, address)
        raise AssertionError("Offline tests must not connect to an external service")

    monkeypatch.setattr(socket.socket, "connect", blocked)
