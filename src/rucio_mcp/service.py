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

    # ── DID content & metadata ────────────────────────────────────

    def list_content(self, scope: str, name: str, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_content(scope=scope, name=name)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def list_parent_dids(self, scope: str, name: str, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_parent_dids(scope=scope, name=name)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_metadata(self, scope: str, name: str, plugin: str = "DID_COLUMN") -> dict[str, Any]:
        return _ok_data(self._client().get_metadata(scope=scope, name=name, plugin=plugin))

    def list_dataset_replicas(
        self, scope: str, name: str, deep: bool = False, limit: int = 200
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_dataset_replicas(scope=scope, name=name, deep=deep)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def list_did_rules(self, scope: str, name: str, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_did_rules(scope=scope, name=name)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    # ── RSE operational data ──────────────────────────────────────

    def get_rse_usage(
        self, rse: str, filters: dict[str, Any] | None = None, limit: int = 200
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().get_rse_usage(rse=rse, filters=filters)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_rse_limits(self, rse: str, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().get_rse_limits(rse=rse)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def list_rse_attributes(self, rse: str) -> dict[str, Any]:
        return _ok_data(self._client().list_rse_attributes(rse=rse))

    def get_rse_protocols(self, rse: str) -> dict[str, Any]:
        return _ok_data(self._client().get_protocols(rse=rse))

    def get_distance(self, source: str, destination: str) -> dict[str, Any]:
        return _ok_data(self._client().get_distance(source=source, destination=destination))

    def list_transfer_limits(self, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_transfer_limits()
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    # ── Accounts & quotas ─────────────────────────────────────────

    def list_accounts(
        self,
        account_type: str | None = None,
        identity: str | None = None,
        filters: dict[str, Any] | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_accounts(
            account_type=account_type, identity=identity, filters=filters
        )
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_account(self, account: str) -> dict[str, Any]:
        return _ok_data(self._client().get_account(account=account))

    def get_local_account_usage(
        self, account: str, rse: str | None = None, limit: int = 200
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().get_local_account_usage(account=account, rse=rse)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_local_account_limits(self, account: str) -> dict[str, Any]:
        return _ok_data(self._client().get_local_account_limits(account=account))

    def list_account_rules(self, account: str, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_account_rules(account=account)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    # ── Subscriptions ─────────────────────────────────────────────

    def list_subscriptions(
        self,
        name: str | None = None,
        account: str | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_subscriptions(name=name, account=account)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def list_subscription_rules(
        self, account: str, name: str, limit: int = 200
    ) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().list_subscription_rules(account=account, name=name)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    # ── Locks ─────────────────────────────────────────────────────

    def get_dataset_locks(self, scope: str, name: str, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().get_dataset_locks(scope=scope, name=name)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    def get_dataset_locks_by_rse(self, rse: str, limit: int = 200) -> dict[str, Any]:
        limit = _clamp_limit(limit)
        cursor = self._client().get_dataset_locks_by_rse(rse=rse)
        items, truncated = _collect(cursor, limit)
        return _ok_items(items, truncated)

    # ── Scopes ────────────────────────────────────────────────────

    def list_scopes(self) -> dict[str, Any]:
        return _ok_data(self._client().list_scopes())

    def list_scopes_for_account(self, account: str) -> dict[str, Any]:
        return _ok_data(self._client().list_scopes_for_account(account=account))
