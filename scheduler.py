"""Core scheduling algorithms for the CPU Scheduling Simulator.

Lower numeric priority values represent higher priority. All algorithms are
non-preemptive except Round Robin, which uses the supplied time quantum.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Process:
    pid: str
    arrival: int
    burst: int
    priority: int = 0
    order: int = 0


@dataclass(frozen=True)
class Segment:
    pid: str
    start: int
    end: int


@dataclass(frozen=True)
class ProcessResult:
    pid: str
    arrival: int
    burst: int
    priority: int
    start: int
    completion: int
    waiting: int
    turnaround: int


@dataclass(frozen=True)
class ScheduleResult:
    algorithm: str
    rows: tuple[ProcessResult, ...]
    gantt: tuple[Segment, ...]
    average_waiting: float
    average_turnaround: float
    makespan: int


def _validate(processes: Iterable[Process]) -> list[Process]:
    items = list(processes)
    if not items:
        raise ValueError("Add at least one process before calculating.")
    ids = [p.pid.strip() for p in items]
    if any(not pid for pid in ids):
        raise ValueError("Process IDs cannot be empty.")
    if len(set(ids)) != len(ids):
        raise ValueError("Process IDs must be unique.")
    for p in items:
        if p.arrival < 0:
            raise ValueError(f"Arrival time for {p.pid} cannot be negative.")
        if p.burst <= 0:
            raise ValueError(f"Burst time for {p.pid} must be greater than zero.")
    return items


def _merge_segment(gantt: list[Segment], pid: str, start: int, end: int) -> None:
    if end <= start:
        return
    if gantt and gantt[-1].pid == pid and gantt[-1].end == start:
        previous = gantt[-1]
        gantt[-1] = Segment(pid, previous.start, end)
    else:
        gantt.append(Segment(pid, start, end))


def _assemble(algorithm: str, processes: list[Process], starts: dict[str, int],
              completions: dict[str, int], gantt: list[Segment]) -> ScheduleResult:
    rows: list[ProcessResult] = []
    for p in processes:
        completion = completions[p.pid]
        turnaround = completion - p.arrival
        waiting = turnaround - p.burst
        rows.append(ProcessResult(p.pid, p.arrival, p.burst, p.priority,
                                  starts[p.pid], completion, waiting, turnaround))
    rows.sort(key=lambda row: (row.completion, row.pid))
    count = len(rows)
    return ScheduleResult(
        algorithm=algorithm,
        rows=tuple(rows),
        gantt=tuple(gantt),
        average_waiting=sum(r.waiting for r in rows) / count,
        average_turnaround=sum(r.turnaround for r in rows) / count,
        makespan=max((segment.end for segment in gantt), default=0),
    )


def _non_preemptive(processes: list[Process], algorithm: str) -> ScheduleResult:
    remaining = set(p.pid for p in processes)
    by_id = {p.pid: p for p in processes}
    time = 0
    starts: dict[str, int] = {}
    completions: dict[str, int] = {}
    gantt: list[Segment] = []

    while remaining:
        ready = [by_id[pid] for pid in remaining if by_id[pid].arrival <= time]
        if not ready:
            next_time = min(by_id[pid].arrival for pid in remaining)
            _merge_segment(gantt, "IDLE", time, next_time)
            time = next_time
            ready = [by_id[pid] for pid in remaining if by_id[pid].arrival <= time]

        if algorithm == "FCFS":
            chosen = min(ready, key=lambda p: (p.arrival, p.order))
        elif algorithm == "SJF":
            chosen = min(ready, key=lambda p: (p.burst, p.arrival, p.order))
        elif algorithm == "LJF":
            chosen = min(ready, key=lambda p: (-p.burst, p.arrival, p.order))
        elif algorithm == "Priority":
            chosen = min(ready, key=lambda p: (p.priority, p.arrival, p.order))
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        starts[chosen.pid] = time
        end = time + chosen.burst
        _merge_segment(gantt, chosen.pid, time, end)
        time = end
        completions[chosen.pid] = time
        remaining.remove(chosen.pid)

    return _assemble(algorithm, processes, starts, completions, gantt)


def round_robin(processes: Iterable[Process], quantum: int) -> ScheduleResult:
    items = _validate(processes)
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than zero.")

    ordered = sorted(items, key=lambda p: (p.arrival, p.order))
    remaining = {p.pid: p.burst for p in items}
    by_id = {p.pid: p for p in items}
    starts: dict[str, int] = {}
    completions: dict[str, int] = {}
    gantt: list[Segment] = []
    queue: list[str] = []
    next_index = 0
    time = 0

    while len(completions) < len(items):
        while next_index < len(ordered) and ordered[next_index].arrival <= time:
            queue.append(ordered[next_index].pid)
            next_index += 1

        if not queue:
            next_time = ordered[next_index].arrival
            _merge_segment(gantt, "IDLE", time, next_time)
            time = next_time
            continue

        pid = queue.pop(0)
        process = by_id[pid]
        if pid not in starts:
            starts[pid] = time
        duration = min(quantum, remaining[pid])
        end = time + duration
        _merge_segment(gantt, pid, time, end)
        time = end
        remaining[pid] -= duration

        # Processes arriving during this slice join the queue before the
        # running process is returned to its tail.
        while next_index < len(ordered) and ordered[next_index].arrival <= time:
            queue.append(ordered[next_index].pid)
            next_index += 1

        if remaining[pid] > 0:
            queue.append(pid)
        else:
            completions[pid] = time

    return _assemble("Round Robin", items, starts, completions, gantt)


def schedule(processes: Iterable[Process], algorithm: str,
             quantum: int | None = None) -> ScheduleResult:
    """Run one supported algorithm and return process metrics plus Gantt data."""
    items = _validate(processes)
    name = algorithm.strip()
    if name == "Round Robin":
        if quantum is None:
            raise ValueError("Enter a time quantum for Round Robin.")
        return round_robin(items, quantum)
    if name not in {"FCFS", "SJF", "LJF", "Priority"}:
        raise ValueError("Choose FCFS, SJF, LJF, Priority, or Round Robin.")
    return _non_preemptive(items, name)
