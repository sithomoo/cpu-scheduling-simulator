"""Run with: python -m unittest test_scheduler.py"""

import unittest

from scheduler import Process, schedule


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.processes = [
            Process("P1", 0, 5, 2, 0),
            Process("P2", 1, 3, 1, 1),
            Process("P3", 2, 8, 3, 2),
            Process("P4", 3, 6, 2, 3),
        ]

    def test_fcfs_metrics(self):
        result = schedule(self.processes, "FCFS")
        self.assertEqual([r.pid for r in result.rows], ["P1", "P2", "P3", "P4"])
        self.assertEqual(result.average_waiting, 5.75)
        self.assertEqual(result.average_turnaround, 11.25)

    def test_sjf_selects_shortest_ready_job(self):
        result = schedule(self.processes, "SJF")
        self.assertEqual([s.pid for s in result.gantt], ["P1", "P2", "P4", "P3"])

    def test_ljf_selects_longest_ready_job(self):
        result = schedule(self.processes, "LJF")
        self.assertEqual([s.pid for s in result.gantt], ["P1", "P3", "P4", "P2"])

    def test_priority_uses_smallest_number_as_highest(self):
        result = schedule(self.processes, "Priority")
        self.assertEqual([s.pid for s in result.gantt], ["P1", "P2", "P4", "P3"])

    def test_round_robin_and_gantt(self):
        result = schedule(self.processes, "Round Robin", quantum=2)
        self.assertEqual(result.makespan, 22)
        self.assertEqual(sum(r.burst for r in result.rows),
                         sum(s.end - s.start for s in result.gantt if s.pid != "IDLE"))
        self.assertTrue(all(r.waiting >= 0 for r in result.rows))

    def test_idle_period_is_shown(self):
        result = schedule([Process("P1", 3, 2)], "FCFS")
        self.assertEqual(result.gantt[0].pid, "IDLE")
        self.assertEqual((result.gantt[0].start, result.gantt[0].end), (0, 3))
        self.assertEqual(result.rows[0].waiting, 0)

    def test_invalid_quantum_is_rejected(self):
        with self.assertRaises(ValueError):
            schedule(self.processes, "Round Robin", quantum=0)

    def test_duplicate_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            schedule([Process("P1", 0, 2), Process("P1", 0, 3)], "FCFS")


if __name__ == "__main__":
    unittest.main()
