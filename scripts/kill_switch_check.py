"""Several Reach servers must share one kill switch. This starts real servers over
stdio and presses a real hotkey, on its own key (Ctrl+Alt+F11) and its own event, so
it neither collides with a running Reach nor kills it.

    python scripts/kill_switch_check.py

It checks five things: two servers start side by side; one press stops both; when
the server holding the hotkey exits, the other takes it over; a server started after
a press is not stopped by it; and a server refuses to start when the hotkey is held
by something that is not Reach.
"""

import asyncio
import ctypes
import subprocess
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from reach import win32

KEY = 0x7A  # F11
SERVER = (
    "from reach import server; from reach.overlay import Overlay; "
    f"server.overlay = Overlay(server.guard.killed.set, key={KEY}, "
    "shared='Local\\\\ReachKillSwitchCheck'); server.main()"
)
PARAMS = StdioServerParameters(command=sys.executable, args=["-c", SERVER])


async def stopped(session: ClientSession) -> bool:
    result = await session.call_tool("windows", {})
    return "kill switch" in str(result.content[0])


async def press() -> None:
    win32.send_keys([0x11, 0x12, KEY])
    await asyncio.sleep(1.0)


async def both_stop() -> None:
    async with (
        stdio_client(PARAMS) as (r1, w1),
        ClientSession(r1, w1) as first,
        stdio_client(PARAMS) as (r2, w2),
        ClientSession(r2, w2) as second,
    ):
        await first.initialize()
        await second.initialize()
        assert not await stopped(first), "the first server did not start clean"
        assert not await stopped(second), "the second server did not start clean"
        print("two servers run side by side")
        await press()
        assert await stopped(first), "the first server ignored the kill switch"
        assert await stopped(second), "the second server ignored the kill switch"
        print("one press stopped both")


async def takeover() -> None:
    async with stdio_client(PARAMS) as (r2, w2), ClientSession(r2, w2) as survivor:
        async with stdio_client(PARAMS) as (r1, w1), ClientSession(r1, w1) as holder:
            await holder.initialize()  # started first, so it holds the hotkey
            await asyncio.sleep(0.5)
            await survivor.initialize()
            assert not await stopped(survivor)
        await asyncio.sleep(1.5)  # the holder has exited; the survivor takes the hotkey
        await press()
        assert await stopped(survivor), "the survivor never took the hotkey over"
        print("the survivor took the hotkey over and stopped")
        # A stopped server is still running. One started now must not inherit its fate.
        async with stdio_client(PARAMS) as (r3, w3), ClientSession(r3, w3) as late:
            await late.initialize()
            await asyncio.sleep(1.0)
            assert not await stopped(late), "a server started after a press was stopped by it"
            print("a server started after the press runs")


def foreign_holder() -> None:
    user32 = ctypes.WinDLL("user32")
    assert user32.RegisterHotKey(None, 1, 0x0001 | 0x0002 | 0x4000, KEY), "the key is in use"
    lone = subprocess.run(
        [sys.executable, "-c", SERVER],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert lone.returncode != 0, "the server started without a kill switch"
    assert "taken by another program" in lone.stderr, lone.stderr
    print("a server refuses to start when the hotkey is not Reach's")


if __name__ == "__main__":
    asyncio.run(both_stop())
    asyncio.run(takeover())
    foreign_holder()
    print("KILL SWITCH CHECK PASSED")
