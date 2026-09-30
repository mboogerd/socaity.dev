# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

"""Worker-session wrapper for the allocator spend log."""

from __future__ import annotations

import datetime as _datetime
from collections.abc import Callable
from typing import Any

from .spend_log import SpendLog, utc_timestamp


class Session:
    """Record one worker invocation when its context exits.

    The ``finally``-style exit behavior records failed sessions too: elapsed
    capacity is still spend, and the record has no success flag to keep the
    schema focused on the cap's wall-clock accounting unit.
    """

    def __init__(self, log: SpendLog, project: str, machine: str, work_item: str,
                 clock: Callable[[], _datetime.datetime] | None = None):
        self.log = log
        self.project = project
        self.machine = machine
        self.work_item = work_item
        self.clock = clock or (lambda: _datetime.datetime.now(_datetime.timezone.utc))
        self.started: str | None = None
        self.record: dict[str, Any] | None = None

    def __enter__(self) -> "Session":
        self.started = utc_timestamp(self.clock())
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool:
        if self.record is not None:
            raise RuntimeError("session wrapper exited more than once")
        assert self.started is not None
        self.record = self.log.append({
            "v": 1,
            "project": self.project,
            "machine": self.machine,
            "work_item": self.work_item,
            "started": self.started,
            "ended": utc_timestamp(self.clock()),
        })
        return False


def run_session(log: SpendLog, project: str, machine: str, work_item: str,
                worker: Callable[[], Any],
                clock: Callable[[], _datetime.datetime] | None = None) -> Any:
    """Run ``worker`` and append exactly one session record afterward."""

    with Session(log, project, machine, work_item, clock=clock):
        return worker()
