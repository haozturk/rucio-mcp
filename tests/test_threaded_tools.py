from __future__ import annotations

import inspect
import threading
import time

import anyio

from rucio_mcp import server


def test_tools_are_async_and_keep_their_signature() -> None:
    fn = server.rucio_list_dids
    assert inspect.iscoroutinefunction(fn)
    params = list(inspect.signature(fn).parameters)
    assert params[:3] == ["scope", "name_pattern", "did_type"]
    assert fn.__doc__


def test_tool_schema_unchanged_by_wrapper() -> None:
    tools = {t.name: t for t in anyio.run(server.mcp.list_tools)}
    props = tools["rucio_list_dids"].inputSchema["properties"]
    assert {"scope", "name_pattern", "did_type", "long", "recursive"} <= set(props)
    assert tools["rucio_list_dids"].inputSchema["required"] == ["scope"]


def test_slow_calls_run_in_parallel(monkeypatch) -> None:
    started = threading.Barrier(2, timeout=5)

    def slow_ping() -> dict[str, str]:
        started.wait()  # both calls must be inside a thread at the same time
        time.sleep(0.2)
        return {"thread": threading.current_thread().name}

    monkeypatch.setattr(server.service, "ping", slow_ping)
    results: list[dict[str, str]] = []

    async def main() -> None:
        async with anyio.create_task_group() as tg:
            for _ in range(2):
                tg.start_soon(lambda: _call(results))

    async def _call(out: list[dict[str, str]]) -> None:
        out.append(await server.rucio_ping())

    anyio.run(main)
    assert len(results) == 2
    assert all(r["thread"] != threading.main_thread().name for r in results)
