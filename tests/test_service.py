from __future__ import annotations

from typing import Any

from rucio_mcp.service import RucioService


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def ping(self) -> dict[str, Any]:
        self.calls.append(("ping", {}))
        return {"version": "test"}

    def whoami(self) -> dict[str, Any]:
        self.calls.append(("whoami", {}))
        return {"account": "test-account"}

    def list_dids(self, **kwargs):
        self.calls.append(("list_dids", kwargs))
        return iter([{"scope": "s", "name": "n1"}, {"scope": "s", "name": "n2"}])

    def get_did(self, **kwargs):
        self.calls.append(("get_did", kwargs))
        return {"scope": kwargs["scope"], "name": kwargs["name"]}

    def list_replicas(self, **kwargs):
        self.calls.append(("list_replicas", kwargs))
        return iter([{"scope": "s", "name": "n1"}])

    def list_rses(self, **kwargs):
        self.calls.append(("list_rses", kwargs))
        return iter([{"rse": "T2_TEST"}])

    def get_rse(self, **kwargs):
        self.calls.append(("get_rse", kwargs))
        return {"rse": kwargs["rse"]}

    def list_requests(self, **kwargs):
        self.calls.append(("list_requests", kwargs))
        return iter([{"id": "req-1"}])

    def list_requests_history(self, **kwargs):
        self.calls.append(("list_requests_history", kwargs))
        return iter([{"id": "req-h-1"}])

    def list_replication_rules(self, **kwargs):
        self.calls.append(("list_replication_rules", kwargs))
        return iter([{"id": "rule-1"}])

    def get_replication_rule(self, **kwargs):
        self.calls.append(("get_replication_rule", kwargs))
        return {"id": kwargs["rule_id"]}


def test_ping_and_whoami() -> None:
    client = FakeClient()
    svc = RucioService(client_factory=lambda: client)

    assert svc.ping()["data"]["version"] == "test"
    assert svc.whoami()["data"]["account"] == "test-account"


def test_list_dids() -> None:
    client = FakeClient()
    svc = RucioService(client_factory=lambda: client)

    out = svc.list_dids(scope="cms", name_pattern="A*", limit=1)

    assert out["count"] == 1
    assert out["truncated"] is True
    method, kwargs = client.calls[-1]
    assert method == "list_dids"
    assert kwargs["scope"] == "cms"
    assert kwargs["filters"] == [{"name": "A*"}]


def test_get_did() -> None:
    client = FakeClient()
    svc = RucioService(client_factory=lambda: client)

    out = svc.get_did(scope="cms", name="dataset")

    assert out["data"]["name"] == "dataset"


def test_list_replicas() -> None:
    client = FakeClient()
    svc = RucioService(client_factory=lambda: client)

    out = svc.list_replicas(dids=[{"scope": "cms", "name": "f1"}], limit=10)

    assert out["count"] == 1
    method, kwargs = client.calls[-1]
    assert method == "list_replicas"
    assert kwargs["dids"] == [{"scope": "cms", "name": "f1"}]


def test_rse_methods() -> None:
    client = FakeClient()
    svc = RucioService(client_factory=lambda: client)

    out1 = svc.list_rses(limit=5)
    out2 = svc.get_rse(rse="T2_TEST")

    assert out1["count"] == 1
    assert out2["data"]["rse"] == "T2_TEST"


def test_request_methods() -> None:
    client = FakeClient()
    svc = RucioService(client_factory=lambda: client)

    out1 = svc.list_requests(src_rse="SRC", dst_rse="DST", request_states=["SUBMITTED"], limit=5)
    out2 = svc.list_requests_history(src_rse="SRC", dst_rse="DST", request_states=["DONE"], offset=0, limit=5)

    assert out1["count"] == 1
    assert out2["count"] == 1


def test_rule_methods() -> None:
    client = FakeClient()
    svc = RucioService(client_factory=lambda: client)

    out1 = svc.list_replication_rules(filters={"scope": "cms"}, limit=5)
    out2 = svc.get_replication_rule(rule_id="rule-1")

    assert out1["count"] == 1
    assert out2["data"]["id"] == "rule-1"
