from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


MAX_LIMIT = 1000


def _clamp_limit(limit: int, *, default: int = 200) -> int:
    if limit is None:
        return default
    if not isinstance(limit, int):
        raise ValueError("limit must be an integer")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    return min(limit, MAX_LIMIT)


def _collect(iterable: Iterable[dict[str, Any]], limit: int) -> tuple[list[dict[str, Any]], bool]:
    items: list[dict[str, Any]] = []
    truncated = False
    for idx, item in enumerate(iterable):
        if idx >= limit:
            truncated = True
            break
        items.append(item)
    return items, truncated


def _ok_items(items: list[dict[str, Any]], truncated: bool) -> dict[str, Any]:
    return {
        "status": "ok",
        "count": len(items),
        "truncated": truncated,
        "items": items,
    }


def _ok_data(data: Any) -> dict[str, Any]:
    return {
        "status": "ok",
        "data": data,
    }


@dataclass
class RucioService:
    client_factory: Callable[[], Any]

    def _client(self) -> Any:
        return self.client_factory()

    def ping(self) -> dict[str, Any]:
        return _ok_data(self._client().ping())

    def whoami(self) -> dict[str, Any]:
        return _ok_data(self._client().whoami())

    def list_dids(
        self,
        scope: str,
        name_pattern: str = "*",
        did_type: str = "collection",
        long: bool = False,
        recursive: bool = False,
        limit: int = 200,
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        filters = [{"name": name_pattern or "*"}]
        cursor = self._client().list_dids(
            scope=scope,
            filters=filters,
            did_type=did_type,
            long=long,
            recursive=recursive,
        )
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_did(self, scope: str, name: str, dynamic_depth: str | None = None) -> dict[str, Any]:
        data = self._client().get_did(scope=scope, name=name, dynamic_depth=dynamic_depth)
        return _ok_data(data)

    def list_replicas(
        self,
        dids: list[dict[str, str]],
        schemes: list[str] | None = None,
        ignore_availability: bool = True,
        all_states: bool = False,
        rse_expression: str | None = None,
        resolve_archives: bool = True,
        limit: int = 200,
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_replicas(
            dids=dids,
            schemes=schemes,
            ignore_availability=ignore_availability,
            all_states=all_states,
            rse_expression=rse_expression,
            resolve_archives=resolve_archives,
        )
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def list_rses(self, rse_expression: str | None = None, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_rses(rse_expression=rse_expression)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_rse(self, rse: str) -> dict[str, Any]:
        return _ok_data(self._client().get_rse(rse=rse))

    def list_requests(
        self,
        src_rse: str,
        dst_rse: str,
        request_states: list[str],
        limit: int = 200,
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_requests(
            src_rse=src_rse,
            dst_rse=dst_rse,
            request_states=request_states,
        )
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def list_requests_history(
        self,
        src_rse: str,
        dst_rse: str,
        request_states: list[str],
        offset: int = 0,
        limit: int = 200,
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_requests_history(
            src_rse=src_rse,
            dst_rse=dst_rse,
            request_states=request_states,
            offset=offset,
            limit=limit,
        )
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def list_replication_rules(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_replication_rules(filters=filters or {})
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_replication_rule(self, rule_id: str) -> dict[str, Any]:
        return _ok_data(self._client().get_replication_rule(rule_id=rule_id))
